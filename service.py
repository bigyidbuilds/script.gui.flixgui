#!/usr/bin/python
# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcaddon
import xbmcvfs
'''######------External Modules-----#####'''
import os
import sqlite3
import threading
'''#####-----Internal Modules-----#####'''


class main():
	
	def __init__(self):
		self.__addon__ = xbmcaddon.Addon('script.gui.flixgui')
		self.db = os.path.join(xbmcvfs.translatePath('special://database'),'{}.db'.format(self.__addon__.getAddonInfo('id')))


	def Run(self):
		self.threadevents = [self.DataBase,self.AddFolders]
		threads = [threading.Thread(target=threadevent) for threadevent in self.threadevents]
		for thread in threads:
			thread.start()
		for thread in threads:
			thread.join()

	def DataBase(self):
		masterconn = sqlite3.connect(self.db)
		with masterconn:
			c=masterconn.cursor()
			try:
				c.execute('SELECT major, minor, patch FROM version')
				(major, minor, patch) = c.fetchone()
				db_version = [major, minor, patch]
			except sqlite3.OperationalError:
				db_version = [0, 0, 0]
			if db_version < [0,0,1]:
				c.execute("CREATE TABLE IF NOT EXISTS version(major INTEGER, minor INTEGER, patch INTEGER)")
				c.execute("CREATE TABLE IF NOT EXISTS tmdb_movie_details(tmdb_id INTEGER, backdrop_path TEXT, overview TEXT, poster_path TEXT, release_date DATE, title TEXT, vote_count INTEGER, genres BLOB,vote_average INTEGER,media_type TEXT,age_rating TEXT,runtime INTEGER,credits_cast BLOB,credits_crew BLOB,videos BLOB, PRIMARY KEY(tmdb_id))")
				c.execute("CREATE TABLE IF NOT EXISTS tmdb_tv_details(tmdb_id INTEGER, backdrop_path TEXT, overview TEXT, poster_path TEXT, first_air_date DATE, title TEXT, vote_count INTEGER, genres BLOB,vote_average INTEGER,media_type TEXT,age_rating TEXT,credits_cast BLOB,credits_crew BLOB,videos BLOB,total_seasons INTEGER,PRIMARY KEY(tmdb_id))")
				c.execute("CREATE TABLE IF NOT EXISTS tmdb_episode_details(tmdb_id INTEGER, overview TEXT, still_path TEXT, air_date DATE, title TEXT, vote_count INTEGER,vote_average INTEGER,episode_number INTEGER,season_number INTEGER, PRIMARY KEY(tmdb_id,episode_number,season_number))")
				c.execute('INSERT INTO version(major, minor, patch) VALUES(0, 0, 1)')
				masterconn.commit()

	def AddFolders(self):
		xbmcvfs.mkdir(os.path.join(xbmcvfs.translatePath(self.__addon__.getAddonInfo('profile')),'temp'))

if __name__ == '__main__':
	m=main()
	m.Run()
