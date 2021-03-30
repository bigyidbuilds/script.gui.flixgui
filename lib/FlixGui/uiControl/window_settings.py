#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''
import xml.etree.ElementTree as ET
import os
'''#####-----Internal Modules-----#####'''
from ._actions import *
from FlixGui.modules._common import Log




class WindowSettings(xbmcgui.WindowXML):

	SETTINGSLIST = 3000
	TOOLSLIST    = 3100
	INFOLIST     = 3200

	xmlFilename = 'Window_Settings.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'

	def __new__(cls,dbconn,*args,**kwargs):
		return super(WindowSettings, cls).__new__(cls,WindowSettings.xmlFilename, WindowSettings.scriptPath, WindowSettings.defaultSkin, WindowSettings.defaultRes)
		

	def __init__(self,dbconn,*args,**kwargs):
		super(WindowSettings,self).__init__()
		self.dbconn = dbconn
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT * FROM temp.caller")
			r=c.fetchone()
			self.addon_id = r['addon_id']
		self.addons_with_settings = self.GetModulesWithSettings()

	def onInit(self):
		self.getControl(self.SETTINGSLIST).addItems(self.addons_with_settings)
		self.getControl(self.TOOLSLIST).addItems(self.ToolsMenu())

	def onAction(self,action):
		actionId = action.getId()
		focusId =  self.getFocusId()
		Log('onAction: {}'.format(actionId))
		if actionId in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif actionId in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if focusId == self.SETTINGSLIST:
				self.OpenSettings(self.getControl(focusId).getSelectedItem())
			elif focusId == self.TOOLSLIST:
				eval(self.getControl(focusId).getSelectedItem().getProperty('func'))

	def onClick(self,controlId):
		'''
		onClick method.

					This method will receive all click events that the main program will send to this window.

		Parameters
					self	Own base class pointer
		controlId	The one time clicked GUI control identifier
		Example:
				# Define own function where becomes called from Kodi
				def onClick(self,controlId):
					if controlId == 10:
						print("The control with Id 10 is clicked")
		'''

	def onControl(self,control):
		'''
		Function: onControl(self, Control)
				onControl method.

		This method will receive all click events on owned and selected controls when the control itself doesn't handle the message.

		Parameters
			self	Own base class pointer
			control	The Control class
		Example:
			# Define own function where becomes called from Kodi
			def onControl(self, control):
				print("Window.onControl(control=[%s])"%control)
		'''

	def onDoubleClick(self,controlId):
		'''
		Function: onDoubleClick(self, int controlId)
				onDoubleClick method.

		This method will receive all double click events that the main program will send to this window.

		Parameters
				self	Own base class pointer
				controlId	The double clicked GUI control identifier
		Example:
				# Define own function where becomes called from Kodi
				def onDoubleClick(self,controlId):
				  if controlId == 10:
					print("The control with Id 10 is double clicked")
		'''

	def onFocus(self,controlId):
		'''
		Function: onFocus(self, int controlId)
				onFocus method.

		This method will receive all focus events that the main program will send to this window.

		Parameters
			self	Own base class pointer
			controlId	The focused GUI control identifier
		Example:
		# Define own function where becomes called from Kodi
		def onDoubleClick(self,controlId):
		   if controlId == 10:
		   print("The control with Id 10 is focused")
		'''

	def Close(self):
		super(WindowSettings,self).close()
		'''
		Function: close()
			Closes this window.

		Closes this window by activating the old window.

		Note
			The window is not deleted with this method. 
		'''
	def OpenSettings(self,listitem):
		xbmcaddon.Addon(listitem.getProperty('addon_id')).openSettings()


	def GetModulesWithSettings(self):
		ignore = ['script.module.inputstreamhelper','script.module.python.twitch','plugin.googledrive']
		items = []
		withsettings = []
		startpath = os.path.join(xbmcvfs.translatePath(xbmcaddon.Addon(self.addon_id).getAddonInfo('path')),'addon.xml')
		items +=(self.AddonDep(self.addon_id))
		for i in items:
			if i and i not in ignore:
				items += self.AddonDep(i)
		addons = list(set(items))
		addons.append(self.addon_id)
		for a in addons:
			if a and a not in ignore and xbmcvfs.exists(os.path.join(xbmcvfs.translatePath(xbmcaddon.Addon(a).getAddonInfo('path')),'resources','settings.xml')):
				li = xbmcgui.ListItem(xbmcaddon.Addon(a).getAddonInfo('name'))
				li.setArt({'thumb':xbmcaddon.Addon(a).getAddonInfo('icon')})
				li.setProperty('addon_id',a)
				withsettings.append(li)
		return withsettings


	def AddonDep(self,addon_id):
		xmlpath = os.path.join(xbmcvfs.translatePath(xbmcaddon.Addon(addon_id).getAddonInfo('path')),'addon.xml')
		if xbmcvfs.exists(xmlpath):
			tree = ET.parse(xmlpath)
			root = tree.getroot()
			return [addon.get('addon') for addon in root.find('requires')]


	def ClearDBTable(self,table):
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("DELETE FROM {}".format(table))
			self.dbconn.conn.commit()
		self.AddonRestart()

	def DeleteNullRow(self,table):
		columns = []
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT * FROM {}".format(table))
			row = c.fetchone()
			if row:
				columns = row.keys()
				for column in columns:
					c.execute("DELETE FROM {} WHERE {} IS NULL".format(table,column))
			self.dbconn.conn.commit()
		self.AddonRestart()


	def DumpDB(self):
		self.dbconn.conn.close()
		deleted = xbmcvfs.delete(self.DBPath('script.gui.flixgui'))
		if deleted:
			self.AddonRestart(service=os.path.join(self.scriptPath,'scripts','database.py'))

	def Dump_DB(self):
		self.dbconn.conn.close()
		deleted = xbmcvfs.delete(self.DBPath(self.addon_id))
		if deleted:
			self.AddonRestart()

	def DBPath(self,addonID):
		return os.path.join(xbmcvfs.translatePath('special://database'),'{}.db'.format(xbmcaddon.Addon(addonID).getAddonInfo('id')))


	def ToolsMenu(self):
		items=[
			{'title':'Clear Contents of TMDB Movie detail cache','func':'self.ClearDBTable("master.tmdb_movie_details")'},
			{'title':'Clear Contents of TMDB TV detail cache','func':'self.ClearDBTable("master.tmdb_tv_details")'},
			{'title':'Clear Contents of TMDB Tv Episode detail cache','func':'self.ClearDBTable("master.tmdb_episode_details")'},
			{'title':'Remove items with missing information from TMDB Movie detail cache','func':'self.DeleteNullRow("master.tmdb_movie_details")'},
			{'title':'Remove items with missing information from TMDB Tv detail cache','func':'self.DeleteNullRow("master.tmdb_tv_details")'},
			{'title':'Remove items with missing information from TMDB Tv Episode detail cache','func':'self.DeleteNullRow("master.tmdb_episode_details")'},
			{'title':'Delete All of TMDB Cache inc DataBase','func':'self.DumpDB()'},
			{'title':'Clear Contents of MyList and Rating list','func':'self.ClearDBTable("user_list")'},
			{'title':'Clear Contents of Watched Movies','func':'self.ClearDBTable("user_watched_movie")'},
			{'title':'Clear Contents of Watched TV','func':'self.ClearDBTable("user_watched_tv")'},
			{'title':'Clear Contents of {} Movie list'.format(xbmcaddon.Addon(self.addon_id).getAddonInfo('name')),'func':'self.ClearDBTable("movie_list")'},
			{'title':'Clear Contents of {} TV list'.format(xbmcaddon.Addon(self.addon_id).getAddonInfo('name')),'func':'self.ClearDBTable("tv_list")'},
			{'title':'Delete All {} Cache Inc DataBase'.format(xbmcaddon.Addon(self.addon_id).getAddonInfo('name')),'func':'self.Dump_DB()'}
			]
		litems =[]
		for i in items:
			li=xbmcgui.ListItem(i.get('title'))
			li.setProperty('func',i.get('func'))
			litems.append(li)
		return litems


	def AddonRestart(self,service=None):
		from . import dialog_response
		res = dialog_response.DialogResponse("Addon requires restarting","OK",posy=100)
		if res.index == 0:
			path = os.path.join(self.scriptPath,'scripts','addon_restart.py')
			if service:
				xbmc.executebuiltin('RunScript({},{},{})'.format(path,self.addon_id,service))
			else:
				xbmc.executebuiltin('RunScript({},{})'.format(path,self.addon_id))
					

