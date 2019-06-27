#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import math
import threading
import time
from Queue import Queue

from yoctopuce.yocto_api import *
from yoctopuce.yocto_display import *

def drawText(layer, x, y, text):
    layer.drawText(x, y, YDisplayLayer.ALIGN.CENTER, text)

class DisplayManager(threading.Thread):
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
        errmsg = YRefParam()

        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            print("init error" + errmsg.value)
            return

        disp = YDisplay.FirstDisplay()
        if disp is None:
            print('No module connected')
            return

        if not disp.isOnline():
            print("Module not connected ")
            return

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

        # print('Hit Ctrl-C to Stop ')
        print('Thread #%s started' % self.ident)

        """ Method that runs forever """
        while not self.shutdown_flag.is_set():
            # we draw in the hidden layer
            l1.clear()

            l1.selectFont("Large.yfm")
            drawText(l1, x, centerY, "Work")
            x += 1
            if x > disp.get_layerWidth() + (disp.get_layerWidth() / 2):
                x = -(disp.get_layerWidth() / 2)

            disp.swapLayerContent(1, 2)

            # Do something
            print('Doing something imporant in the background (display)')

            num = self.queue.get()
            self.queue.task_done()
            print("Consumed", num)

            time.sleep(self.interval)

        print('Thread #%s stopped' % self.ident)


