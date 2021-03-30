#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmc
import xbmcaddon
'''######------External Modules-----#####'''
from dateutil import parser as dparser
from urllib   import parse  as urlparse
'''#####-----Internal Modules-----#####'''
from . import tmdbapi
from ._common import Log


class MetaCache(object):

	def __init__(self,dbconn,apikey,addon_id):
		self.addon_id = addon_id
		self.dbconn = dbconn
		self.tmdbapi = tmdbapi.TmdbApi(apikey)
		self.artbase = urlparse.urlparse(self.tmdbapi.configuration('APIConfiguration').get('images').get('base_url'))

	def MovieMeta(self,tmdb_id):
		d = self.tmdbapi.movie(tmdb_id,'Details',append_to_response='release_dates,credits,videos')
		if d:
			credits = d.get('credits')
			release_dates_results = d.get('release_dates').get('results')
			backdrop_path = self.ImagePath(d.get('backdrop_path'))
			poster_path = self.ImagePath(d.get('poster_path'))
			try :
				release_date = dparser.parse(d.get('release_date')).date()
			except:
				release_date = None
			age_rating = None
			for release_dates_result in release_dates_results:
				if ("iso_3166_1",xbmcaddon.Addon(self.addon_id).getSetting("general.region")) in release_dates_result.items():
					rd = release_dates_result.get("release_dates")
					for r in rd:
						age_rating = r.get('certification',None)
						if not release_date:
							try:
								release_date = dparser.parse(r.get('release_date')).date()
							except:
								release_date = dparser.parse('1900-01-01').date()
						if age_rating:
							break


			with self.dbconn.conn: 
				self.dbconn.conn.execute("INSERT OR IGNORE INTO master.tmdb_movie_details(tmdb_id, backdrop_path, overview, poster_path , release_date , title , vote_count , genres ,vote_average ,media_type,age_rating,runtime,credits_cast,credits_crew,videos) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(tmdb_id,backdrop_path,d.get('overview'),poster_path,release_date,d.get('title'),d.get('vote_count'),str(d.get('genres')),d.get('vote_average'),'movie',age_rating,d.get("runtime"),str(credits.get('cast')),str(credits.get('crew')),str(d.get('videos').get('results'))))
				self.dbconn.conn.commit()

	def TvMeta(self,tmdb_id):
		d = self.tmdbapi.tv(tmdb_id,'Details',append_to_response='videos,content_ratings,credits')
		if d:
			content_ratings = list(filter(lambda r: r["iso_3166_1"] == xbmcaddon.Addon(self.addon_id).getSetting("general.region"), d.get('content_ratings').get('results')))
			credits = d.get('credits')
			if len(content_ratings) >=1:
				content_rating = content_ratings[0].get('rating')
			else:
				content_rating = ''
			try:
				first_air_date = dparser.parse(d.get('first_air_date')).date()
			except:
				first_air_date = dparser.parse('1900-01-01').date()
			backdrop_path = self.ImagePath(d.get('backdrop_path'))
			poster_path = self.ImagePath(d.get('poster_path'))
			with self.dbconn.conn:
				self.dbconn.conn.execute("INSERT OR IGNORE INTO master.tmdb_tv_details(tmdb_id, backdrop_path, overview, poster_path, first_air_date, title, vote_count, genres,vote_average ,media_type,total_seasons,videos,age_rating,credits_cast,credits_crew) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(tmdb_id,backdrop_path,d.get('overview'),poster_path,first_air_date,d.get('name'),d.get('vote_count'),str(d.get('genres')),d.get('vote_average'),'tvshow',d.get('number_of_seasons'),str(d.get('videos').get('results')),content_rating,str(credits.get('cast')),str(credits.get('crew'))))
				self.dbconn.conn.commit()


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

