#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glib
import shutil
import commands
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
        os.mkdir('ui-%d' % uipid)
        os.mkdir('wp-%d' % wppid)

    def update(self):
        timestamp = calendar.timegm(datetime.now().utctimetuple())
        src = '/proc/%d/smaps' % self.uipid
        dst = 'ui-%d/smaps-%d' % (self.uipid, timestamp)
        shutil.copy(src, dst)
        src = '/proc/%d/smaps' % self.wppid
        dst = 'wp-%d/smaps-%d' % (self.wppid, timestamp)
        shutil.copy(src, dst)
        glib.timeout_add_seconds(2, self.update)

    def run(self):
        self.loop = glib.MainLoop()
        self.update()
        self.loop.run()


def pidof(process):
    pid = commands.getoutput('pidof WebProcess')
    return int(pid) if pid else 0

def parentpid(child):
    with open('/proc/%d/status' % child, 'r') as f:
        for line in f:
            if line.startswith('PPid'):
                return int(line.split('\t')[-1].strip())

def main():
    ui = None
    wp = None
    seconds = 1
    if len(sys.argv) == 1:
        wp = pidof('WebProcess')
        if not wp:
            print 'There is no WebProcess running.'
            sys.exit(1)
    elif len(sys.argv) == 2:
        wp = int(sys.argv[2])

    if len(sys.argv) < 3:
        ui = parentpid(wp)
        if not ui:
            print 'There is no UIProcess running.'
            sys.exit(1)
    elif len(sys.argv) == 3:
        ui = int(sys.argv[1])
    else:
        print 'Usage: %s [WebProcessPID [UIProcessPID]]' % sys.argv[0]
        sys.exit(1)

    print 'Monitoring memory for UIProcess %d and WebProcess %d' % (ui, wp)
    mon = WebKitMonitor(ui, wp)
    mon.run()
    print 'Monitoring has ended.'


if __name__ == '__main__':
    main()

