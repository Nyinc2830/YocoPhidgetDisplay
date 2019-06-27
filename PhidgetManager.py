#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from ctypes import *
import threading
import time
from Queue import Queue

from Phidget22.PhidgetException import *
from Phidget22.Devices import *
from Phidget22.Devices.Manager import *
from Phidget22.Phidget import *

# ========== Event Handling Functions ==========

def AttachHandler(self, channel):

    attachedDevice = channel
    serialNumber = attachedDevice.getDeviceSerialNumber()
    deviceName = attachedDevice.getDeviceName()
    print("Hello to Device " + str(deviceName) + ", Serial Number: " + str(serialNumber))

def DetachHandler(self, channel):
    detachedDevice = channel
    serialNumber = detachedDevice.getDeviceSerialNumber()
    deviceName = detachedDevice.getDeviceName()
    print("Goodbye Device " + str(deviceName) + ", Serial Number: " + str(serialNumber))

# =========== Python-specific Exception Handler ==========        

def LocalErrorCatcher(e):
    print("Phidget Exception: " + str(e.code) + " - " + str(e.details) + ", Exiting...")
    return False

class PhidgetManager(object):
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
        try: manager = Manager()
        except RuntimeError as e:
            print("Runtime Error " + e.details)
            return False

        try:
            manager.setOnAttachHandler(AttachHandler)
            manager.setOnDetachHandler(DetachHandler)
        except PhidgetException as e: return LocalErrorCatcher(e)

        try:
            manager.open()
        except PhidgetException as e: return LocalErrorCatcher(e)

        """ Method that runs forever """
        while True:
            # Do something
            print('Doing something imporant in the background (phiget)')


            time.sleep(self.interval)

        try:
            manager.close()
        except PhidgetException as e: return LocalErrorCatcher(e)

