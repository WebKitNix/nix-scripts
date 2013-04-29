#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json

'''
Parses data from directory containing /proc/PID/smaps files
of a single process, collected through time. All the files
in the directory *must* follow the format "smaps-TIMESTAMP".
Use the script 'smapscollector.py' to generate these.
'''

def parseValues(filename):
    data = open(filename, 'r').readlines()
    entries = {}
    previousItem = None

    for i in range(0, len(data), 15):
        item = data[i].split(' ')[-1].strip()
        if item.startswith('[stack'):
            item = '[stack]'
        elif not item:
            item = previousItem

        if not item in entries:
            entries[item] = { 'size' : [], 'rss' : [], 'pss' : [] }

        getData = lambda j: int(data[i+j].split(' ')[-2])

        entries[item]['size'].append(getData(1))
        entries[item]['rss'].append(getData(2))
        entries[item]['pss'].append(getData(3))

        previousItem = item

    return entries


def main():
    if len(sys.argv) != 2:
        print 'Usage: %s directory' % sys.argv[0]
        sys.exit(1)

    directory = sys.argv[1]

    if not os.path.exists(directory) or not os.path.isdir(directory):
        print 'Directory %s does not exist or it is not a directory.' % sys.argv[1]
        sys.exit(1)

    data = {}
    files = sorted(os.listdir(directory))
    initialTime = int(files[0].split('-')[-1])
    finalTime = int(files[-1].split('-')[-1])
    timestamps = []
    for i, df in enumerate(files):
        timestamp = int(df.split('-')[-1]) - initialTime
        timestamps.append(timestamp)
        entries = parseValues(os.path.join(directory, df))
        sections = entries.keys()
        results = ''
        for fullName in sections:
            if not fullName in data:
                name = fullName.split('/')[-1]
                data[fullName] = { 'name' : name, 'size' : [], 'rss' : [], 'pss' : [] }
            data[fullName]['size'].append(sum(entries[fullName]['size']))
            data[fullName]['rss'].append(sum(entries[fullName]['rss']))
            data[fullName]['pss'].append(sum(entries[fullName]['pss']))
    sections = {}
    for key, value in data.items():
        section = 'other'
        if key.startswith('[stack'):
            section = 'stack'
        elif key.startswith('[heap'):
            section = 'heap'
        elif '/lib' in key and '.so' in key:
            section = 'libraries'
        elif key.startswith('(deleted'):
            section = 'deleted'
        elif key.endswith('.ttf') or 'cache/fontconfig/' in key:
            section = 'fonts'
        elif '.cache' in key or '/MANIFEST' in key:
            section = 'cache'
        elif '/WebProcess' in key:
            section = 'Binary'
        elif key == '':
            value['name'] = '?'
            section = 'nameless'
        if not section in sections:
            sections[section] = []
        sections[section].append(value)

    final = { 'timestamps' : timestamps, 'name' : 'global', 'children' : [] }
    for section in sorted(sections.keys()):
        final['children'].append({ 'name' : section, 'children' : sections[section]})
    print json.dumps(final)

if __name__ == '__main__':
    main()

