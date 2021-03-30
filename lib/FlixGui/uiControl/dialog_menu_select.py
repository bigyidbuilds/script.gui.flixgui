# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcaddon
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''


'''#####-----Internal Modules-----#####'''
from ._actions import *
from FlixGui.modules._common import Log,Sleep




class DialogMenuSelect(xbmcgui.WindowXMLDialog):

	SIDECTRLWINDOW       = 1000
	SIDECTRLGROUP        = 1001
	SIDECTRLHOME         = 1002
	SIDECTRLHOME_INDI    = 10021
	SIDECTRLSEARCH       = 1003
	SIDECTRLSEARCH_INDI  = 10031
	SIDECTRLMOVIE        = 1004
	SIDECTRLMOVIE_INDI   = 10041
	SIDECTRLTV           = 1005
	SIDECTRLTV_INDI      = 10051
	SIDECTRLSETTING      = 1006
	SIDECTRLSETTING_INDI = 10061
	SIDECTRLMYLIST       = 1007
	SIDECTRLMYLIST_INDI  = 10071
	EXITBUTTON           = 1100

	xmlFilename = 'Dialog_Menu_Select.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'

	viewselected = None
	exit         = False
	backtolist   = False

	def __new__(cls,dbconn,sidectrlfocus,sidectrlindi,*args,**kwargs):
		return super(DialogMenuSelect, cls).__new__(cls,DialogMenuSelect.xmlFilename, DialogMenuSelect.scriptPath, DialogMenuSelect.defaultSkin, DialogMenuSelect.defaultRes)
		

	def __init__(self,dbconn,sidectrlfocus,sidectrlindi,*args,**kwargs):
		super(DialogMenuSelect,self).__init__()
		self.dbconn        = dbconn
		self.sidectrlfocus = sidectrlfocus
		self.sidectrlindi  = sidectrlindi



	def onInit(self):
		if self.sidectrlfocus != 0:
			self.setFocusId(self.sidectrlfocus)
		else:
			self.setFocusId(self.SIDECTRLHOME)
		if self.sidectrlindi != 0:
			self.setSideCtrlIndi(self.sidectrlindi)
		else:
			self.setSideCtrlIndi(self.SIDECTRLHOME_INDI)


	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU,ACTION_RIGHT]:
			self.backtolist = True
			self.Close()

			

	def onClick(self,controlId):
		Log('onClick: {}'.format(controlId))
		if controlId == self.EXITBUTTON:
			self.exit = True
		else:
			self.viewselected =  controlId
		self.Close()


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
		self.clearProperty( "AnimationWaitingDialogOnClose" )
		Sleep(.4)
		super(DialogMenuSelect,self).close()


	def setControlVisible(self, controlId, visible):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setVisible(visible)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return

	def setSideCtrlIndi(self,required):
		for i in [self.SIDECTRLHOME_INDI,self.SIDECTRLSEARCH_INDI,self.SIDECTRLMOVIE_INDI,self.SIDECTRLTV_INDI,self.SIDECTRLSETTING_INDI,self.SIDECTRLMYLIST_INDI]:
			if i != required:
				self.setControlVisible(i,False)
		self.setControlVisible(required,True)


