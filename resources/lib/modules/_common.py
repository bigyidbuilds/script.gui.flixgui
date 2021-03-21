#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import xbmc
import xbmcaddon
from datetime import date,datetime,timedelta
from dateutil import parser as dparser
from ._addon import *


def DateTimeObject(date_str,df=False):
	DTO = dparser.parse(date_str,dayfirst=df)
	return DTO

def DateTimeNow():
	DTN = datetime.now()
	return DTN

def DateTimeStrf(dateString,fmt='%Y-%m-%d'):
	DTS = dateString.strftime(fmt)
	return DTS

def DateTimeStrp(dateString,fmt):
	try:
		DTS = datetime.strptime(dateString, fmt)
	except TypeError:
		DTS = datetime.fromtimestamp(time.mktime(time.strptime(dateString,fmt)))
	return DTS

def FromTimeStamp(dt_stamp,fmt=''):
	stamp = datetime.fromtimestamp(float(dt_stamp))
	if fmt == '':
		return stamp
	else:
		strstamp = stamp.strftime(fmt)
		return strstamp

def Log(msg):
	# if xbmcaddon.Addon(CALLER.caller.callerAddon).getSettingBool('general.debug'):
	from inspect import getframeinfo, stack
	fileinfo = getframeinfo(stack()[1][0])
	xbmc.log('*__{}__{}*{} Python file name = {} Line Number = {}'.format(script_name,script_version,msg,fileinfo.filename,fileinfo.lineno), level=xbmc.LOGINFO)
	# else:pass


def Sleep(sec):
	time.sleep(sec)


def ToTimeStamp(dt):
	ts = time.mktime(dt.timetuple())
	return ts
