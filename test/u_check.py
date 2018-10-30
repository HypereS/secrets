# !/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import sys
sys.path.append("..")
import codecs
import time
import logging
from watchdog.observers import Observer
from watchdog.events import *

from Adaptors.log2File import Assert
from Adaptors.switchtab import *

#check 360devmdriver is running or not
def devmCheck():
	info = os.popen("sc query 360devm")
	if info:
		str = info.read()
		index = re.search(r'RUNNING',str)
		if index:
			log2File("360devm is RUNNING..")
			#print "360devm is RUNNING.."
			return 0
		else:
			log2File("360devm is not RUNNING..")
			#print "360devm is not RUNNING.."
			return 1
	else:
		log2File("Open Service failed")
		#print "Open Service failed"
		return -1

# analysys latest log record	
def uLogAnalysis():
	strlogentdev = r'latestlog.log'
	try:
		fo = codecs.open (strlogentdev, 'rb', 'utf-16')
		#fi = codecs.open("111.txt", "wb", 'utf-16')
		listall = []
		for line in fo.readlines():
			 if(-1 != line.rfind(u"|enabled|")):
				listall.append(line)
			 if(-1 != line.rfind(u"|disabled|")):
				listall.append(line)
		if 0 == len(listall):
			#print "No USB startagy distribute.."
			Assert("No USB startagy distribute..", "Fail")
			return
		listall.sort()
		latest = listall
		# str_drive_path = u"DISK&VEN_HP&PROD_V220W&REV_1100"  					#惠普U盘
		# str_mass_path = u"VID_03F0&PID_5A07"
		str_device_id = ""
		str_drive_path = u"DISK&VEN_KINGSTON&PROD_DATATRAVELER_3.0&REV_PMAP"	#金士顿U盘
		str_mass_path = u"VID_0951&PID_1666"
		count = 0
		for index in latest:
			if -1 != index.find(str_mass_path):
				count +=1
		if count == 0:
			Assert("No USB Stratagy Found..", "Fail")
			#print "No USB Stratagy distribute|No USB Device Found"
			return
		log2File("'Find USB Device: %s'" % (str_drive_path))
		#print "Find USB Device: %s" % (str_drive_path)
		count_disable = 0
		count_enable = 0
		for index in latest:
			if -1 != index.rfind("|disabled|") and (-1 != index.find(str_mass_path) or -1 != index.find(str_drive_path)):
				count_disable += 1
				Assert("Current USB Device is Disabled..", "Pass")
				#print "Current USB Device is Disabled.."
				return
			elif -1 != index.rfind("|enabled|") and (-1 != index.find(str_mass_path) or -1 != index.find(str_drive_path)):
				count_enable += 1
		if count_disable == 0 and count_enable == 0:
			Assert("USB Device Exception..", "Fail")
			#print "USB Device Exception.."
			return
		Assert("Current USB Device is Enabled..", "Pass")
		#print "Current USB Device is Enabled.."
		#fi.close()
		fo.close()
	except:
		# import traceback
		# print traceback.format_exc()
		log2File("file error: file random code caused!")
		#print "file error: file random code caused!"


class myFileHandler(FileSystemEventHandler):
    def __init__(self, pos):
        FileSystemEventHandler.__init__(self)
        self.pos = pos
    def on_modified(self, event):
        if event.is_directory:
            # print "directory modified:{}".format(event.src_path)
            pass
        elif event.src_path == r"C:\ProgramData\360Skylar6\EntDEVMgr.ext.log":
            print "file modified:{}".format(event.src_path)
            #path = os.path.realpath(event.src_path)
            foObsvr = codecs.open(event.src_path, 'r', 'utf-16')
            fiObsvr = codecs.open("latestlog.log", 'w', 'utf-16')
            # foObsvr.seek(self.pos, 0)
            log_new = foObsvr.read()
            str = log_new[self.pos/2:]
            fiObsvr.write(str)
            self.pos = foObsvr.tell()
            fiObsvr.close()
            foObsvr.close()
            uLogAnalysis()
        else:
            #print "other file modified!"
            pass

if __name__ == "__main__":
    if 0 == devmCheck():
	    path = r"C:\ProgramData\360Skylar6"
	    fo = codecs.open(r"C:\ProgramData\360Skylar6\EntDEVMgr.ext.log", 'r', 'utf-16')
	    list_str = fo.read()
	    pos_end = fo.tell()
	    fo.close()
	    obsvr = Observer()
	    event_handler = myFileHandler(pos_end)
	    obsvr.schedule(event_handler, path, recursive=True)
	    obsvr.start()
	    try:
	        while True:
	            time.sleep(1)
	    except KeyboardInterrupt:
	        obsvr.stop()
	    obsvr.join()








