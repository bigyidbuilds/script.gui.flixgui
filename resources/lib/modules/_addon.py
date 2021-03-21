#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import xbmc
import xbmcaddon
import xbmcvfs



script          = xbmcaddon.Addon('script.gui.flixgui')
scriptinfo      = script.getAddonInfo
setting         = script.getSetting
setting_true    = lambda x: bool(True if setting(str(x)) == "true" else False)
setting_set     = script.setSetting
local_str       = script.getLocalizedString
has_addon       = lambda x: xbmc.getCondVisibility("System.HasAddon({addon})".format(addon=str(x)))



script_version   = scriptinfo('version')
script_name      = scriptinfo('name')
script_id        = scriptinfo('id')
script_icon      = scriptinfo("icon")
script_fanart    = scriptinfo("fanart")
script_path      = xbmcvfs.translatePath(scriptinfo('path'))
script_profile   = xbmcvfs.translatePath(scriptinfo('profile'))


# XBMC USERDATA FOLDERS
UD_DATABASE = xbmcvfs.translatePath('special://database')

#ADDON FOLDERS
RESOURCES_FOLDER     = os.path.join(script_path,'resources')
MEDIA_FOLDER         = os.path.join(RESOURCES_FOLDER,'media')
AGE_RATE_ICON_FOLDER = os.path.join(MEDIA_FOLDER,'age_rating_icons')


#FILES
CACHEDB       = os.path.join(UD_DATABASE,'script.gui.flixgui.db')
