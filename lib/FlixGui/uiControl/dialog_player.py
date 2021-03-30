# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui

'''######------External Modules-----#####'''


'''#####-----Internal Modules-----#####'''
from ._actions import *
from FlixGui.modules._common import Log




class DialogPlayer(xbmcgui.WindowXMLDialog):

	'''
	___info__ add buttons and controls,similar to example below
	BUTTON_CLOSE = 100
	HEADING_CTRL = 200
	TEXT_CTRL    = 201
	'''

	xmlFilename = 'Dialog_Player.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'



	def __new__(cls,listitem,*args,**kwargs):
		return super(DialogPlayer, cls).__new__(cls,DialogPlayer.xmlFilename, DialogPlayer.scriptPath, DialogPlayer.defaultSkin, DialogPlayer.defaultRes)
		

	def __init__(self,listitem,*args,**kwargs):
		super(DialogPlayer,self).__init__()
		self.listitem = listitem
		self.Player = self._Player()

	def onInit(self):
		self.PlayMedia()
		


	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()

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
		super(DialogPlayer,self).close()

	def PlayMedia(self):
		self.Player.play(self.listitem.getPath(),self.listitem,True)
		while(not xbmc.abortRequested):
			xbmc.sleep(1000)


	class _Player(xbmc.Player):

		def __init__(self):
			xbmc.Player.__init__(self)


		def onPlayBackEnded(self):
			xbmc.executebuiltin('Dialog.Close(all,true) ')

