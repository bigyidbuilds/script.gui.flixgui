# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''


'''#####-----Internal Modules-----#####'''
from ._actions import *
from modules._addon import *
from modules._common import Log
from modules import media_player 




class WindowTvEpisodes(xbmcgui.WindowXML):

	HEADERGROUP   = 1000
	HEADERTITLE   = 1001
	HEADERYEAR    = 1002
	HEADERAGERATE = 1003
	HEADERSEASONS = 1004
	SEASONLIST    = 2000
	EPISODELIST   = 3000

	xmlFilename = 'Window_Tv_Episodes.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'


	artUrl = 'https://image.tmdb.org/t/p/original'

	def __new__(cls,dbconn,listitem,ratingicon,total_seasons,current_episode,*args,**kwargs):
		return super(WindowTvEpisodes, cls).__new__(cls,WindowTvEpisodes.xmlFilename, WindowTvEpisodes.scriptPath, WindowTvEpisodes.defaultSkin, WindowTvEpisodes.defaultRes)
		

	def __init__(self,dbconn,listitem,ratingicon,total_seasons,current_episode,*args,**kwargs):
		super(WindowTvEpisodes,self).__init__()
		self.dbconn = dbconn
		self.listitem = listitem
		self.tmdbid = self.listitem.getUniqueID('tmdb')
		self.ratingicon = ratingicon
		self.total_seasons = total_seasons
		self.seasonswithepisodes = self.GetSeasonsWithEpisodes()
		self.episodeList = self.GetEpisodes()
		self.current_episode = current_episode


	def onInit(self):
		self.getControl(self.SEASONLIST).reset()
		self.getControl(self.EPISODELIST).reset()
		self.setControlLabel(self.HEADERTITLE,self.listitem.getLabel())
		self.setControlLabel(self.HEADERYEAR,self.listitem.getProperty('year'))
		self.setControlImage(self.HEADERAGERATE,self.ratingicon)
		self.setControlLabel(self.HEADERSEASONS,self.total_seasons)
		for s in self.seasonswithepisodes:
			e = self.GetTotalEpisodesPerSeason(s)
			lis = xbmcgui.ListItem('Season {}'.format(s),'{} Episodes'.format(e))
			lis.setProperty('season',str(s))
			self.getControl(self.SEASONLIST).addItem(lis)
		self.getControl(self.EPISODELIST).addItems(self.episodeList)
		self.SetFocusEpisodeList()

# ted.tmdb_id,ted.overview,ted.still_path,ted.air_date,ted.title,ted.season_number,ted.episode_number

	def onAction(self,action):
		actionId = action.getId()
		focusId =  self.getFocusId()
		Log('onAction: {}'.format(action.getId()))
		if actionId in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif actionId in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if focusId == self.SEASONLIST:
				listitem = self.getControl(focusId).getSelectedItem()
				self.SetFocusEpisodeList_Season(listitem)
			elif focusId == self.EPISODELIST:
				listitem = self.getControl(focusId).getSelectedItem()
				self.PlayMedia(listitem)


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
		super(WindowTvEpisodes,self).close()


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


	def GetSeasonsWithEpisodes(self):
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT DISTINCT season FROM tv_episode_list WHERE tmdb_id=? ORDER BY season ASC",(self.tmdbid,))
			i = [x[0] for x in c.fetchall()]
			c.close()
		return i 


	def GetTotalEpisodesPerSeason(self,season):
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT COUNT(*) FROM tv_episode_list WHERE tmdb_id = ? AND season=?",(self.tmdbid,season))
			i =  c.fetchone()[0]
			c.close()
		return i 


	def GetEpisodes(self):
		content = []
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT ted.tmdb_id,ted.overview,ted.still_path,ted.air_date,ted.title,ted.season_number,ted.episode_number,uwt.inprogress,uwt.runtime FROM tmdb_episode_details ted INNER JOIN tv_episode_list tel ON ted.tmdb_id = tel.tmdb_id AND ted.season_number=tel.season AND ted.episode_number=tel.episode INNER JOIN user_watched_tv uwt ON ted.tmdb_id = uwt.tmdb_id AND ted.season_number=uwt.season AND ted.episode_number=uwt.episode WHERE ted.tmdb_id=? ORDER BY ted.season_number,ted.episode_number",(self.tmdbid,))
			items = c.fetchall()
			for i in items:
				if i[2]:
					still_path = i[2]
				else:
					still_path = 'DefaultTVShows.png'
				if i[7]:
					progress = i[7]
				else:
					progress = 0
				if i[8]:
					runtime = i[8]
				else:
					runtime = 0
				content.append(self.ListItemBuilder(i[4],still_path,self.listitem.getArt('fanart'),'tmdb',self.listitem.getRating('tmdb'),self.listitem.getVotes('tmdb'),self.tmdbid,i[1],self.listitem.getProperty('genres'),self.listitem.getProperty('year'),'tvshow',self.listitem.getProperty('age_rating'),i[6],i[5],progress,runtime))
			c.close()
		return content



	def ListItemBuilder(self,title,poster,fanart,moviedb,votes,count,dbID,plot,genres,year,mediatype,age_rating,episode,season,progress,runtime):
		'''setInfo, genres single string or list of strings,year int,
		moviedb, "imdb"/"tvdb"/"tmdb"/"anidb"'''
		li= xbmcgui.ListItem(title)
		li.setArt({'poster':poster,'fanart':fanart})
		li.setRating(moviedb,votes,count,True)
		li.setUniqueIDs({moviedb:dbID},moviedb)
		li.setInfo('video', {'genre':genres,'year':year,'plot':plot,'title':title,'episode':episode,'season':season,'mediatype':mediatype,'duration':runtime})
		li.setProperties({'mediatype':mediatype,'moviedb':moviedb.upper(),'year':year,'age_rating':age_rating,'plot':plot,'genres':str(genres),'season':season,'episode':episode,'resumetime':float(progress),'totaltime':float(runtime)})
		return li


	def GetSeasonPos(self,season):
		for i,listitem in enumerate(self.episodeList):
			if listitem.getProperty('season') == season:
				return i
		return 0

	def GetSeasonEpisodePos(self,season,episode):
		for i,listitem in enumerate(self.episodeList):
			if listitem.getProperty('season') == season and listitem.getProperty('episode') == episode:
				return i
		return 0

	def SetFocusEpisodeList(self):
		pos = self.GetSeasonEpisodePos(self.current_episode.season,self.current_episode.episode)
		xbmc.executebuiltin('control.setfocus({},{},absolute)'.format(self.EPISODELIST,pos))


	def SetFocusEpisodeList_Season(self,listitem):
		season = listitem.getProperty('season')
		pos = self.GetSeasonPos(season)
		xbmc.executebuiltin('control.setfocus({},{},absolute)'.format(self.EPISODELIST,pos))


	def PlayMedia(self,listitem):
		season = listitem.getProperty('season')
		episode = listitem.getProperty('episode')
		progress = float(listitem.getProperty('resumetime'))
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT stream FROM tv_episode_list WHERE tmdb_id=? AND season=? AND episode=?",(self.tmdbid,season,episode))
			streams = c.fetchone()
			if streams:
				streams = eval(streams[0])
			if len(streams) > 1:
				listitems = []
				for i,s in enumerate(self.movieItem.streams):
					li = xbmcgui.ListItem()
					li.setLabel('Stream {}'.format(i+1))
					li.setPath(s)
					li.setProperty('list_pos',str(i))
					listitems.append(li)
				import dialog_listselect
				selected = dialog_listselect.DialogListselect('Multiple Streams Available please select one',listitems)
				listitem.setPath(selected.item.getPath())
			else:
				listitem.setPath(streams[0])
		if progress > 0:
			media_player.PlayerCallBack(self.dbconn,listitem,seekpos=progress)
		else:
			media_player.PlayerCallBack(self.dbconn,listitem)
