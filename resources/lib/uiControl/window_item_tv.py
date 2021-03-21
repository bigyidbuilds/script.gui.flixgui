# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''
from collections import namedtuple
from dateutil import parser as dparser
import os
from sqlite3 import OperationalError
from urllib import parse as urlparse
'''#####-----Internal Modules-----#####'''
from ._actions import *
from modules._addon import *
from modules._common import DateTimeNow,DateTimeStrp,Log
from modules import tmdbapi
from modules import media_player 




class WindowItemTv(xbmcgui.WindowXML):

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
	PLAYBEGGROUP        = 2250
	PLAYBEGBUTTON       = 2251
	EPISODEGROUP        = 2300
	EPISODEBUTTON       = 2301
	PLAYTRAILGROUP      = 2400
	PLAYTRAILBUTTON     = 2401
	MORELIKEGROUP       = 2500
	MORELIKEBUTTON      = 2501
	MYLISTGROUP         = 2700
	MYLISTBUTTON        = 2701
	ICON_MYLISTBUTTON   = 2702
	CREDITSGROUP        = 2800
	CREDITSBUTTON       = 2801


	xmlFilename = 'Window_Item_Tv.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'




	def __new__(cls,dbconn,listitem,*args,**kwargs):
		return super(WindowItemTv, cls).__new__(cls,WindowItemTv.xmlFilename, WindowItemTv.scriptPath, WindowItemTv.defaultSkin, WindowItemTv.defaultRes)
		

	def __init__(self,dbconn,listitem,*args,**kwargs):
		super(WindowItemTv,self).__init__()
		self._config = imp.load_source('_config',CALLER_CONFIG)
		self.dbconn = dbconn
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT * FROM temp.caller")
			r=c.fetchone()
			self.tmdb_key =  r['tmdb_key']
			self.addon_id = r['addon_id']
		self.listitem = listitem
		self.tmdbid = self.listitem.getUniqueID('tmdb')
		self.tmDB = tmdbapi.TmdbApi(self.tmdb_key)
		self.artbase = urlparse.urlparse(self.tmDB.configuration('APIConfiguration').get('images').get('base_url'))
		self.mediatype = self.listitem.getProperty('mediatype')
		self.tvtuple = namedtuple('tvItem','total_seasons,credits_cast,credits_crew,genres,rated,mylist,videos,trailers')
		self.thumbtuple = namedtuple('thumbsRate','label,icon')
		self.mylisttuple = namedtuple('myList','label,icon')
		self.myseasonprogresstuple = namedtuple('mySeasonprogress','season,episode,inprogress,runtime')
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT tmdb_tv_details.total_seasons,tmdb_tv_details.credits_cast,tmdb_tv_details.credits_crew,tmdb_tv_details.genres,user_list.rated,user_list.mylist,tmdb_tv_details.videos FROM master.tmdb_tv_details INNER JOIN tv_list USING(tmdb_id) INNER JOIN user_list USING(tmdb_id,media_type) WHERE tmdb_tv_details.tmdb_id = ?",(self.tmdbid,))
			items = [x for x in c.fetchone()]+[None]
			c.close()
		self.tvItem = self.tvtuple._make(items)
		self.tvItem = self.tvItem._replace(trailers= list(filter(lambda d: d['type'] == 'Trailer', eval(self.tvItem.videos))))
		try:
			self.ratingicon = os.path.join(AGE_RATE_ICON_FOLDER,xbmcaddon.Addon(self.addon_id).getSetting("general.region"),'{}.png'.format(self.listitem.getProperty('age_rating')))
		except:
			self.ratingicon = os.path.join(AGE_RATE_ICON_FOLDER,xbmcaddon.Addon(self.addon_id).getSetting("general.region"),'AV.png')
		self.total_seasons_label = self.TotalSeasons()
		self.GetTmdbInfo()
		self.GetRating()
		self.GetMyListInfo()
		
		
		
	
		


	def onInit(self):
		self.GetSeriesProgress()
		if len(self.tvItem.trailers) == 0:
			self.setControlVisible(self.PLAYTRAILGROUP,False)
		self.setControlVisible(self.RATINGBUTTON_1,False)
		self.setControlVisible(self.ICON_RATINGBUTTON_1,False)
		self.setControlVisible(self.RATINGBUTTON_2,False)
		self.setControlVisible(self.ICON_RATINGBUTTON_2,False)
		self.setControlImage(self.HEADERFANART,self.listitem.getArt('fanart'))
		self.setControlLabel(self.HEADERTITLE,self.listitem.getLabel())
		self.setControlLabel(self.HEADERYEAR,self.listitem.getProperty('year'))
		self.setControlImage(self.HEADERAGERATING,self.ratingicon)
		self.setControlLabel(self.HEADERDURATION, self.total_seasons_label)
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
			if self.getControlLabel(self.PLAYBUTTON).startswith('Resume'):
				self.PlayMedia(True)
			else:
				self.PlayMedia()
		elif controlId ==self.PLAYBEGBUTTON:
			self.PlayMedia()
		elif controlId == self.PLAYTRAILBUTTON:
			from . import window_trailer
			d=window_trailer.WindowTrailer(self.dbconn,self.listitem.getArt('fanart'),self.tvItem.trailers)
			d.doModal()
			del d
		elif controlId == self.MORELIKEBUTTON:
			from . import window_more
			d=window_more.WindowMore(self.dbconn,self.listitem,self.tvItem)
			d.doModal()
			del d
		elif controlId == self.CREDITSBUTTON:
			from . import window_credits
			d=window_credits.WindowCredits(self.dbconn,self.tvItem.credits_cast,self.tvItem.credits_crew,self.tvItem.videos,self.listitem.getUniqueID('tmdb'))
			d.doModal()
			del d
		elif controlId == self.EPISODEBUTTON:
			from . import window_tv_episodes
			d=window_tv_episodes.WindowTvEpisodes(self.dbconn,self.listitem,self.ratingicon,self.total_seasons_label,self.mySeasonprogress)
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
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("DROP TABLE IF EXISTS temp.series_progress")
		self.setControlProgress(self.PLAYPROGRESS,0)
		del self.tvItem
		super(WindowItemTv,self).close()
	
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

	def CreditsCast(self):
		castlist = []
		actors = eval(self.tvItem.credits_cast)
		for actor in actors:
			if actor.get('order') in range(0,5):
				castlist.append(actor.get('name'))
		return 'Cast: '+', '.join(castlist)

	def CreditsDirector(self):
		dirlist = []
		crew = eval(self.tvItem.credits_crew)
		for member in crew:
			if ("job","Director") in member.items():
				dirlist.append(member.get("name"))
		return 'Director: '+', '.join(dirlist)

	def Genres(self):
		return ', '.join([x.get('name') for x in eval(self.tvItem.genres)])


	def RatingButtonCtrl(self):
		if self.getControl(self.RATINGBUTTON).isVisible():
			for x in [(self.RATINGBUTTON,False),(self.ICON_RATINGBUTTON,False),(self.RATINGBUTTON_1,True),(self.ICON_RATINGBUTTON_1,True),(self.RATINGBUTTON_2,True),(self.ICON_RATINGBUTTON_2,True)]:
				self.setControlVisible(*x)
				self.setFocusId(self.RATINGBUTTON_1)
		else:
			for x in [(self.RATINGBUTTON,True),(self.ICON_RATINGBUTTON,True),(self.RATINGBUTTON_1,False),(self.ICON_RATINGBUTTON_1,False),(self.RATINGBUTTON_2,False),(self.ICON_RATINGBUTTON_2,False)]:
				self.setControlVisible(*x)


	def GetRating(self):
		if self.tvItem.rated == True:
			Icon = 'button-icon-thumbs-up.png'
			Label = 'Change Rating'
		elif self.tvItem.rated == False:
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
			c.execute("UPDATE user_list SET rated=?,rated_date=? WHERE tmdb_id=?",(vote,DateTimeNow(),self.listitem.getUniqueID('tmdb')))
			c.close()
			self.dbconn.conn.commit()
		self.tvItem = self.tvItem._replace(rated=vote)
		self.GetRating()
		self.RatingButtonCtrl()
		self.setControlLabel(self.RATINGBUTTON,self.thumbsRate.label)
		self.setControlImage(self.ICON_RATINGBUTTON,self.thumbsRate.icon)


	def SetPlayedInfo(self):
		if self.mySeasonprogress.inprogress:
			self.setControlProgress(self.PLAYPROGRESS,(100.00/(self.mySeasonprogress.runtime))*self.mySeasonprogress.inprogress)
			self.setControlLabel(self.PLAYBUTTON,'Resume Season {} Episode {}'.format(self.mySeasonprogress.season,self.mySeasonprogress.episode))
		else:
			self.setControlVisible(self.PLAYPROGRESS,False)
			self.setControlVisible(self.PLAYBEGGROUP,False)
			self.setControlLabel(self.PLAYBUTTON,'Play Season {} Episode {}'.format(self.mySeasonprogress.season,self.mySeasonprogress.episode))

	def GetMyListInfo(self):
		if self.tvItem.mylist == True:
			Label = 'Remove From MyList' 
			Icon = 'button-icon-minus.png'
		elif self.tvItem.mylist == False:
			Label = 'Add To MyList'
			Icon = 'button-icon-plus.png'
		else:
			Label = 'Add To MyList'
			Icon = 'button-icon-plus.png'
		self.myList = self.mylisttuple._make([Label,Icon])


	def SetMyListInfo(self):
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			if self.tvItem.mylist == True:
				added = False
			elif self.tvItem.mylist == False:
				added = True
			else:
				added = True
			c.execute("UPDATE tv_list SET user_list_added=?,user_list_added_date=? WHERE tmdb_id=?",(added,DateTimeNow(),self.listitem.getUniqueID('tmdb')))
		self.tvItem = self.tvItem._replace(mylist=added)
		self.GetMyListInfo()
		self.setControlLabel(self.MYLISTBUTTON,self.myList.label)
		self.setControlImage(self.ICON_MYLISTBUTTON,self.myList.icon)

	def TotalSeasons(self):
		if self.tvItem.total_seasons > 1:
			label = '{} Seasons'.format(self.tvItem.total_seasons)
		else:
			label = '1 Season'
		return label

	def GetTmdbInfo(self):
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT * FROM tv_episode_list WHERE tmdb_id=?",(self.tmdbid,))
			tveps = c.fetchall()
			for e in tveps:
				c.execute("SELECT EXISTS(SELECT 1 FROM master.tmdb_episode_details WHERE tmdb_id=? AND season_number=? AND episode_number=?)",(self.tmdbid,e[2],e[3]))
				f = c.fetchone()
				if f[0] == None or f[0] == 0:
					d = self.tmDB.tvepisodes(self.tmdbid,e[2],e[3])
					if d:
						still_path =self.ImagePath(d.get('still_path'))
						c.execute("INSERT OR IGNORE INTO master.tmdb_episode_details(tmdb_id,overview,still_path,air_date,title,vote_count,vote_average,episode_number,season_number) VALUES(?,?,?,?,?,?,?,?,?)",(self.tmdbid,d.get('overview'),still_path,dparser.parse(d.get('air_date')).date(),d.get('name'),d.get('vote_count'),d.get('vote_average'),d.get('episode_number'),d.get('season_number')))
			c.close()
			self.dbconn.conn.commit()

	def GetSeriesProgress(self):
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			try:
				c.execute("SELECT max( rowid ) FROM temp.series_progress")
				tablecheck =True
				rows = c.fetchone()[0]
			except OperationalError:
				tablecheck = False
				rows = 0
			if tablecheck:
				c.execute("SELECT tmdb_id,season,episode,inprogress,runtime,watched FROM user_watched_tv INTERSECT SELECT tmdb_id,season,episode,inprogress,runtime,watched FROM temp.series_progress ")
				if len(c.fetchall()) != rows:
					c.execute("DROP TABLE IF EXISTS temp.series_progress")
			c.execute("CREATE TABLE IF NOT EXISTS temp.series_progress(season INTEGER,episode INTEGER,inprogress INTEGER,runtime INTEGER,watched BOOLEAN,tmdb_id INTEGER, UNIQUE(season,episode))")
			c.execute("INSERT OR IGNORE INTO temp.series_progress(season,episode,inprogress,runtime,watched,tmdb_id) SELECT tel.season,tel.episode,uwt.inprogress,uwt.runtime,uwt.watched,uwt.tmdb_id FROM tv_episode_list tel INNER JOIN user_watched_tv uwt USING(tmdb_id,season,episode)  WHERE tel.tmdb_id=? ORDER BY tel.season DESC,tel.episode DESC",(self.tmdbid,))
			c.execute("SELECT rowid,season,episode,inprogress,runtime,watched FROM temp.series_progress WHERE inprogress IS NOT NULL OR watched=1")
			item = c.fetchone()
			if item:
				if item[5]:
					if item[0] > 1:
						c.execute("SELECT season,episode FROM temp.series_progress WHERE rowid=?",(item[0]-1,))
						season,episode = c.fetchone()
					else:
						season = item[1]
						episode = item[2]
					progress = None
					runtime = item[4]
				elif item[4]:
					rowid,season,episode,progress,runtime,watched = item
			else:
				c.execute("SELECT rowid,season,episode,inprogress,runtime FROM temp.series_progress WHERE rowid = ( SELECT max( rowid ) FROM temp.series_progress)")
				rowid,season,episode,progress,runtime = c.fetchone()
			self.mySeasonprogress = self.myseasonprogresstuple._make([season,episode,progress,runtime])

	def ImagePath(self,path,img_size='original'):
		if path:
			if path.startswith('/'):
				path = path.lstrip('/')
			if not img_size.endswith('/'):
				img_size = img_size+'/'
			path = urlparse.urljoin(urlparse.urljoin(self.artbase.path,'original/'),path)
			return urlparse.urlunparse((self.artbase.scheme,self.artbase.netloc,path,None,None,None))
		else:
			return None


	def PlayMedia(self,seek=False):
		li = xbmcgui.ListItem()
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT tmdb_id,overview,still_path,air_date,title,vote_count,vote_average,episode_number,season_number FROM master.tmdb_episode_details  WHERE tmdb_id=? AND episode_number=? AND season_number=? ",(self.tmdbid,self.mySeasonprogress.episode,self.mySeasonprogress.season))
			episode_details = c.fetchone()
			if episode_details:
				title = episode_details[4]
				li.setLabel(title)
				li.setArt({'poster':episode_details[2],'fanart':self.listitem.getArt('fanart')})
				li.setInfo('video',{'mediatype':'tvshow','plot':episode_details[1],'title':title,'episode':episode_details[7],'season':episode_details[8]})
				li.setProperties({'mediatype':self.mediatype,'season':self.mySeasonprogress.season,'episode':self.mySeasonprogress.episode})
				li.setUniqueIDs({'tmdb':self.tmdbid},'tmdb')
			c.execute("SELECT stream FROM tv_episode_list  WHERE tmdb_id=? AND episode=? AND season=? ",(self.tmdbid,self.mySeasonprogress.episode,self.mySeasonprogress.season))
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
				li.setPath(selected.item.getPath())
			else:
				li.setPath(streams[0])
		self.return_from_player = True
		if seek:
			media_player.PlayerCallBack(self.dbconn,li,seekpos=self.mySeasonprogress.inprogress)
		else:
			media_player.PlayerCallBack(self.dbconn,li)