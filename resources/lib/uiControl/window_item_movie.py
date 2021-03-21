# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''
from collections import namedtuple
import os

'''#####-----Internal Modules-----#####'''
from ._actions import *
from modules._addon import *
from modules._common import DateTimeNow,Log
from modules import media_player 




class WindowItemMovie(xbmcgui.WindowXML):

	HEADERGROUP         = 1000 
	HEADERFANART        = 1001
	HEADERTITLE         = 1002
	HEADERYEAR          = 1003
	HEADERAGERATING     = 1004
	HEADERDURATION      = 1005
	HEADERPLOT          = 1006
	HEADERCAST          = 1007
	HEADERDIRECTOR      = 1008
	HEADERGENRES        = 1009
	OPTION_LIST         = 2000
	RATINGBUTTON        = 2101
	RATINGBUTTON_1      = 2102
	RATINGBUTTON_2      = 2103
	ICON_RATINGBUTTON   = 2110
	ICON_RATINGBUTTON_1 = 2111
	ICON_RATINGBUTTON_2 = 2112
	PLAYGROUP           = 2200
	PLAYBUTTON          = 2201
	PLAYPROGRESS        = 2203
	PLAYBEGGROUP        = 2300
	PLAYBEGBUTTON       = 2301
	PLAYTRAILGROUP      = 2400
	PLAYTRAILBUTTON     = 2401
	MORELIKEGROUP       = 2500
	MORELIKEBUTTON      = 2501
	MYLISTGROUP         = 2700
	MYLISTBUTTON        = 2701
	ICON_MYLISTBUTTON   = 2702
	CREDITSGROUP        = 2800
	CREDITSBUTTON       = 2801


	xmlFilename = 'Window_Item_Movie.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'


	def __new__(cls,dbconn,listitem,*args,**kwargs):
		return super(WindowItemMovie, cls).__new__(cls,WindowItemMovie.xmlFilename, WindowItemMovie.scriptPath, WindowItemMovie.defaultSkin, WindowItemMovie.defaultRes)
		

	def __init__(self,dbconn,listitem,*args,**kwargs):
		super(WindowItemMovie,self).__init__()
		self.dbconn = dbconn
		self.listitem = listitem
		self.movietuple = namedtuple('movieItem','runtime,credits_cast,credits_crew,genres,rated,inprogress,mylist,videos,streams,trailers')
		self.thumbtuple = namedtuple('thumbsRate','label,icon')
		self.mylisttuple = namedtuple('myList','label,icon')
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT tmdb_movie_details.runtime,tmdb_movie_details.credits_cast,tmdb_movie_details.credits_crew,tmdb_movie_details.genres,user_list.rated,user_watched_movie.inprogress,user_list.mylist,tmdb_movie_details.videos,movie_list.stream FROM master.tmdb_movie_details INNER JOIN movie_list USING(tmdb_id) INNER JOIN user_watched_movie USING(tmdb_id) INNER JOIN user_list USING(tmdb_id,media_type) WHERE  tmdb_movie_details.tmdb_id =?",(self.listitem.getUniqueID('tmdb'),))
			items = [x for x in c.fetchone()]+[None]
			c.execute("SELECT * FROM temp.caller")
			r=c.fetchone()
			self.tmdb_key =  r['tmdb_key']
			self.addon_id = r['addon_id']
		self.movieItem = self.movietuple._make(items)
		self.movieItem = self.movieItem._replace(trailers= list(filter(lambda d: d['type'] == 'Trailer', eval(self.movieItem.videos))))
		s = eval(self.movieItem.streams)
		self.movieItem = self.movieItem._replace(streams=s)
		try:
			self.ratingicon = os.path.join(AGE_RATE_ICON_FOLDER,xbmcaddon.Addon(self.addon_id).getSetting("general.region"),'{}.png'.format(self.listitem.getProperty('age_rating')))
		except:
			self.ratingicon = os.path.join(AGE_RATE_ICON_FOLDER,xbmcaddon.Addon(self.addon_id).getSetting("general.region"),'AV.png')
		self.visibleButtons = []
		self.return_from_player = False
		self.GetRating()
		self.GetMyListInfo()
	
		


	def onInit(self):
		if self.return_from_player:
			self.UpdateProgress()
		if len(self.movieItem.trailers) == 0:
			self.setControlVisible(self.PLAYTRAILGROUP,False)
		self.setControlVisible(self.RATINGBUTTON_1,False)
		self.setControlVisible(self.ICON_RATINGBUTTON_1,False)
		self.setControlVisible(self.RATINGBUTTON_2,False)
		self.setControlVisible(self.ICON_RATINGBUTTON_2,False)
		self.setControlImage(self.HEADERFANART,self.listitem.getArt('fanart'))
		self.setControlLabel(self.HEADERTITLE,self.listitem.getLabel())
		self.setControlLabel(self.HEADERYEAR,self.listitem.getProperty('year'))
		self.setControlImage(self.HEADERAGERATING,self.ratingicon)
		self.setControlLabel(self.HEADERDURATION,self.MediaDuration())
		self.setControlText(self.HEADERPLOT,self.listitem.getProperty('plot'))
		self.setControlLabel(self.HEADERCAST,self.CreditsCast())
		self.setControlLabel(self.HEADERDIRECTOR,self.CreditsDirector())
		self.setControlLabel(self.HEADERGENRES,self.Genres())
		self.setControlLabel(self.RATINGBUTTON,self.thumbsRate.label)
		self.setControlImage(self.ICON_RATINGBUTTON,self.thumbsRate.icon)
		self.setControlLabel(self.MYLISTBUTTON,self.myList.label)
		self.setControlImage(self.ICON_MYLISTBUTTON,self.myList.icon)
		self.SetPlayedInfo()
		



	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_DOWN]:
			if self.getFocusId() in [self.RATINGBUTTON_1,self.RATINGBUTTON_2]:
				self.RatingButtonCtrl()
				self.setFocusId(self.PLAYBUTTON)

	def onClick(self,controlId):
		Log('onClick: {}'.format(controlId))
		if controlId in [self.RATINGBUTTON_1,self.RATINGBUTTON_2]:
			self.SetRating(controlId)
		elif controlId == self.MYLISTBUTTON:
			self.SetMyListInfo()
		elif controlId == self.PLAYBUTTON:
			if self.getControlLabel(self.PLAYBUTTON) == 'Resume':
				self.PlayMedia(seek=True)
			else:
				self.PlayMedia()
		elif controlId ==  self.PLAYBEGBUTTON:
			self.PlayMedia()
		elif controlId == self.PLAYTRAILBUTTON:
			from . import window_trailer
			d=window_trailer.WindowTrailer(self.dbconn,self.listitem.getArt('fanart'),self.movieItem.trailers)
			d.doModal()
			del d
		elif controlId == self.MORELIKEBUTTON:
			from . import window_more
			d=window_more.WindowMore(self.dbconn,self.listitem,self.movieItem)
			d.doModal()
			del d
		elif controlId == self.CREDITSBUTTON:
			from . import window_credits
			d=window_credits.WindowCredits(self.movieItem.credits_cast,self.movieItem.credits_crew,self.movieItem.videos,self.listitem.getUniqueID('tmdb'))
			d.doModal()
			del d



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
		Log('onFocus: {}'.format(controlId))
		if controlId ==  self.RATINGBUTTON:
			self.RatingButtonCtrl()


	def Close(self):
		self.setControlProgress(self.PLAYPROGRESS,0)
		del self.movieItem
		super(WindowItemMovie,self).close()
		'''
		Function: close()
			Closes this window.

		Closes this window by activating the old window.

		Note
			The window is not deleted with this method. 
		'''

	def getControlLabel(self,controlId):
		if not controlId:
			label = None
		control = self.getControl(controlId)
		if control:
			label = control.getLabel()
		return label

	def setControlImage(self, controlId,image):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setImage(image)

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

	def setControlProgress(self,controlId,percent):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setPercent(percent)

	def MediaDuration(self):
		duration = self.movieItem.runtime
		if duration <= 59:
			duration = '{:02d}m'.format(duration)
		else:
			duration = '{:d}h {:02d}m'.format(*divmod(duration, 60))
		return duration

	def CreditsCast(self):
		castlist = []
		actors = eval(self.movieItem.credits_cast)
		for actor in actors:
			if actor.get('order') in range(0,5):
				castlist.append(actor.get('name'))
		return 'Cast: '+', '.join(castlist)

	def CreditsDirector(self):
		dirlist = []
		crew = eval(self.movieItem.credits_crew)
		for member in crew:
			if ("job","Director") in member.items():
				dirlist.append(member.get("name"))
		return 'Director: '+', '.join(dirlist)

	def Genres(self):
		return ', '.join([x.get('name') for x in eval(self.movieItem.genres)])


	def RatingButtonCtrl(self):
		if self.getControl(self.RATINGBUTTON).isVisible():
			for x in [(self.RATINGBUTTON,False),(self.ICON_RATINGBUTTON,False),(self.RATINGBUTTON_1,True),(self.ICON_RATINGBUTTON_1,True),(self.RATINGBUTTON_2,True),(self.ICON_RATINGBUTTON_2,True)]:
				self.setControlVisible(*x)
				self.setFocusId(self.RATINGBUTTON_1)
		else:
			for x in [(self.RATINGBUTTON,True),(self.ICON_RATINGBUTTON,True),(self.RATINGBUTTON_1,False),(self.ICON_RATINGBUTTON_1,False),(self.RATINGBUTTON_2,False),(self.ICON_RATINGBUTTON_2,False)]:
				self.setControlVisible(*x)


	def GetRating(self):
		if self.movieItem.rated == True:
			Icon = 'button-icon-thumbs-up.png'
			Label = 'Change Rating'
		elif self.movieItem.rated == False:
			Icon = 'button-icon-thumbs-down.png'
			Label = 'Change Rating'
		else:
			Icon = 'button-icon-thumbs-up.png'
			Label = 'Rate This Title'
		self.thumbsRate = self.thumbtuple._make([Label,Icon])



	def SetRating(self,controlId):
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			if controlId == self.RATINGBUTTON_1:
				vote = True
			elif controlId == self.RATINGBUTTON_2:
				vote = False
			c.execute("UPDATE user_list SET rated=?,rated_date=? WHERE tmdb_id=? AND media_type=?",(vote,DateTimeNow(),self.listitem.getUniqueID('tmdb'),'movie'))
			self.dbconn.conn.commit()
		self.movieItem = self.movieItem._replace(rated=vote)
		self.GetRating()
		self.RatingButtonCtrl()
		self.setControlLabel(self.RATINGBUTTON,self.thumbsRate.label)
		self.setControlImage(self.ICON_RATINGBUTTON,self.thumbsRate.icon)

	def UpdateProgress(self):
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT inprogress FROM user_watched_movie WHERE tmdb_id =?",(self.listitem.getUniqueID('tmdb'),))
			prg = c.fetchone()
			if prg:
				self.movieItem = self.movieItem._replace(inprogress=prg[0]) 



	def SetPlayedInfo(self):
		if self.movieItem.inprogress:
			self.setControlLabel(self.PLAYBUTTON,'Resume')
			self.setControlProgress(self.PLAYPROGRESS,(100.00/(self.movieItem.runtime*60))*self.movieItem.inprogress)
		else:
			self.setControlLabel(self.PLAYBUTTON,'Play')
			self.setControlVisible(self.PLAYBEGGROUP,False)
			self.setControlVisible(self.PLAYPROGRESS,False)

	def GetMyListInfo(self):
		if self.movieItem.mylist == True:
			Label = 'Remove From MyList' 
			Icon = 'button-icon-minus.png'
		elif self.movieItem.mylist == False:
			Label = 'Add To MyList'
			Icon = 'button-icon-plus.png'
		else:
			Label = 'Add To MyList'
			Icon = 'button-icon-plus.png'
		self.myList = self.mylisttuple._make([Label,Icon])


	def SetMyListInfo(self):
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			if self.movieItem.mylist == True:
				added = False
			elif self.movieItem.mylist == False:
				added = True
			else:
				added = True
			c.execute("UPDATE user_list SET mylist=?,mylist_date=? WHERE tmdb_id=? AND media_type=?",(added,DateTimeNow(),self.listitem.getUniqueID('tmdb'),'movie'))
			self.dbconn.conn.commit()
		self.movieItem = self.movieItem._replace(mylist=added)
		self.GetMyListInfo()
		self.setControlLabel(self.MYLISTBUTTON,self.myList.label)
		self.setControlImage(self.ICON_MYLISTBUTTON,self.myList.icon)


	def PlayMedia(self,seek=False):
		if len(self.movieItem.streams) > 1:
			listitems = []
			for i,s in enumerate(self.movieItem.streams):
				li = xbmcgui.ListItem()
				li.setLabel('Stream {}'.format(i+1))
				li.setPath(s)
				li.setProperty('list_pos',str(i))
				listitems.append(li)
			import dialog_listselect
			selected = dialog_listselect.DialogListselect('Multiple Streams Available please select one',listitems)
			self.listitem.setPath(selected.item.getPath())
		else:
			self.listitem.setPath(self.movieItem.streams[0])
		self.return_from_player = True
		if seek:
			media_player.PlayerCallBack(self.dbconn,self.listitem,seekpos=self.movieItem.inprogress)
		else:
			media_player.PlayerCallBack(self.dbconn,self.listitem)



