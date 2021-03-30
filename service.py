#!/usr/bin/python
# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmc 
import xbmcaddon
import xbmcvfs
'''######------External Modules-----#####'''
import os
'''#####-----Internal Modules-----#####'''
xbmc.executebuiltin('RunScript({})'.format(os.path.join(xbmcvfs.translatePath(xbmcaddon.Addon('script.gui.flixgui').getAddonInfo('path')),'scripts','database.py')))
