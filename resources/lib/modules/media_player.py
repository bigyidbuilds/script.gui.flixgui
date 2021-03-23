#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmc
'''######------External Modules-----#####'''
from collections import namedtuple
import math
import sqlite3
'''#####-----Internal Modules-----#####'''
from modules._common import Log,DateTimeNow

class PlayerCallBack():

	def __init__(self,dbconn,listitem,*args,**kwargs):
		seekpos = kwargs.get('seekpos')
		self.PM = PlayerMonitour()
		self.PM.PlayStream(listitem,dbconn,seekpos)
		while(not xbmc.Monitor().abortRequested() or not self.PM.CallBack.stopped  or  not self.PM.CallBack.ended ):
			xbmc.sleep(500)
		del self.PM


class PlayerMonitour(xbmc.Player):

	CallBack = None

	def __init__(self,*args,**kwargs):
		xbmc.Player.__init__(self)
		self.callback = namedtuple('CallBack','started,stopped,ended,error,paused,inprogress,watched,watched_date,runtime')
		self.CallBack = self.callback._make([False,False,False,False,False,None,None,None,None])
		self.playedtime = 0
		self.totaltime = 0
		self.dbconn = None
		self.listitem = None


	def onAVStarted(self):
		if not self.CallBack.started:
			Log('onAVStarted')
			self.totaltime = math.floor(self.getTotalTime())
			self.CallBack = self.CallBack._replace(started=True,runtime=self.totaltime)
			if self.seekpos:
				self.seekTime(self.seekpos)
			self.PlayedTime()


	def onPlayBackEnded(self):
		if not self.CallBack.ended:
			Log('onPlayBackEnded')
			self.CallBack = self.CallBack._replace(ended=True,watched=True,watched_date=DateTimeNow(),inprogress=0,runtime=self.totaltime)
			self.Update()


	def onPlayBackStopped(self):
		if not self.CallBack.stopped:
			Log('onPlayBackStopped')
			self.CallBack = self.CallBack._replace(stopped=True,inprogress=self.playedtime,runtime=self.totaltime)
			self.Update()


	def onPlayBackError(self):
		if not self.CallBack.error:
			Log('onPlayBackError')

	def onPlayBackPaused(self):
		Log('onPlayBackPaused')
		self.CallBack = self.CallBack._replace(paused=True,inprogress=self.playedtime,runtime=self.totaltime)

	def PlayStream(self,listitem,dbconn,seekpos):
		self.listitem = listitem
		self.dbconn = dbconn
		self.seekpos = seekpos
		streamurl = self.listitem.getPath()
		import resolveurl
		host = resolveurl.HostedMediaFile(streamurl)
		if host:
			Log('stream been resolved by resolveurl')
			streamurl = resolveurl.resolve(streamurl)
		else:
			Log('Stream not resolvable by resolveurl')
		Log('Attemping to play stream')
		self.play(streamurl,self.listitem)

			
		


	def PlayedTime(self):
		try:
			while self.isPlaying():
				self.playedtime = self.getTime()
		except:
			pass



	def Update(self):
		with self.dbconn.conn:
			c = self.dbconn.conn.cursor()
			if self.listitem.getProperty('mediatype') == 'movie':
				c.execute("UPDATE user_watched_movie SET inprogress=?,watched=?,watched_date=?,runtime=? WHERE tmdb_id=?",(math.floor(self.CallBack.inprogress),self.CallBack.watched,self.CallBack.watched_date,self.CallBack.runtime,self.listitem.getUniqueID('tmdb')))
			elif self.listitem.getProperty('mediatype') == 'tvshow':
				c.execute("UPDATE user_watched_tv SET inprogress=?,watched=?,watched_date=?,runtime=? WHERE tmdb_id=? AND season=? AND episode=?",(math.floor(self.CallBack.inprogress),self.CallBack.watched,self.CallBack.watched_date,self.CallBack.runtime,self.listitem.getUniqueID('tmdb'),self.listitem.getProperty('season'),self.listitem.getProperty('episode')))
			try:
				self.dbconn.conn.commit()
			except:
				pass

				
