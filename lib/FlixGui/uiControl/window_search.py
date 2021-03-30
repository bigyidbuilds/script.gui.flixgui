# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcaddon
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''
import difflib
import sqlite3
import os
import string

'''#####-----Internal Modules-----#####'''
from ._actions import *
from FlixGui.modules._common import Log,DateTimeStrf
from FlixGui.modules import tmdbapi




class WindowSearch(xbmcgui.WindowXML):

	SIDECTRLWINDOW       = 1000
	SIDECTRLGROUP        = 1001
	SIDECTRLHOME         = 1002
	SIDECTRLSEARCH       = 1003
	SIDECTRLSEARCH_INDI  = 10031
	SIDECTRLMOVIE        = 1004
	SIDECTRLTV           = 1005
	SIDECTRLSETTING      = 1006
	SIDECTRLMYLIST       = 1007
	KEYBOARDGROUP        = 2000
	KEYBOARD_TOP_ROW     = 2100
	KEYBOARD_KEYS        = 2200
	SEARCH_QUERY         = 3001
	QUERY_RESULTS_LIST   = 4000
	PREDICT_QUERY_LIST   = 5000


	xmlFilename = 'Window_Search.xml'
	scriptPath  = xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path'))
	defaultSkin = 'Default'
	defaultRes  = '720p'

	def __new__(cls,dbconn,*args,**kwargs):
		return super(WindowSearch, cls).__new__(cls,WindowSearch.xmlFilename, WindowSearch.scriptPath, WindowSearch.defaultSkin, WindowSearch.defaultRes)
		

	def __init__(self,dbconn,*args,**kwargs):
		super(WindowSearch,self).__init__()
		self.dbconn = dbconn
		with self.dbconn.conn:
			c=self.dbconn.conn.cursor()
			c.execute("SELECT * FROM temp.caller")
			r=c.fetchone()
			self.tmdb_key =  r['tmdb_key']
		self.mediaFolder = os.path.join(self.scriptPath,'resources','skins',self.defaultSkin,'media')
		self.kb = [{'label':'spacebar','image':os.path.join(self.mediaFolder,'space-bar.png')},{'label':'backspace','image':os.path.join(self.mediaFolder,'backspace.png')}]
		self.querystring = ''
		with self.dbconn.conn:
			c = self.dbconn.conn.cursor()
			c.execute("SELECT tmdb_movie_details.title,tmdb_movie_details.poster_path,tmdb_movie_details.tmdb_id,tmdb_movie_details.media_type,tmdb_movie_details.backdrop_path,tmdb_movie_details.overview,tmdb_movie_details.release_date,tmdb_movie_details.age_rating,tmdb_movie_details.vote_average,tmdb_movie_details.vote_count,tmdb_movie_details.genres FROM master.tmdb_movie_details INNER JOIN movie_list USING(tmdb_id) UNION ALL SELECT tmdb_tv_details.title,tmdb_tv_details.poster_path,tmdb_tv_details.tmdb_id,tmdb_tv_details.media_type,tmdb_tv_details.backdrop_path,tmdb_tv_details.overview,tmdb_tv_details.first_air_date,tmdb_tv_details.age_rating,tmdb_tv_details.vote_average,tmdb_tv_details.vote_count,tmdb_tv_details.genres FROM master.tmdb_tv_details INNER JOIN tv_list USING(tmdb_id)")
			self.allcontent = c.fetchall()
		self.seqmatcher = difflib.SequenceMatcher(None)
		self.tmDB = tmdbapi.TmdbApi(self.tmdb_key)

	def onInit(self):
		# self.setSideCtrlIndi(self.SIDECTRLSEARCH_INDI)
		self.getControl(self.KEYBOARD_KEYS).reset()
		for k in self.kb:
			li = xbmcgui.ListItem(k.get('label'))
			li.setArt({'icon':k.get('image')})
			self.getControl(self.KEYBOARD_TOP_ROW).addItem(li)
		for i in list(string.ascii_lowercase)+list(('1','2','3','4','5','6','7','8','9','0')):
			li = xbmcgui.ListItem(i)
			self.getControl(self.KEYBOARD_KEYS).addItem(li)
		self.setFocusId(self.KEYBOARD_KEYS)


	def onAction(self,action):
		buttonId = action.getButtonCode()
		actionId = action.getId()
		Log('onAction: {}'.format(action.getId()))
		if buttonId != 0:
			Log('onAction : {} keyboard call on {}'.format(actionId,buttonId))
		if actionId in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			focused = self.getFocusId()
			if focused in [self.KEYBOARD_KEYS,self.KEYBOARD_TOP_ROW]:
				self.QueryString(self.getControl(focused).getSelectedItem())
				self.DisplayQuery()
				self.DisplayQueryResults()
				self.DisplayPredictive()
			elif focused == self.QUERY_RESULTS_LIST:
				listitem = self.getControl(focused).getSelectedItem()
				if listitem.getProperty('media_type') == 'movie':
					from . import window_item_movie
					d=window_item_movie.WindowItemMovie(self.dbconn,listitem)
					d.doModal()
					del d
				elif listitem.getProperty('media_type') == 'tv':
					from . import window_item_tv
					d=window_item_tv.WindowItemTv(self.dbconn,listitem)
					d.doModal()
					del d
			elif focused == self.PREDICT_QUERY_LIST:
				listitem = self.getControl(focused).getSelectedItem()
				self.ShowPredicResults(listitem)




	def onClick(self,controlId):
		Log('onClick: {}'.format(controlId))


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
		if controlId in [ self.SIDECTRLHOME,self.SIDECTRLSEARCH,self.SIDECTRLMOVIE,self.SIDECTRLTV,self.SIDECTRLSETTING]:
			from . import dialog_menu_select
			d=dialog_menu_select.DialogMenuSelect(self.dbconn,self.SIDECTRLSEARCH,self.SIDECTRLSEARCH_INDI)
			d.doModal()
			if d.viewselected:
				from . import window_home
				d=window_home.WindowHome(self.dbconn,viewselected=d.viewselected)
				d.doModal()
				del d
			elif not d.viewselected and d.exit:
				self.Close()
			elif d.backtolist:
				self.setFocusId(self.KEYBOARD_KEYS)
			del d
		elif controlId in [self.KEYBOARD_KEYS,self.KEYBOARD_TOP_ROW] and self.getControl(self.SEARCH_QUERY).getLabel().startswith('Similar to'):
			self.setControlLabel(self.SEARCH_QUERY,self.querystring)


	def Close(self):
		# super(WindowSearch,self).close()
		self.dbconn.Close()
		xbmc.executebuiltin('ActivateWindow(home)')

	def setControlVisible(self, controlId, visible):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setVisible(visible)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return

	def setControlLabel(self, controlId, label):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setLabel(label)

	# def setSideCtrlIndi(self,required):
	# 	for i in [self.SIDECTRLHOME_INDI,self.SIDECTRLSEARCH_INDI,self.SIDECTRLMOVIE_INDI,self.SIDECTRLTV_INDI,self.SIDECTRLSETTING_INDI]:
	# 		if i != required:
	# 			self.setControlVisible(i,False)
	# 	self.setControlVisible(required,True)


	def QueryString(self,listitem):
		kbinput = listitem.getLabel()
		if kbinput == 'spacebar':
			self.querystring += ' '
		elif kbinput == 'backspace':
			self.querystring = (self.querystring[:-1])
		else:
			self.querystring += kbinput


	def DisplayQuery(self):
		self.setControlLabel(self.SEARCH_QUERY,self.querystring)


	def DisplayQueryResults(self):
		queryresultlist = self.getControl(self.QUERY_RESULTS_LIST)
		queryresultlist.reset()
		queryresults = []
		self.seqmatcher.set_seq1(self.querystring)
		for title,poster_path,tmdb_id,media_type,backdrop_path,overview,release_date,age_rating,vote_avg,votes,genres in self.allcontent:
			if self.querystring in title.lower():
				self.seqmatcher.set_seq2(title)
				r = self.seqmatcher.ratio()
				queryresults.append({'title':title,'poster_path':poster_path,'tmdb_id':tmdb_id,'r':r,'media_type':media_type,'backdrop_path':backdrop_path,'overview':overview,'year':DateTimeStrf(release_date,'%Y'),'age_rating':age_rating,'vote_avg':vote_avg,'votes':votes,'genres':genres})
		queryresults = sorted(queryresults,key=lambda k: k['r'],reverse=True)
		if len(queryresults)>100:
			queryresults = queryresults[:100]
		for qr in queryresults:
			queryresultlist.addItem(self.ListItemBuilder(qr.get('title'),qr.get('poster_path'),qr.get('backdrop_path'),'tmdb',qr.get('vote_avg'),qr.get('votes'),qr.get('tmdb_id'),qr.get('overview'),qr.get('genres'),qr.get('year'),qr.get('media_type'),qr.get('age_rating')))


	def DisplayPredictive(self):
		predictlist = self.getControl(self.PREDICT_QUERY_LIST)
		predictlist.reset()
		if len(self.querystring) >= 3:
			items = self.tmDB.search(self.querystring,'Multi').get('results')
			for i in items:
				media_type = i.get("media_type")
				if media_type == 'movie':
					title = i.get('original_title')
				elif media_type == 'tv':
					media_type = 'tvshow'
					title = i.get('original_name')
				elif media_type == 'person':
					title = i.get('name')
				li = xbmcgui.ListItem(title)
				li.setUniqueIDs({'tmdb':i.get('id')},'tmdb')
				li.setProperty('media_type',media_type)
				predictlist.addItem(li)


	def ShowPredicResults(self,listitem):
		queryresultlist = self.getControl(self.QUERY_RESULTS_LIST)
		queryresultlist.reset()
		mediatype = listitem.getProperty('media_type')
		tmdbid = int(listitem.getUniqueID('tmdb'))
		Log(mediatype)
		for title,poster_path,tmdb_id,media_type,backdrop_path,overview,release_date,age_rating,vote_avg,votes,genres in self.allcontent:
			if tmdb_id == tmdbid and mediatype == media_type:
				queryresultlist.addItem(self.ListItemBuilder(title,poster_path,backdrop_path,'tmdb',vote_avg,votes,tmdb_id,overview,genres,DateTimeStrf(release_date,'%Y'),media_type,age_rating))
		if mediatype == 'movie':
			results = self.tmDB.movie(tmdbid,'Similar').get('results')
		elif mediatype == 'tvshow':
			results = self.tmDB.tv(tmdbid,'Similar').get('results')
		else:
			results = []
		for title,poster_path,tmdb_id,media_type,backdrop_path,overview,release_date,age_rating,vote_avg,votes,genres in self.allcontent:
			for i in results:
				if tmdb_id == int(i.get('id')) and media_type == mediatype:
					queryresultlist.addItem(self.ListItemBuilder(title,poster_path,backdrop_path,'tmdb',vote_avg,votes,tmdb_id,overview,genres,DateTimeStrf(release_date,'%Y'),media_type,age_rating))
		self.setControlLabel(self.SEARCH_QUERY,'Similar to {}'.format(listitem.getLabel()))






		
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


