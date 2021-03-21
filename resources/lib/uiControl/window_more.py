# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''
import sqlite3
'''#####-----Internal Modules-----#####'''
from ._actions import *
from modules._addon import *
from modules._common import Log,DateTimeStrf
from modules import tmdbapi




class WindowMore(xbmcgui.WindowXML):

	HEADERGROUP   = 1000
	HEADERTITLE   = 1001
	HEADERYEAR    = 1002
	HEADERAGERATE = 1003
	HEADERTERM    = 1004
	NAMELIST      = 2000
	MAINLIST      = 3000

	xmlFilename = 'Window_More.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'

	def __new__(cls,dbconn,listitem,addinfo,*args,**kwargs):
		return super(WindowMore, cls).__new__(cls,WindowMore.xmlFilename, WindowMore.scriptPath, WindowMore.defaultSkin, WindowMore.defaultRes)
		

	def __init__(self,dbconn,listitem,addinfo,*args,**kwargs):
		super(WindowMore,self).__init__()
		self.dbconn = dbconn
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT * FROM temp.caller")
			r=c.fetchone()
			self.tmdb_key =  r['tmdb_key']
		self.listitem = listitem
		self.addinfo = addinfo
		self.tmDB = tmdbapi.TmdbApi(self.tmdb_key)
		self.mediatype = self.listitem.getProperty('mediatype')
		self.tmdbid = self.listitem.getUniqueID('tmdb')
		self.ratingicon = self.AgeRateIcon(self.listitem.getProperty('age_rating'))
		if self.mediatype == 'tv':
			self.header_term = self.TotalSeasons(self.addinfo.total_seasons)
		elif self.mediatype == 'movie':
			self.header_term = self.MediaDuration(addinfo.runtime)
		else:
			self.header_term = ''
		self.content = self.GetListContent()



	def onInit(self):
		self.getControl(self.NAMELIST).reset()
		self.getControl(self.MAINLIST).reset()
		self.setControlLabel(self.HEADERTITLE,self.listitem.getLabel())
		self.setControlLabel(self.HEADERYEAR,self.listitem.getProperty('year'))
		self.setControlImage(self.HEADERAGERATE,self.ratingicon)
		self.setControlLabel(self.HEADERTERM,self.header_term)
		self.getControl(self.NAMELIST).addItem(xbmcgui.ListItem('More Like','{} titles'.format(len(self.content))))
		self.getControl(self.MAINLIST).addItems(self.content)
		self.setFocusId(self.MAINLIST)
		


	def onAction(self,action):
		actionId = action.getId()
		focusId =  self.getFocusId()
		Log('onAction: {}'.format(action.getId()))
		if actionId in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif actionId in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if focusId == self.MAINLIST:
				listitem = self.getControl(focusId).getSelectedItem()
				if self.mediatype == 'movie':
					import window_item_movie
					d=window_item_movie.WindowItemMovie(self.dbconn,listitem)
					d.doModal()
					del d
				elif self.mediatype == 'tv':
					import window_item_tv
					d=window_item_tv.WindowItemTv(self.dbconn,listitem)
					d.doModal()
					del d


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
		super(WindowMore,self).close()


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


	def MediaDuration(self,duration):
		if duration <= 59:
			duration = '{:02d}m'.format(duration)
		else:
			duration = '{:d}h {:02d}m'.format(*divmod(duration, 60))
		return duration


	def TotalSeasons(self,seasons):
		if seasons > 1:
			label = '{} Seasons'.format(seasons)
		else:
			label = '1 Season'
		return label


	def GetListContent(self):
		litems = []
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			if self.mediatype == 'tv':
				similar = self.tmDB.tv(self.tmdbid,'Similar').get('results')
				c.execute("SELECT tmdb_id FROM tv_list")
				tmdbids = [ x[0] for x in c.fetchall()]
				for s in similar:
					tmdbID = s.get('id')
					if tmdbID  in tmdbids:
						c.execute("SELECT * FROM tmdb_tv_details WHERE tmdb_id=?",(tmdbID,))
						items = c.fetchall()
						for i in items:
							litems.append(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],i[7],DateTimeStrf(i[4],'%Y'),i[9],i[10],self.header_term))
			elif self.mediatype == 'movie':
				similar = self.tmDB.movie(self.tmdbid,'Similar').get('results')
				c.execute("SELECT tmdb_id FROM movie_list")
				tmdbids = [ x[0] for x in c.fetchall()]
				for s in similar:
					tmdbID = s.get('id')
					if tmdbID  in tmdbids:
						c.execute("SELECT * FROM tmdb_movie_details WHERE tmdb_id=?",(tmdbID,))
						items = c.fetchall()
						for i in items:
							litems.append(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],i[7],DateTimeStrf(i[4],'%Y'),i[9],i[10],self.header_term))
			else:
				similar = None
				tmdbids = []

		return litems


	def ListItemBuilder(self,title,poster,fanart,moviedb,votes,count,dbID,plot,genres,year,mediatype,age_rating,term):
		'''setInfo, genres single string or list of strings,year int,
		moviedb, "imdb"/"tvdb"/"tmdb"/"anidb"'''
		thumb = self.AgeRateIcon(age_rating)
		li= xbmcgui.ListItem(title)
		li.setArt({'poster':poster,'fanart':fanart,'thumb':thumb})
		li.setRating(moviedb,votes,count,True)
		li.setUniqueIDs({moviedb:dbID},moviedb)
		li.setInfo('video', {'genre':genres,'year':year,'plot':plot,'title':title,'mediatype':mediatype})
		li.setProperties({'mediatype':mediatype,'moviedb':moviedb.upper(),'year':year,'age_rating':age_rating,'plot':plot,'genres':str(genres),'term':term})
		return li


	def AgeRateIcon(self,age_rating):
		try:
			ratingicon = eval('RATE_'+age_rating+'_ICON')
		except:
			ratingicon = RATE_AV_ICON
		return ratingicon