#!/usr/bin/python
# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''

'''######------External Modules-----#####'''
import datetime
import sqlite3
import threading

'''#####-----Internal Modules-----#####'''
from modules._addon import CACHEDB
from modules._common import FromTimeStamp,Log,ToTimeStamp,DateTimeNow,DateTimeObject,DateTimeStrf




class DatabaseConnection(object):
	
	def __init__(self,db):
		sqlite3.register_adapter(datetime.datetime, ToTimeStamp)
		sqlite3.register_converter("TIMESTAMP", FromTimeStamp)
		sqlite3.register_adapter(datetime.date, DateTimeStrf)
		sqlite3.register_converter("DATE", DateTimeObject)
		sqlite3.register_adapter(bool, int)
		sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
		self.lock = threading.Lock()
		self.conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread=False)
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str
		sql = "ATTACH DATABASE '{}' AS master".format(CACHEDB)
		self.conn.execute(sql)

	def Close(self):
		self.conn.close()


	def Create(self):
		with self.conn:
			c = self.conn.cursor()
			try:
				c.execute('SELECT major, minor, patch FROM db_version')
				(major, minor, patch) = c.fetchone()
				db_version = [major, minor, patch]
			except sqlite3.OperationalError:
				db_version = [0, 0, 0]
			if db_version < [0,0,1]:
				c.execute("CREATE TABLE IF NOT EXISTS last_cache_time(last_cache_time TIMESTAMP)")
				c.execute("CREATE TABLE IF NOT EXISTS db_version(major INTEGER, minor INTEGER, patch INTEGER)")
				c.execute("CREATE TABLE IF NOT EXISTS movie_list(title TEXT,tmdb_id INTEGER,genre BLOB, overview TEXT, poster_path TEXT,backdrop_path TEXT,release_date TIMESTAMP,stream TEXT,date_added TIMESTAMP,media_type DEFAULT 'movie' NOT NULL,PRIMARY KEY(tmdb_id))")
				c.execute("CREATE TABLE IF NOT EXISTS tv_list(title TEXT,tmdb_id INTEGER,genre BLOB, overview TEXT, poster_path TEXT,backdrop_path TEXT,release_date TIMESTAMP,episodes BLOB,date_added TIMESTAMP,media_type TEXT DEFAULT 'tvshow' NOT NULL ,PRIMARY KEY(tmdb_id))")
				c.execute("CREATE TABLE IF NOT EXISTS tv_episode_list(tmdb_id INTEGER REFERENCES tv_list(tmdb_id) ON DELETE CASCADE ,title TEXT,season INTEGER,episode INTEGER,stream BLOB,PRIMARY KEY(tmdb_id,season,episode))")
				c.execute("CREATE TABLE IF NOT EXISTS user_watched_tv(tmdb_id INTEGER,season INTEGER,episode INTEGER,inprogress INTEGER,watched BOOLEAN,watched_date TIMESTAMP,runtime INTEGER, PRIMARY KEY(tmdb_id,season,episode))")
				c.execute("CREATE TABLE IF NOT EXISTS user_watched_movie(tmdb_id INTEGER,inprogress INTEGER,watched BOOLEAN,watched_date TIMESTAMP,runtime INTEGER, PRIMARY KEY(tmdb_id))")
				c.execute("CREATE TABLE IF NOT EXISTS user_list(tmdb_id INTEGER,media_type TEXT,rated BOOLEAN,rated_date TIMESTAMP,mylist BOOLEAN,mylist_date TIMESTAMP,PRIMARY KEY(tmdb_id,media_type))")
				c.execute('INSERT INTO db_version(major, minor, patch) VALUES(0, 0, 1)')
				c.execute("INSERT INTO last_cache_time(last_cache_time) VALUES(?)",(DateTimeNow(),))
				self.conn.commit()
			c.execute("CREATE TABLE IF NOT EXISTS temp.caller(addon_id TEXT,tmdb_key TEXT,tmdb_user TEXT,tmdb_password TEXT,youtubeapi_key TEXT,youtubeapi_clientid TEXT,youtubeapi_clientsecret TEXT, PRIMARY KEY(addon_id))")
			c.execute("SELECT name FROM sqlite_master WHERE type=?",('table',))
			tables = [x[0] for x in c.fetchall()]
			rowheaders = map(lambda x: x[1],c.execute("PRAGMA table_info(last_cache_time)"))
			to_add = list(set(tables) - set(rowheaders))
			if len(to_add) >=1:
				for t in to_add:
					c.execute("ALTER TABLE last_cache_time ADD COLUMN {} TIMESTAMP DEFAULT 0".format(t))
				self.conn.commit()
