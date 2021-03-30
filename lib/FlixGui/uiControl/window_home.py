# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
'''######------External Modules-----#####'''
import random
'''#####-----Internal Modules-----#####'''
from ._actions import *
from FlixGui.modules._common import Log,DateTimeStrf
from FlixGui.modules import tmdbapi


class WindowHome(xbmcgui.WindowXML):

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
	MAINWINDOW           = 2000
	MAINWINDOW_1_LABEL   = 2101
	MAINWINDOW_1_LIST    = 2102
	MAINWINDOW_2_LABEL   = 2201
	MAINWINDOW_2_LIST    = 2202

	xmlFilename = 'Window_Home.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'


	def __new__(cls,dbconn,*args,**kwargs):
		return super(WindowHome, cls).__new__(cls,WindowHome.xmlFilename, WindowHome.scriptPath, WindowHome.defaultSkin, WindowHome.defaultRes)
		

	def __init__(self,dbconn,*args,**kwargs):
		super(WindowHome,self).__init__()		
		self.dbconn = dbconn
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT * FROM temp.caller")
			r=c.fetchone()
			self.tmdb_key =  r['tmdb_key']
		self.tmDB = tmdbapi.TmdbApi(self.tmdb_key)
		self.movieCats = self.SectionCats('master.tmdb_movie_details','movie_list')
		self.tvCats = self.SectionCats('master.tmdb_tv_details','tv_list')
		self.homelistpos = 0
		self.movielistpos = 0
		self.tvlistpos = 0
		self.viewitem = None
		self.viewselected = kwargs.get('viewselected',None)
		if self.viewselected:
			self.viewselected = (int(self.viewselected))
		self.sidectrlfocus = 0
		self.sidectrlindi = 0
		self.homeContent = self.HomeMenuContent()

  
		

	def onInit(self):
		self.control_list_1 = self.getControl(self.MAINWINDOW_1_LIST)
		self.control_list_2 = self.getControl(self.MAINWINDOW_2_LIST)
		if self.viewselected == self.SIDECTRLHOME or self.viewitem == 'home':
			self.LoadHomeMenu(self.homelistpos)
		elif self.viewselected == self.SIDECTRLSEARCH:
			self.LoadSearchMenu()
		elif self.viewselected == self.SIDECTRLMOVIE or self.viewitem == 'movie':
			self.LoadMovieMenu(self.movielistpos)
		elif self.viewselected == self.SIDECTRLTV or self.viewitem == 'tv':
			self.LoadTvMenu(self.tvlistpos)
		elif self.viewselected == self.SIDECTRLSETTING:
			self.LoadSettingMenu()
		elif self.viewselected == self.SIDECTRLMYLIST or self.viewitem == 'mylist':
			self.LoadMyList()
		else:
			self.LoadHomeMenu(self.homelistpos)


	def onAction(self,action):
		actionId = action.getId()
		focusId =  self.getFocusId()
		buttonId = action.getButtonCode()
		Log('onAction: {}'.format(actionId))
		if buttonId != 0:
			Log('onAction : {} keyboard call on {}'.format(actionId,buttonId))
		if actionId in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.LoadMenuSelect()
		elif actionId in [ACTION_UP]:
			if focusId == self.MAINWINDOW_1_LIST:
				if self.viewitem == 'home':
					v = (self.homelistpos-1)
					if v >= 0:
						self.LoadHomeMenu(v)
				elif self.viewitem == 'movie':
					v = (self.movielistpos-1)
					if v >= 0:
						self.LoadMovieMenu(v)
				elif self.viewitem == 'tv':
					v = (self.tvlistpos-1)
					if v >= 0:
						self.LoadTvMenu(v)
		elif actionId in [ACTION_DOWN]:
			if focusId == self.MAINWINDOW_1_LIST:
				if self.viewitem == 'home':
					v = (self.homelistpos+1)
					if v <= (len(self.homeContent)-1):
						self.LoadHomeMenu(v)
				elif self.viewitem == 'movie':
					v = (self.movielistpos+1)
					if v <= (len(self.movieCats)-1): 
						self.LoadMovieMenu(v)
				elif self.viewitem == 'tv':
					v = (self.tvlistpos+1)
					if v <=(len(self.tvCats)-1):
						self.LoadTvMenu(v)
		elif actionId in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if focusId == self.MAINWINDOW_1_LIST:
				listitem = self.getControl(focusId).getSelectedItem()
				if listitem.getProperty('mediatype') == 'movie':
					from . import window_item_movie
					d=window_item_movie.WindowItemMovie(self.dbconn,listitem)
					d.doModal()
					del d 
				elif listitem.getProperty('mediatype') == 'tvshow':
					from . import window_item_tv
					d=window_item_tv.WindowItemTv(self.dbconn,listitem)
					d.doModal()
					del d 

	def onClick(self,controlId):
		Log('onClick: {}'.format(controlId))
		

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
		Log('onFocus: {}'.format(controlId))
		if controlId in [ self.SIDECTRLHOME,self.SIDECTRLSEARCH,self.SIDECTRLMOVIE,self.SIDECTRLTV,self.SIDECTRLSETTING,self.SIDECTRLMYLIST]:
			self.LoadMenuSelect()
			

	def Close(self):
		self.dbconn.Close()
		# super(WindowHome,self).close()
		Log('closing window')
		xbmc.executebuiltin('ActivateWindow(home)')


	def setControlFadeLabel(self, controlId,label):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.addLabel(label)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return

	def setControlProgress(self,controlId,percent):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setPercent(percent)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return


	def setControlImage(self, controlId,image):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setImage(image)


	def setControlVisible(self, controlId, visible):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setVisible(visible)

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
		else:
			Log('controlId {} not recognized'.format(controlId))
			return

	def setSideCtrlIndi(self,required):
		for i in [self.SIDECTRLHOME_INDI,self.SIDECTRLSEARCH_INDI,self.SIDECTRLMOVIE_INDI,self.SIDECTRLTV_INDI,self.SIDECTRLSETTING_INDI,self.SIDECTRLMYLIST_INDI]:
			if i != required:
				self.setControlVisible(i,False)
		self.setControlVisible(required,True)
		self.sidectrlindi = required


	def LoadMenuSelect(self):
		from . import dialog_menu_select
		d=dialog_menu_select.DialogMenuSelect(self.dbconn,self.sidectrlfocus,self.sidectrlindi)
		d.doModal()
		if d.viewselected == self.SIDECTRLHOME:
			self.LoadHomeMenu(self.homelistpos)
		elif d.viewselected == self.SIDECTRLSEARCH:
			self.LoadSearchMenu()
		elif d.viewselected == self.SIDECTRLMOVIE:
			self.LoadMovieMenu(self.movielistpos)
		elif d.viewselected == self.SIDECTRLTV:
			self.LoadTvMenu(self.tvlistpos)
		elif d.viewselected == self.SIDECTRLSETTING:
			self.LoadSettingMenu()
		elif d.viewselected == self.SIDECTRLMYLIST:
			self.LoadMyList()
		elif not d.viewselected and d.exit:
			self.Close()
		elif d.backtolist:
			self.setFocusId(self.MAINWINDOW_1_LIST)
		else:
			self.LoadHomeMenu(0)
		del d 


	def LoadHomeMenu(self,listpos):
		self.sidectrlfocus = self.SIDECTRLHOME
		self.viewitem = 'home'
		self.homelistpos = listpos
		self.setSideCtrlIndi(self.SIDECTRLHOME_INDI)
		self.ControlListReset()
		label_1 = self.homeContent[listpos].get('name')
		content_1 = self.homeContent[listpos].get('content')
		if (len(self.homeContent)-1) >= (listpos+1):
			label_2 = self.homeContent[(listpos+1)].get('name')
			content_2 = self.homeContent[(listpos+1)].get('content')
		else:
			label_2 = None
			content_2 = None
		self.setControlLabel(self.MAINWINDOW_1_LABEL,label_1)
		self.control_list_1.addItems(content_1)
		if content_2 and label_2:
			self.control_list_2.addItems(content_2)
			self.setControlLabel(self.MAINWINDOW_2_LABEL,label_2)
		else:
			self.setControlLabel(self.MAINWINDOW_2_LABEL,'')
		self.setFocusId(self.MAINWINDOW_1_LIST)
		
		
		
		
	def LoadSearchMenu(self):
		self.setSideCtrlIndi(self.SIDECTRLSEARCH_INDI)
		from . import window_search
		d=window_search.WindowSearch(self.dbconn)
		d.doModal()
		del d

	def LoadMovieMenu(self,listpos):
		self.sidectrlfocus = self.SIDECTRLMOVIE
		self.movielistpos = listpos
		self.viewitem = 'movie'
		self.setSideCtrlIndi(self.SIDECTRLMOVIE_INDI)
		self.ControlListReset()
		genre_1 = self.movieCats[listpos].get('name')
		if (len(self.movieCats)-1) >= (listpos+1):
			genre_2 = self.movieCats[(listpos+1)].get('name')
		else:
			genre_2 = None
		self.setControlLabel(self.MAINWINDOW_1_LABEL,genre_1)
		with self.dbconn.conn:
			c = self.dbconn.conn.cursor()
			c.execute("SELECT * FROM master.tmdb_movie_details WHERE genres LIKE ? AND tmdb_id in (SELECT tmdb_id FROM movie_list)",('%'+genre_1+'%',))
			items = c.fetchall()
			for i in items:
				self.control_list_1.addItem(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],self.Genres(i[7]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
			if genre_2 != None:
				self.setControlLabel(self.MAINWINDOW_2_LABEL,genre_2)
				c.execute("SELECT * FROM master.tmdb_movie_details WHERE genres LIKE ? AND tmdb_id in (SELECT tmdb_id FROM movie_list)",('%'+genre_2+'%',))
				items = c.fetchall()
				for i in items:
					self.control_list_2.addItem(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],self.Genres(i[7]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
			else:
				self.setControlLabel(self.MAINWINDOW_2_LABEL,'')
		self.setFocusId(self.MAINWINDOW_1_LIST)


	def LoadTvMenu(self,listpos):
		self.sidectrlfocus = self.SIDECTRLTV
		self.tvlistpos = listpos
		self.viewitem = 'tv'
		self.setSideCtrlIndi(self.SIDECTRLTV_INDI)
		self.ControlListReset()
		genre_1 = self.tvCats[listpos].get('name')
		if (len(self.tvCats)-1) >= (listpos+1):
			genre_2 = self.tvCats[(listpos+1)].get('name')
		else:
			genre_2 = None
		self.setControlLabel(self.MAINWINDOW_1_LABEL,genre_1)
		with self.dbconn.conn:
			c = self.dbconn.conn.cursor()
			c.execute("SELECT * FROM tmdb_tv_details WHERE genres LIKE ? AND tmdb_id in (SELECT tmdb_id FROM tv_list)",('%'+genre_1+'%',))
			items = c.fetchall()
			for i in items:
				self.control_list_1.addItem(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],self.Genres(i[7]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
			if genre_2 != None:
				self.setControlLabel(self.MAINWINDOW_2_LABEL,genre_2)
				c.execute("SELECT * FROM tmdb_tv_details WHERE genres LIKE ? AND tmdb_id in (SELECT tmdb_id FROM tv_list)",('%'+genre_2+'%',))
				items = c.fetchall()
				for i in items:
					self.control_list_2.addItem(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],self.Genres(i[7]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
			else:
				self.setControlLabel(self.MAINWINDOW_2_LABEL,'')
		self.setFocusId(self.MAINWINDOW_1_LIST)

	def LoadSettingMenu(self):
		# self.setFocusId(self.SIDECTRLSETTING)
		self.setSideCtrlIndi(self.SIDECTRLSETTING_INDI)
		from . import window_settings
		d=window_settings.WindowSettings(self.dbconn)
		d.doModal()
		del d

	def LoadMyList(self):
		self.viewitem = 'mylist'
		self.sidectrlfocus = self.SIDECTRLMYLIST
		self.setSideCtrlIndi(self.SIDECTRLMYLIST_INDI)
		self.ControlListReset()
		self.setControlLabel(self.MAINWINDOW_1_LABEL,'MyList')
		self.setControlLabel(self.MAINWINDOW_2_LABEL,'')
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT tmd.title,tmd.poster_path,tmd.tmdb_id,tmd.overview,tmd.vote_average,tmd.vote_count,tmd.genres,tmd.release_date,tmd.media_type,tmd.age_rating,tmd.backdrop_path,user_list.mylist_date FROM tmdb_movie_details  tmd INNER JOIN movie_list USING(tmdb_id,media_type) INNER JOIN user_list USING(tmdb_id,media_type) WHERE user_list.mylist =1 UNION ALL SELECT ttd.title,ttd.poster_path,ttd.tmdb_id,ttd.overview,ttd.vote_average,ttd.vote_count,ttd.genres,ttd.first_air_date,ttd.media_type,ttd.age_rating,ttd.backdrop_path,user_list.mylist_date FROM tmdb_tv_details ttd INNER JOIN tv_list USING(tmdb_id,media_type) INNER JOIN user_list USING(tmdb_id,media_type) WHERE user_list.mylist =1 ORDER BY user_list.mylist_date")
			items = c.fetchall()
			if items:
				for title,poster_path,tmdb_id,overview,vote_average,vote_count,genres,release_date,media_type,age_rating,backdrop_path,added_date in items:
					self.control_list_1.addItem(self.ListItemBuilder(title,poster_path,backdrop_path,'tmdb',vote_average,vote_count,tmdb_id,overview,self.Genres(genres),DateTimeStrf(release_date,'%Y'),media_type,age_rating))
				self.setFocusId(self.MAINWINDOW_1_LIST)
			else:
				from . import dialog_response
				d=dialog_response.DialogResponse("You haven't added any Films or TV Shows to MyList","OK",posy=100)
				d.doModal()
				del d



	def SectionCats(self,detail_table,list_table):
		cat = []
		with self.dbconn.conn:
			c = self.dbconn.conn.cursor()
			sql = "SELECT genres FROM {} WHERE tmdb_id in (SELECT tmdb_id FROM {}) ".format(detail_table,list_table)
			c.execute(sql)
			for x in c.fetchall():
				for a in eval(x[0]):
					if a not in cat:
						cat.append(a)
		return cat


	def ListItemBuilder(self,title,poster,fanart,moviedb,votes,count,dbID,plot,genres,year,mediatype,age_rating):
		'''setInfo, genres single string or list of strings,year int,
		moviedb, "imdb"/"tvdb"/"tmdb"/"anidb"'''
		li= xbmcgui.ListItem(title)
		li.setArt({'poster':poster,'fanart':fanart})
		li.setRating(moviedb,votes,count,True)
		li.setUniqueIDs({moviedb:dbID},moviedb)
		li.setInfo('video', {'genre':genres,'year':year,'plot':plot,'title':title,'mediatype':mediatype})
		li.setProperties({'mediatype':mediatype,'moviedb':moviedb.upper(),'year':year,'age_rating':age_rating,'plot':plot,'genres':str(genres)})
		return li

	def ControlListReset(self):
		self.control_list_1.reset()
		self.control_list_2.reset()


	def HomeMenuContent(self):
		content = []
		litems = []
		with self.dbconn.conn:
			c = self.dbconn.conn.cursor()
			#recent added movies
			c.execute("SELECT md.tmdb_id,md.backdrop_path,md.overview,md.poster_path,md.release_date,md.title,md.vote_count,md.vote_average,ml.date_added,md.media_type,md.age_rating,md.genres FROM master.tmdb_movie_details md INNER JOIN movie_list ml USING(tmdb_id) ORDER BY date_added DESC LIMIT 10")
			items = c.fetchall()
			for i in items:
				litems.append(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[7],i[6],i[0],i[2],self.Genres(i[11]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
			items = litems[:]
			content.append({'name':'Recent Added Movies','content':items})
			del litems[:]
			#recent added tv
			c.execute("SELECT d.tmdb_id,d.backdrop_path,d.overview,d.poster_path,d.first_air_date,d.title,d.vote_count,d.vote_average,l.date_added,d.media_type,d.age_rating,d.genres FROM master.tmdb_tv_details d INNER JOIN tv_list l USING(tmdb_id) ORDER BY date_added DESC LIMIT 10")
			items = c.fetchall()
			for i in items:
				litems.append(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[7],i[6],i[0],i[2],self.Genres(i[11]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
			items = litems[:]
			content.append({'name':'Recent Added TV','content':items})
			del litems[:]
			#because you liked max last 4 likes used
			c.execute("SELECT tmdb_id,media_type,rated_date FROM user_list WHERE rated=1  ORDER BY rated_date DESC LIMIT 4")
			items = c.fetchall()
			for i in items:
				if i[1] == 'movie':
					c.execute("SELECT title FROM master.tmdb_movie_details WHERE tmdb_id=?",(i[0],))
					title = c.fetchone()[0]
					results = self.tmDB.movie(i[0],'Recommendations').get('results')
					for r in results:
						tmdbID = r.get('id')
						c.execute("SELECT * FROM master.tmdb_movie_details WHERE tmdb_id IN (SELECT tmdb_id FROM movie_list WHERE tmdb_id=?)",(tmdbID,))
						items = c.fetchall()
						for i in items:
							litems.append(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],self.Genres(i[7]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
				elif i[1] == 'tvshow':
					c.execute("SELECT title FROM master.tmdb_tv_details WHERE tmdb_id=?",(i[0],))
					title = c.fetchone()[0]
					results = self.tmDB.tv(i[0],'Recommendations').get('results')
					for r in results:
						tmdbID = r.get('id')
						c.execute("SELECT * FROM master.tmdb_tv_details WHERE tmdb_id IN (SELECT tmdb_id FROM tv_list WHERE tmdb_id=?)",(tmdbID,))
						items = c.fetchall()
						for i in items:
							litems.append(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],self.Genres(i[7]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
				items = litems[:]
				if len(items)>=1:
					content.append({'name':'Because you like {}'.format(title),'content':items})
				del litems[:]
			# popular by rating
			c.execute("SELECT tmdb_movie_details.title,tmdb_movie_details.poster_path,tmdb_movie_details.tmdb_id,tmdb_movie_details.overview,tmdb_movie_details.vote_average,tmdb_movie_details.vote_count,tmdb_movie_details.genres,tmdb_movie_details.release_date,tmdb_movie_details.media_type,tmdb_movie_details.age_rating,tmdb_movie_details.backdrop_path FROM master.tmdb_movie_details INNER JOIN movie_list USING(tmdb_id) UNION ALL SELECT tmdb_tv_details.title,tmdb_tv_details.poster_path,tmdb_tv_details.tmdb_id,tmdb_tv_details.overview,tmdb_tv_details.vote_average,tmdb_tv_details.vote_count,tmdb_tv_details.genres,tmdb_tv_details.first_air_date,tmdb_tv_details.media_type,tmdb_tv_details.age_rating,tmdb_tv_details.backdrop_path FROM master.tmdb_tv_details INNER JOIN tv_list USING(tmdb_id) ORDER BY vote_average DESC LIMIT 10")
			items = c.fetchall()
			for title,poster_path,tmdb_id,overview,vote_average,vote_count,genres,release_date,media_type,age_rating,backdrop_path in items:
				litems.append(self.ListItemBuilder(title,poster_path,backdrop_path,'tmdb',vote_average,vote_count,tmdb_id,overview,self.Genres(genres),DateTimeStrf(release_date,'%Y'),media_type,age_rating))
			items = litems[:]
			content.append({'name':'Popular','content':items})
			del litems[:]
			# trending
			results = self.tmDB.trending('all','day').get('results')
			for d in results:
				mediatype = d.get('media_type')
				if mediatype == 'movie':
					c.execute("SELECT * FROM master.tmdb_movie_details INNER JOIN movie_list USING(tmdb_id) WHERE tmdb_id=?",(d.get('id'),))
					i = c.fetchone()
					if i:
						litems.append(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],self.Genres(i[7]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
				elif mediatype == 'tv':
					c.execute("SELECT * FROM master.tmdb_tv_details INNER JOIN tv_list USING(tmdb_id) WHERE tmdb_id=?",(d.get('id'),))
					i = c.fetchone()
					if i:
						litems.append(self.ListItemBuilder(i[5],i[3],i[1],'tmdb',i[8],i[6],i[0],i[2],self.Genres(i[7]),DateTimeStrf(i[4],'%Y'),i[9],i[10]))
			items = litems[:]
			content.append({'name':'Trending','content':items})
			del litems[:]
			# continue watching
			c.execute("SELECT tmdb_movie_details.title,tmdb_movie_details.poster_path,tmdb_movie_details.tmdb_id,tmdb_movie_details.overview,tmdb_movie_details.vote_average,tmdb_movie_details.vote_count,tmdb_movie_details.genres,tmdb_movie_details.release_date,tmdb_movie_details.media_type,tmdb_movie_details.age_rating,tmdb_movie_details.backdrop_path,user_watched_movie.inprogress FROM master.tmdb_movie_details INNER JOIN movie_list USING(tmdb_id) INNER JOIN user_watched_movie USING(tmdb_id) WHERE user_watched_movie.inprogress IS NOT NULL ")
			items = c.fetchall()
			if items:
				for title,poster_path,tmdb_id,overview,vote_average,vote_count,genres,release_date,media_type,age_rating,backdrop_path,progress in items:
					litems.append(self.ListItemBuilder(title,poster_path,backdrop_path,'tmdb',vote_average,vote_count,tmdb_id,overview,self.Genres(genres),DateTimeStrf(release_date,'%Y'),media_type,age_rating))
				items = litems[:]
				content.append({'name':'Continue Watching','content':items})
				del litems[:]
			random.shuffle(content)

		return content

	def Genres(self,strlist):
		return ', '.join([x.get('name') for x in eval(strlist)])