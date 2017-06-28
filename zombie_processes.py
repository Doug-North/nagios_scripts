#!/usr/bin/python

import json
import platform
import subprocess
import os
import sys

#if any impacting changes to this plugin kindly increment the plugin version here.
PLUGIN_VERSION = "1"

#Setting this to true will alert you when there is a communication problem while posting plugin data to server
HEARTBEAT="true"

TOPCOMMAND='top', '-b', '-n', '1'

def os_exit(code):
    sys.stdout.flush()
    try:
        sys.exit(code)
    except SystemExit as e:
        os._exit(code)

def zombie_watch():
    data = {}
    data['plugin_version'] = PLUGIN_VERSION
    data['heartbeat_required']=HEARTBEAT

    try:
        proc = subprocess.Popen(TOPCOMMAND,stdout=subprocess.PIPE,close_fds=True)
        top_output = proc.communicate()[0]
#        print(top_output)
        for line in top_output.split('\n'):
            if not line:
                continue
            if line.startswith('Tasks') and line.endswith('zombie'):
                try:
                    zombies_raw = line.split(',')[-1]
                    if 'zombie' in zombies_raw:
                        data['zombies'] = zombies_raw.split()[0]
                        break
                except Exception as exception:
                    data['status']=0
                    data['msg']='error while parsing top output'

    except Exception as exception:
        data['status']=0
        data['msg']='error while executing top command'

    zombie_num = int(data['zombies'])
#    print(zombie_num)
    if zombie_num < 10:
        print("OK : No Zombies found")
        os_exit(0)
    elif zombie_num >= 10 and zombie_num <= 50:
        print("WARNING : {} zombies found, potential indication of a bug".format(zombie_num))
        os_exit(1)
    elif zombie_num > 50:
        print("CRITICAL : {} zombies found, kill of redundant processes".format(zombie_num))
        os_exit(2)
    else:
        print("UNKNOWN : could not parse JSON data")
        os_exit(3)



if __name__ == '__main__':
    zombie_watch()