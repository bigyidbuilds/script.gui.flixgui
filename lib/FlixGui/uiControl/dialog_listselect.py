# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''
from collections import namedtuple

'''#####-----Internal Modules-----#####'''
from ._actions import *
from FlixGui.modules._common import Log




class _DialogListselect(xbmcgui.WindowXMLDialog):

	DIALOG     = 1000
	BACKGROUND = 1001
	TEXT       = 2000
	LIST       = 3000

	xmlFilename = 'Dialog_Listselect.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'


	listItem = None
	listIndex = None



	def __new__(cls,text,listitems,*args,**kwargs):
		return super(_DialogListselect, cls).__new__(cls,_DialogListselect.xmlFilename, _DialogListselect.scriptPath, _DialogListselect.defaultSkin, _DialogListselect.defaultRes)
		

	def __init__(self,text,listitems,*args,**kwargs):
		super(_DialogListselect,self).__init__()
		self.setProperty('TEXT',text)
		self.listitems = listitems


	def onInit(self):
		labelH = self.getControl(self.TEXT).getHeight()+10
		Log(labelH)
		listH  = len(self.listitems)*50
		Log(listH)
		totalH = labelH+listH
		top_pos = (720-totalH)/2
		self.getControl(self.DIALOG).setPosition(440,top_pos)
		self.getControl(self.BACKGROUND).setHeight(totalH)
		self.ctrllist = self.getControl(self.LIST)
		self.ctrllist.setPosition(5,labelH+5)
		self.ctrllist.addItems(self.listitems)
		self.setFocusId(self.LIST)



	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()

	def onClick(self,controlId):
		Log('onClick:{}'.format(controlId))
		if controlId == self.LIST:
			self.listItem = self.ctrllist.getSelectedItem()
			self.listIndex = self.ctrllist.getSelectedPosition()
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
		super(_DialogListselect,self).close()




def DialogListselect(message,listitems):
	#returns named tuple containing label and index of selected button
	_selected = namedtuple('Selected','item,index')
	d=_DialogListselect(message,listitems)
	d.doModal()
	selected = _selected._make([d.listItem,d.listIndex])
	del d
	return selected