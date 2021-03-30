#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcaddon

class AddonRestart():


	def __init__(self):
		self.__addon__     = xbmcaddon.Addon(sys.argv[1])
		self.__addonid__   = self.__addon__.getAddonInfo('id')
		self.__addonname__ = self.__addon__.getAddonInfo('name')
		self.__addonver__ =  self.__addon__.getAddonInfo('version')
		if len(sys.argv)>2:
			self.service = sys.argv[2]
		else:
			self.service = None
		self.InitScript()

	def Stop(self):
		self.Log('Stopping addon via script')
		xbmc.executebuiltin("ActivateWindow(Home)")

	def Start(self):
		self.Log('restarting addon via script')
		xbmc.executebuiltin("RunAddon({})".format(self.__addonid__))

	def Service(self):
		self.Log('Running service script')
		xbmc.executebuiltin('RunScript({})'.format(self.service))

	def InitScript(self):
		self.Stop()
		if self.service:
			self.Service()
		self.Start()

	def Log(self,msg):
		if self.__addon__.getSettingBool('general.debug'):
			from inspect import getframeinfo, stack
			fileinfo = getframeinfo(stack()[1][0])
			xbmc.log('*__{}__{}*{} Python file name = {} Line Number = {}'.format(self.__addonname__,self.__addonver__,msg,fileinfo.filename,fileinfo.lineno),  level=xbmc.LOGINFO)
		else:pass




if __name__ == '__main__':
	AddonRestart()