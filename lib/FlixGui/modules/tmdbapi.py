#!/usr/bin/python
# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''

'''######------External Modules-----#####'''
import requests
from urllib import parse as urlparse
'''#####-----Internal Modules-----#####'''
from ._common import Log


class TmdbApi():

	scheme = 'https'
	netloc = 'api.themoviedb.org'
	api_verison = 3

	def __init__(self,api_key):
		self.session = requests.Session() 
		self.session.params.update({'api_key':api_key})

	def configuration(self,func):
		self.path = '{}/configuration'.format(self.api_verison)
		self.url  = urlparse.urlunparse((self.scheme,self.netloc,self.path,None,None,None))

		def APIConfiguration():
			r = self.session.get(self.url)
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data

		return eval(func)()

	def genres(self,func):
		self.path = '{}/genre'.format(self.api_verison)
		self.url  = urlparse.urlunparse((self.scheme,self.netloc,self.path,None,None,None))

		def Movie():
			urL = self.url+'/movie/list'
			r = self.session.get(urL)
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data

		return eval(func)()

	def movie(self,iD,func,*args,**kwargs):
		self.page = kwargs.get('page',1)
		self.append_to_response = kwargs.get('append_to_response')
		self.path = '{}/movie/{}'.format(self.api_verison,iD)
		self.url  = urlparse.urlunparse((self.scheme,self.netloc,self.path,None,None,None))

		def Details():
			if self.append_to_response:
				r = self.session.get(self.url,params={'append_to_response':self.append_to_response})
			else:
				r = self.session.get(self.url)
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data

		def Recommendations():
			url = self.url+'/recommendations'
			r = self.session.get(url,params={'page':self.page})
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data

		def Similar():
			url = self.url+'/similar'
			r = self.session.get(url,params={'page':self.page})
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data
					
		return eval(func)()

	def search(self,query,func,*args,**kwargs):
		self.query = query
		self.page = kwargs.get('page',1)
		self.language = kwargs.get('language','en-US')
		self.path = '{}/search'.format(self.api_verison)
		self.url  = urlparse.urlunparse((self.scheme,self.netloc,self.path,None,None,None))

		def Multi():
			url = self.url+'/multi'
			r = self.session.get(url,params={'page':self.page,'language':self.language,'query':self.query})
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data

		def Tv():
			url = self.url+'/tv'
			r = self.session.get(url,params={'page':self.page,'language':self.language,'query':self.query})
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data

		return eval(func)()

	def trending(self,media_type,time_window):
		"""
		media_type: all,movie,tv,person
		time_window: day,week
		"""
		self.path = '{}/trending/{}/{}'.format(self.api_verison,media_type,time_window)
		self.url  = urlparse.urlunparse((self.scheme,self.netloc,self.path,None,None,None))
		r = self.session.get(self.url)
		if r.ok:
			content_type = r.headers.get('Content-Type')
			if 'application/json' in content_type:
				data=r.json()
				return data 
				

	def tv(self,iD,func,*args,**kwargs):
		self.page = kwargs.get('page',1)
		self.append_to_response = kwargs.get('append_to_response')
		self.path = '{}/tv/{}'.format(self.api_verison,iD)
		self.url  = urlparse.urlunparse((self.scheme,self.netloc,self.path,None,None,None))

		def Details():
			if self.append_to_response:
				r = self.session.get(self.url,params={'append_to_response':self.append_to_response})
			else:
				r = self.session.get(self.url)
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data 

		def Recommendations():
			url = self.url+'/recommendations'
			r = self.session.get(url,params={'page':self.page})
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data

		def Similar():
			url = self.url+'/similar'
			r = self.session.get(url,params={'page':self.page})
			if r.ok:
				content_type = r.headers.get('Content-Type')
				if 'application/json' in content_type:
					data=r.json()
					return data

		return eval(func)()

	def tvepisodes(self,iD,season,episode):
		self.path = '{}/tv/{}/season/{}/episode/{}'.format(self.api_verison,iD,season,episode)
		self.url  = urlparse.urlunparse((self.scheme,self.netloc,self.path,None,None,None))
		r = self.session.get(self.url)
		if r.ok:
			content_type = r.headers.get('Content-Type')
			if 'application/json' in content_type:
				data=r.json()
				return data 



