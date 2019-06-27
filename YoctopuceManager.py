#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import threading
import time
from Queue import Queue

from yoctopuce.yocto_api import *

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

def deviceArrival(m):
    serial = m.get_serialNumber()
    print('Device arrival : ' + serial)
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

def deviceRemoval(m):
    print('Device removal : ' + m.get_serialNumber())

class YoctopuceManager(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, queue, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.queue = queue
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        errmsg = YRefParam()

        # No exception please
        YAPI.DisableExceptions()

        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            sys.exit("init error" + errmsg.value)

        YAPI.RegisterDeviceArrivalCallback(deviceArrival)
        YAPI.RegisterDeviceRemovalCallback(deviceRemoval)

        print('Hit Ctrl-C to Stop ')

        """ Method that runs forever """
        while True:
            # Do something
            print('Doing something imporant in the background (yoctopuce)')


            time.sleep(self.interval)

