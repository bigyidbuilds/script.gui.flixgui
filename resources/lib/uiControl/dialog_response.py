# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''
from collections import namedtuple

'''#####-----Internal Modules-----#####'''
from ._actions import *
from modules._addon import *
from modules._common import Log




class _DialogResponse(xbmcgui.WindowXMLDialog):

	FRAME         = 1000
	TEXTBOX       = 1001
	BUTTONGROUP   = 2000
	BUTTONA_GROUP = 2100
	BUTTONA       = 2101
	BUTTONB_GROUP = 2200
	BUTTONB       = 2201
	BUTTONC_GROUP = 2300
	BUTTONC       = 2301

	BUTTONS = [BUTTONA,BUTTONB,BUTTONC]

	xmlFilename = 'Dialog_Response.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'

	buttonResponse = None
	buttonIndex    = None

	def __new__(cls,pos,message,buttonA,buttonB,buttonC,*args,**kwargs):
		return super(_DialogResponse, cls).__new__(cls,_DialogResponse.xmlFilename, _DialogResponse.scriptPath, _DialogResponse.defaultSkin, _DialogResponse.defaultRes)
		

	def __init__(self,pos,message,buttonA,buttonB,buttonC,*args,**kwargs):
		super(_DialogResponse,self).__init__()
		self.pos     = pos
		self.message = message
		self.buttonA = buttonA
		self.buttonB = buttonB
		self.buttonC = buttonC
		self.setProperty('TEXTBOX',self.message)

	def onInit(self):
		self.getControl(999).setPosition(*self.pos)
		textboxH = self.getControl(self.TEXTBOX).getHeight()
		self.getControl(self.FRAME).setHeight(textboxH+75)
		self.getControl(1999).setPosition(0,textboxH)
		self.setControlLabel(self.BUTTONA,self.buttonA)
		if self.buttonB:
			self.setControlLabel(self.BUTTONB,self.buttonB)
		else:
			self.setControlVisible(self.BUTTONB_GROUP,False)
		if self.buttonC:
			self.setControlLabel(self.BUTTONC,self.buttonC)
		else:
			self.setControlVisible(self.BUTTONC_GROUP,False)

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()

	def onClick(self,controlId):
		Log('onClick: {}'.format(controlId))
		if controlId in self.BUTTONS:
			self.buttonResponse = self.getControlLabel(controlId)
			self.buttonIndex = self.BUTTONS.index(controlId)
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
		super(_DialogResponse,self).close()
		'''
		Function: close()
			Closes this window.

		Closes this window by activating the old window.

		Note
			The window is not deleted with this method. 
		'''

	def getControlLabel(self,controlId):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			return control.getLabel()

	def setControlLabel(self, controlId, label):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setLabel(label)

	def setControlText(self, controlId,text):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setText(text)


	def setControlVisible(self, controlId, visible):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setVisible(visible)



def DialogResponse(message,buttonA,buttonB=None,buttonC=None,posx=440,posy=0):
	#returns named tuple containing label and index of selected button
	_reponse = namedtuple('Response','label,index')
	pos = (posx,posy)
	d=_DialogResponse(pos,message,buttonA,buttonB,buttonC)
	d.doModal()
	response = _reponse._make([d.buttonResponse,d.buttonIndex])
	del d
	return response
