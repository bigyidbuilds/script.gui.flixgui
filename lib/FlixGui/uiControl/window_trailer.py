# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
'''######------External Modules-----#####'''
import imp
import youtube_resolver

'''#####-----Internal Modules-----#####'''
from ._actions import *
from FlixGui.modules._common import Log




class WindowTrailer(xbmcgui.WindowXML):

	FANARTIMAGE = 1000
	TRAILERLIST = 3000

	xmlFilename = 'Window_Trailer.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'

	def __new__(cls,dbconn,fanart,traileritems,*args,**kwargs):
		return super(WindowTrailer, cls).__new__(cls,WindowTrailer.xmlFilename, WindowTrailer.scriptPath, WindowTrailer.defaultSkin, WindowTrailer.defaultRes)
		

	def __init__(self,dbconn,fanart,traileritems,*args,**kwargs):
		super(WindowTrailer,self).__init__()
		self.dbconn = dbconn
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT * FROM temp.caller")
			r=c.fetchone()
			self.__addon_id__ = r['addon_id']
		self.fanart=fanart
		self.traileritems=traileritems
		self.Player = xbmc.Player()
		self.trailerList = self.TrailerList()
		

	def onInit(self):
		self.setControlImage(self.FANARTIMAGE,self.fanart)
		if self.getControl(self.TRAILERLIST).size() == 0: 
			self.getControl(self.TRAILERLIST).addItems(self.trailerList)
		self.setFocusId(self.TRAILERLIST)
		

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.TRAILERLIST:
				self.PlayMedia(self.getControl(self.TRAILERLIST).getSelectedItem())

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
		if self.Player.isPlaying():
			import dialog_response
			response=dialog_response.DialogResponse('Media is still playing would you like to stop player before going back?','Yes','No')
			if response.index == 0:
				self.Player.stop()
		super(WindowTrailer,self).close()


	def setControlImage(self, controlId,image):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setImage(image)


	def PlayMedia(self,listitem):
		self.Player.play(listitem.getPath(),listitem,True)
		while(not xbmc.abortRequested):
			xbmc.sleep(1000)


	def ListItemBuilder(self,title,streamurl,thumb):
		li = xbmcgui.ListItem(title)
		li.setPath(streamurl)
		li.setInfo('video',{'title':title})
		li.setArt({'thumb':thumb})
		return li


	def TrailerList(self):
		content = []
		for i in self.traileritems:
			name = i.get('name')
			key = i.get('key')
			if i.get('site') == 'YouTube':
				stream_info = youtube_resolver.resolve(key, addon_id=self.__addon_id__)[0]
				meta = stream_info.get('meta')
				content.append(self.ListItemBuilder(name,stream_info.get('url'),meta.get('images').get('high')))
		return content




# u'name': u"Marvel's The Avengers- Trailer (OFFICIAL)", u'key': u'eOrNdBpGMv8', u'iso_3166_1': u'US', u'id': u'5794fd8bc3a3687605005cc9', u'size': 1080, u'type': u'Trailer', u'site': u'YouTube', u'iso_639_1': u'en'