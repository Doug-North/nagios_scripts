#!/usr/bin/env python

"""
Since this is a nagios test, we'll return different sys_exit codes
correspoding to these states:
0) OK - plain sailing
1) WARNING - we are surpassing some threshold for the service check
2) CRITICAL - inbox count is too high, implying auto-purging has stop
3) UNKNOWN - script errors, invalid data, etc

Comment:
- you have to use os_exit(code) to exit the process with calling cleanup
 handlers, flushing stdio buffers, etc. Otherwise print messages might not
 appear.
- you have to silence stdout while performing sql operations in order not
 to show messages from the client
 
 script by Douglas North
 
"""

#import ConfigParser
import datetime
import httplib2
import imaplib
import os
import requests
import sys

# Load the configuration file
#with open("/etc/nagios/gluster/gluster-contacts.cfg ") as f:
#    config = f.read()
#print(config)

#mail details
try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    mail.login('EMAIL-HERE', 'PASSWORD') # must be defined
    mail.select("inbox") # connect to inbox
except:
    print("UNKNOWN : Failure to gain access to account")
    sys.exit(0)
    
def os_exit(code):
    sys.stdout.flush()
    try:
        sys.exit(code)
    except SystemExit as e:
        os._exit(code)

def get_old_email_count():
    date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%b-%Y")
    result, data = mail.uid('search', None, '(SENTBEFORE {})'.format(date))
    count = len(data[0].split(" "))-1 # data is formatted as a list of one string hence [0]
    return count

def slack_post():
    url = 'https://hooks.slack.com/services/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'
    payload={"text": "CRITICAL : Found emails older than 24 hours, check Auto-purge"}
    r = requests.post(url, json=payload)
    print(r)

def auto_message():
    count = get_old_email_count()
    ok_msg = 'OK : Number in inbox is {}'.format(count)
    warning_msg = 'WARNING : Found {} emails older than 24 hours, worth checking'.format(count)
    critical_msg = 'CRITICAL : Found {} emails older than 24 hours, check Auto-purge'.format(count)
    unknown_msg = 'UNKNOWN : Could not report on number of emails'
    
    if count == 0:
        print(ok_msg)
        os_exit(0)
    elif count <= 1000:
        print(warning_msg)
        os_exit(1)
    elif count >= 1000: 
        print(critical_msg)
        slack_post()
        os_exit(2)
    else: 
        print(unknown_msg)
        os_exit(3)
        
if __name__ == '__main__':
    auto_message()
