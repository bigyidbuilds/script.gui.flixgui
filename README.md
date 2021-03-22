# script.gui.flixgui

A Script to allow a Kodi addon to be viewed in a layout similar to NetFlix, Addon creator can create a addon that then passes their content via a database to the script

The script has also has it's own database for caching of TMDB Meta data which is shared with all callers of the script 


## Requirements of the Caller Addon to the script

* TMDB API _Used for the collection of media meta data_
	* TMDB Details key obtainable from https://www.themoviedb.org/settings/api
	* A api Key is required

*  YouTube API _YouTube is used for the playing of media trailers_
	* Youtube details https://developers.google.com/youtube/v3/getting-started
	* A api Key is required
	* A client Id is required
	* A client Secret is required

