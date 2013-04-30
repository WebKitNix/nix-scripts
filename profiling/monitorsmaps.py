#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glib
import time
import shutil
import subprocess
from datetime import datetime
import calendar

'''
Starts and monitors WebKit2 applications, collecting
/proc/PID/smaps data from both UIProcess and WebProcess
every # seconds (right now it's 2). The directories
'ui-PID' and 'wp-PID' are created and populated with
copies of the smaps file in the format 'smaps-TIMESTAMP'.
The smaps may be further processed by the 'smapsdir2json.py'
and visualized with the d3 powered visualization page
'memoryview.html' in this same directory.
The visualization page requires the output of this script
to be put in a 'memory.json' file, and normal browsers will
require the page to be hosted in a webserver to accept loading
the json file. (But you may start google-chrome with the
--allow-file-access-from-files argument to avoid having the
webserver running.
'''

class WebKitMonitor(object):
    def __init__(self, uipid, wppid):
        self.uipid = uipid
        self.wppid = wppid
        self.uidir = 'ui-%d' % uipid
        self.wpdir = 'wp-%d' % wppid
        os.mkdir(self.uidir)
        os.mkdir(self.wpdir)

    def update(self):
        timestamp = calendar.timegm(datetime.now().utctimetuple())
        uiSrc = '/proc/%d/smaps' % self.uipid
        wpSrc = '/proc/%d/smaps' % self.wppid
        if not os.path.exists(uiSrc) or not os.path.exists(wpSrc):
            self.loop.quit()
            return
        shutil.copy(uiSrc, 'ui-%d/smaps-%d' % (self.uipid, timestamp))
        shutil.copy(wpSrc, 'wp-%d/smaps-%d' % (self.wppid, timestamp))
        glib.timeout_add_seconds(2, self.update)

    def run(self):
        self.loop = glib.MainLoop()
        self.update()
        self.loop.run()


def pidOfChildWebProcess(parentPid):

    def getParentPid(childPid):
        with open('/proc/%d/status' % childPid, 'r') as procStatus:
            for line in procStatus:
                if line.startswith('PPid'):
                    return int(line.split('\t')[-1].strip())

    pidof = subprocess.Popen(['pidof', 'WebProcess'], stdout=subprocess.PIPE)
    pidofOutput, _ = pidof.communicate()
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
    mon = WebKitMonitor(uiproc.pid, wppid)
    mon.run()
    print 'Monitoring has ended.'
    print 'Check the directories: "%s" and "%s"' % (mon.uidir, mon.wpdir)


if __name__ == '__main__':
    main()
