#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import threading
import time
from Queue import Queue
import random

###############################################################################
# Phidgets ####################################################################
###############################################################################

from Phidget22.PhidgetException import *
from Phidget22.Devices import *
from Phidget22.Devices.Manager import *
from Phidget22.Phidget import *

# ========== Event Handling Functions ==========

def phidgetDeviceArrival(self, channel):

    attachedDevice = channel
    serialNumber = attachedDevice.getDeviceSerialNumber()
    deviceName = attachedDevice.getDeviceName()
    print("Hello to Device " + str(deviceName) + ", Serial Number: " + str(serialNumber))

def phidgetDeviceRemoval(self, channel):
    detachedDevice = channel
    serialNumber = detachedDevice.getDeviceSerialNumber()
    deviceName = detachedDevice.getDeviceName()
    print("Goodbye Device " + str(deviceName) + ", Serial Number: " + str(serialNumber))

# =========== Python-specific Exception Handler ==========        

def LocalErrorCatcher(e):
    print("Phidget Exception: " + str(e.code) + " - " + str(e.details) + ", Exiting...")
    return False

###############################################################################
# Yoctopuce ####################################################################
###############################################################################

from yoctopuce.yocto_api import *
from yoctopuce.yocto_anbutton import *

def functionValueChangeCallback(fct, value):
    info = fct.get_userData()
    print(info['hwId'] + ": " + value + " " + info['unit'] + " (new value)")


def sensorTimedReportCallback(fct, measure):
    info = fct.get_userData()
    print(info['hwId'] + ": " + str(measure.get_averageValue()) + " " + info['unit'] + " (timed report)")


def configChangeCallback(mod):
    print(mod.get_serialNumber() + ": configuration change")

def beaconCallback(mod, beacon):
    print("%s: beacon changed to %d" % (mod.get_serialNumber(), beacon))

def yoctoDeviceArrival(m):
    serial = m.get_serialNumber()
    print('YoctoDevice arrival : ' + serial)
    m.registerConfigChangeCallback(configChangeCallback)
    m.registerBeaconCallback(beaconCallback)

    # First solution: look for a specific type of function (eg. anButton)
    fctcount = m.functionCount()
    for i in range(fctcount):
        hardwareId = serial + '.' + m.functionId(i)
        if hardwareId.find('.anButton') >= 0:
            print('- ' + hardwareId)
            bt = YAnButton.FindAnButton(hardwareId)
            bt.set_userData({'hwId': hardwareId, 'unit': ''})
            bt.registerValueCallback(functionValueChangeCallback)

    # Alternate solution: register any kind of sensor on the device
    sensor = YSensor.FirstSensor()
    while sensor:
        if sensor.get_module().get_serialNumber() == serial:
            hardwareId = sensor.get_hardwareId()
            print('- ' + hardwareId)
            sensor.set_userData({'hwId': hardwareId, 'unit': sensor.get_unit()})
            sensor.registerValueCallback(functionValueChangeCallback)
            sensor.registerTimedReportCallback(sensorTimedReportCallback)
            sensor = sensor.nextSensor()

def yoctoDeviceRemoval(m):
    print('YoctoDevice removal : ' + m.get_serialNumber())

###############################################################################

def startYocto():
    errmsg = YRefParam()

    # No exception please
    YAPI.DisableExceptions()

    # Setup the API to use local USB devices
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        print("init error" + errmsg.value)
        return None

    YAPI.RegisterDeviceArrivalCallback(yoctoDeviceArrival)
    YAPI.RegisterDeviceRemovalCallback(yoctoDeviceRemoval)

    return errmsg

def startPhidgets():
    try: manager = Manager()
    except RuntimeError as e:
        print("Runtime Error " + e.details)
        return False

    try:
        manager.setOnAttachHandler(phidgetDeviceArrival)
        manager.setOnDetachHandler(phidgetDeviceRemoval)
    except PhidgetException as e: return LocalErrorCatcher(e)

    try:
        manager.open()
    except PhidgetException as e: return LocalErrorCatcher(e)
    return manager

###############################################################################

class DeviceManager(threading.Thread):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, queue, interval=500):
        threading.Thread.__init__(self)

        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.queue = queue
        self.interval = interval

        self.shutdown_flag = threading.Event()

        # self.thread = threading.Thread(target=self.run, args=())
        # self.thread.daemon = True                            # Daemonize thread
        # self.thread.start()                                  # Start the execution

    def run(self):
        errmsg = startYocto()
        manager = startPhidgets()

        if errmsg != None and manager != None:

            print('Hit Ctrl-C to Stop ')

            nums = range(5)

            print('Thread #%s started' % self.ident)

            """ Method that runs forever """
            while not self.shutdown_flag.is_set():

                # Do something
                print('Doing something imporant in the background (device)')

                YAPI.UpdateDeviceList(errmsg)  # traps plug/unplug events

                num = random.choice(nums)
                self.queue.put(num)
                print("Produced", num)

                YAPI.Sleep(self.interval, errmsg)  # traps others events
                # time.sleep(self.interval)

            print('Thread #%s stopped' % self.ident)

            YAPI.FreeAPI()

            try:
                manager.close()
            except PhidgetException as e: return LocalErrorCatcher(e)
