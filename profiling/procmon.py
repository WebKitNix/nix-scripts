#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glib
import time
import commands
import subprocess
from datetime import datetime

'''
Starts and monitors WebKit2 applications, collecting
/proc/PID/status data from both UIProcess and WebProcess
every # seconds (right now it's 1), and outputs a couple
of CSV files.
'''

class WebKitMonitor(object):
    HEADINGS = 'Time,Peak,Size,Lck,Pin,HWM,RSS,Data,Stk,Exe,Lib,PTE,Swap,Threads'
    (
        UIPROCESS,
        WEBPROCESS
    ) = range(2)
    PROCESSES = ('UIProcess', 'WebProcess')
    MAXINTERVALSECONDS = 30
    MAXMONITORINGSECONDS = 360

    def __init__(self, uipid, wppid, seconds):
        self.startTime = None
        self.seconds = seconds
        self.pid = [0, 0]
        self.pid[WebKitMonitor.UIPROCESS] = uipid
        self.pid[WebKitMonitor.WEBPROCESS] = wppid
        self.init(WebKitMonitor.UIPROCESS)
        self.init(WebKitMonitor.WEBPROCESS)

    @staticmethod
    def csvFilename(process, pid):
        return '%s-%d.csv' % (WebKitMonitor.PROCESSES[process].lower(), pid)

    def init(self, process):
        filename = WebKitMonitor.csvFilename(process, self.pid[process])
        with open(filename, 'w') as f:
            f.write(WebKitMonitor.HEADINGS + '\n')

    def append(self, process, entry):
        filename = WebKitMonitor.csvFilename(process, self.pid[process])

        # Check previous entry to see if nothing changed.
        with open(filename, 'r') as f:
            lastEntry = f.readlines()[-1].strip().split(',')[1:]
            newEntry = entry.split(',')[1:]
            if lastEntry == newEntry:
                if self.seconds < WebKitMonitor.MAXINTERVALSECONDS:
                    self.seconds *= 2
                return

        with open(filename, 'a') as f:
            f.write(entry + '\n')

    def readEntry(self, process):
        with open('/proc/%d/status' % self.pid[process], 'r') as f:
            mem = [line for line in f.readlines() if line.startswith('Vm') or line.startswith('Threads')]
            data = [datetime.now().strftime('%H:%M:%S')]
            threads = mem.pop().split('\t')[-1].strip()
            for entry in mem:
                data.append([mem.strip() for mem in entry.split(' ')][-2])
            if len(data) == 1:
                return None
            data.append(threads)
            return ','.join(data)

    def update(self):
        def readPID(process):
            procdir = '/proc/%d' % self.pid[process]
            if not os.path.exists(procdir):
                print '%s with PID %d does not exist.' % (WebKitMonitor.PROCESSES[process], self.pid[process])
                return False
            entry = self.readEntry(process)
            if entry:
                self.append(process, entry)
            return True

        uiProc = readPID(WebKitMonitor.UIPROCESS)
        wpProc = readPID(WebKitMonitor.WEBPROCESS)

        delta = datetime.now() - self.startTime
        if delta.seconds > WebKitMonitor.MAXMONITORINGSECONDS or not uiProc or not wpProc:
            self.loop.quit()
        else:
            glib.timeout_add_seconds(self.seconds, self.update)

    def run(self):
        self.startTime = datetime.now()
        self.loop = glib.MainLoop()
        self.update()
        self.loop.run()


def pidOfChildWebProcess(parentPid):

    def getParentPid(childPid):
        with open('/proc/%d/status' % childPid, 'r') as procStatus:
            for line in procStatus:
                if line.startswith('PPid'):
                    return int(line.split('\t')[-1].strip())

    pidofOutput = commands.getoutput('pidof WebProcess')
    for pid in [int(pid) for pid in pidofOutput.split(' ') if pid]:
        if getParentPid(pid) == parentPid:
            return pid

    return None

def main():
    if len(sys.argv) == 1:
        print 'Usage: %s <webkit2-application> [application-arguments]' % sys.argv[0]
        sys.exit(1)

    try:
        uiproc = subprocess.Popen(sys.argv[1:])
    except OSError:
        print 'ERROR: could not locate application.'
        sys.exit(1)

    wppid = None

    for i in range(10):
        wppid = pidOfChildWebProcess(uiproc.pid)
        if wppid:
            break
        print 'WebProcess not found. Trying again.'
        time.sleep(1)

    if not wppid:
        print 'Could not find WebProcess. Aborting.'
        sys.exit(1)

    print 'Monitoring memory for UIProcess %d (%s) and WebProcess %d' % (uiproc.pid, sys.argv[1], wppid)
    mon = WebKitMonitor(uiproc.pid, wppid, 1)
    mon.run()
    print 'Monitoring has ended.'
    uiDataFile = WebKitMonitor.csvFilename(WebKitMonitor.UIPROCESS, uiproc.pid)
    wpDataFile = WebKitMonitor.csvFilename(WebKitMonitor.WEBPROCESS, wppid)
    print 'Check the files: "%s" and "%s"' % (uiDataFile, wpDataFile)

if __name__ == '__main__':
    main()
