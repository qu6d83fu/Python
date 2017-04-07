#!/usr/bin/python
# -*- coding:utf-8 -*-

from threading import *
import time

class itemX:
    def __init__(self):
        self.cnt = 0

    def produce(self, num=1):
        self.cnt += 1

    def consume(self, num=1):
        if self.cnt:
            self.cnt -= 1
        else:
            print 'WARNING***********************WARNING'

    def isEmpty(self):
        return not self.cnt

    def getCount(self):
        return self.cnt

class Producer(Thread):
    def __init__(self, condition, event, item, sleeptime=1):
        Thread.__init__(self)
        self.con = condition
        self.event = event
        self.item = item
        self.sleeptime = sleeptime

    def run(self):
        while (True):
            time.sleep(self.sleeptime)
            self.con.acquire()
            self.item.produce()
            print 'produce 1 product, remain({0})\r\n'.format(self.item.getCount())
            self.event.set()
            self.con.release()

class Consumer(Thread):
    def __init__(self, condition, event, item, sleeptime=1):
        Thread.__init__(self)
        self.con = condition
        self.event = event
        self.item = item
        self.sleeptime = sleeptime
    def run(self):
        while (True):
            time.sleep(self.sleeptime)
            self.con.acquire()
            print '({0})enter\r\n'.format(self.getName())
            #while self.item.isEmpty():
            while (True):
                print '({0})wait'.format(self.getName())
                self.event.wait()
                break
            self.item.consume()
            self.event.clear()
            print '({0})consume 1 product, remain({1})\r\n'.format(self.getName(), self.item.getCount())
            self.con.release()


if __name__ == "__main__":
    X = itemX()
    cond_Con = Condition()
    cond_Pro = Condition()
    event = Event()
    Producer(cond_Pro, event, X).start()
    Consumer(cond_Con, event, X).start()
    Consumer(cond_Con, event, X).start()

    while (True):
        pass 
