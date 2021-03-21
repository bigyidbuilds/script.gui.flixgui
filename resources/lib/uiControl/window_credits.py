# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''
import sqlite3
import youtube_resolver

'''#####-----Internal Modules-----#####'''
from ._actions import *
from modules._addon import *
from modules._common import Log




class WindowCredits(xbmcgui.WindowXML):

	CASTGROUP   = 2100
	CASTBUTTON  = 2101
	CREWGROUP   = 2200
	CREWBUTTON  = 2201
	VIDEOGROUP  = 2300
	VIDEOBUTTON = 2301
	CASTPANEL   = 3000
	CREWPANEL   = 3500
	VIDEOPANEL  = 4000

	xmlFilename = 'Window_Credits.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'

	def __new__(cls,dbconn,cast_dict,crew_dict,videos_dict,tmdb_id,*args,**kwargs):
		return super(WindowCredits, cls).__new__(cls,WindowCredits.xmlFilename, WindowCredits.scriptPath, WindowCredits.defaultSkin, WindowCredits.defaultRes)
		

	def __init__(self,dbconn,cast_dict,crew_dict,videos_dict,tmdb_id,*args,**kwargs):
		super(WindowCredits,self).__init__()
		self.dbconn = dbconn
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT * FROM temp.caller")
			r=c.fetchone()
			self.__addon_id__ = r['addon_id']
		self.cast_dict = eval(cast_dict)
		self.crew_dict = eval(crew_dict)
		self.videos_dict = eval(videos_dict)
		self.tmdb_id = tmdb_id

	def onInit(self):
		self.getControl(self.CASTPANEL).reset()
		self.getControl(self.CREWPANEL).reset()
		self.getControl(self.VIDEOPANEL).reset()
		self.getControl(self.CASTPANEL).addItems(self.CastList())
		self.getControl(self.CREWPANEL).addItems(self.CrewList())
		self.getControl(self.VIDEOPANEL).addItems(self.VideoList())


	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			Log(self.getFocusId())
			if self.getFocusId() == self.VIDEOPANEL:
				from . import dialog_player
				d=dialog_player.DialogPlayer(self.getControl(self.VIDEOPANEL).getSelectedItem())
				d.doModal()
				del d

	def onClick(self,controlId):
		if controlId == self.CASTBUTTON:
			self.ReLoadMainPanel(self.CastList())
		elif controlId == self.CREWBUTTON:
			self.ReLoadMainPanel(self.CrewList())

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
		super(WindowCredits,self).close()
		'''
		Function: close()
			Closes this window.

		Closes this window by activating the old window.

		Note
			The window is not deleted with this method. 
		'''


	def ListItemBuilder(self,label,thumb,moviedb,dbID,label2=None,streamurl=None):
		#default_icon = DefaultActor.png|DefaultDirector.png
		li = xbmcgui.ListItem(label,label2)
		li.setLabel(label)
		if label2:
			li.setLabel2(label2)
		if streamurl:
			li.setPath(streamurl)
		li.setUniqueIDs({moviedb:dbID},moviedb)
		li.setInfo('video',{'title':label})
		li.setArt({'thumb':thumb})
		return li


	def CastList(self):
		content = []
		for i in self.cast_dict:
			image_url = i.get('profile_path')
			if image_url:
				profile_path = 'https://image.tmdb.org/t/p/original'+image_url
			else:
				profile_path = 'DefaultActor.png'
			content.append(self.ListItemBuilder(i.get('name',i.get('original_name','Name Missing')),profile_path,'tmdb',i.get('id'),label2=i.get('character')))
		return content

	def CrewList(self):
		content = []
		for i in self.crew_dict:
			image_url = i.get('profile_path')
			if image_url:
				profile_path = 'https://image.tmdb.org/t/p/original'+image_url
			else:
				profile_path = 'DefaultDirector.png'
			content.append(self.ListItemBuilder(i.get('name',i.get('original_name','Name Missing')),profile_path,'tmdb',i.get('id'),label2=i.get('job')))
		return content


	def VideoList(self):
		content = []
		for i in self.videos_dict:
			name = i.get('name')
			key = i.get('key')
			if i.get('site') == 'YouTube':
				stream_info = youtube_resolver.resolve(key, addon_id=self.__addon_id__)[0]
				meta = stream_info.get('meta')
				content.append(self.ListItemBuilder(name,meta.get('images').get('high'),'tmdb',self.tmdb_id,streamurl=stream_info.get('url')))
		return content


	def ReLoadMainPanel(self,listitems):
		control = self.getControl(self.MAINPANEL)
		control.reset()
		control.addItems(listitems)