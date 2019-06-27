#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys
import signal
from DeviceManager import *
# from DisplayManager import *
from yoctopuce.yocto_display import *

from Queue import Queue

queue = Queue(10)

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

def handler(signum, frame):
    print('Signal handler called with signal', signum)
    raise ServiceExit

def drawText(layer, x, y, text):
    layer.drawText(x, y, YDisplayLayer.ALIGN.CENTER, text)

def main():

    signal.signal(signal.SIGABRT, handler)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    print('Starting main program')

    try:


        errmsg = YRefParam()

        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            print("init error" + errmsg.value)
            raise ServiceExit

        disp = YDisplay.FirstDisplay()
        if disp is None:
            print('No module connected')
            raise ServiceExit

        if not disp.isOnline():
            print("Module not connected ")
            raise ServiceExit

        # display clean up
        disp.resetAll()

        l0 = disp.get_displayLayer(0)

        l1 = disp.get_displayLayer(1)
        l2 = disp.get_displayLayer(2)
        l1.hide()  # L1 is hidden, l2 stays visible
        centerX = disp.get_displayWidth() / 2
        centerY = disp.get_displayHeight() / 2
        radius = disp.get_displayHeight() / 2
        a = 0

        x = 0

        y = DeviceManager(queue)
        # d = DisplayManager(queue)

        y.start()
        # d.start()

        while True:
            # we draw in the hidden layer
            l1.clear()

            l1.selectFont("Large.yfm")
            drawText(l1, x, centerY, "Work")
            x += 1
            if x > disp.get_layerWidth() + (disp.get_layerWidth() / 2):
                x = -(disp.get_layerWidth() / 2)

            disp.swapLayerContent(1, 2)

            # Do something
            print('Doing something imporant in the background (main)')

            num = queue.get()
            queue.task_done()
            print("Consumed", num)

            time.sleep(0.5)
    except ServiceExit:
        y.shutdown_flag.set()
        # d.shutdown_flag.set()

        y.join()
        # d.join()

    print("Exiting the main program")

if __name__ == '__main__':
    main()


