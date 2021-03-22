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


* Settings XML file _min items required for settings these are also used in the script_
```
	<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
	<settings version="1">
		<section id="plugin.video.bybexample">
			<category id="general" label="32000" help="">
				<group id="1" label="32001">
					<setting id="general.debug" type="boolean" label="32002" help="">
						<level>0</level>
						<default>false</default>
						<control type="toggle"/>
					</setting>
					<setting id="general.region" label="32003" type="string">
						<level>0</level>
						<default>GB</default>
						<constraints>
							<options>
								<option label="32004">GB</option>
								<option label="32005">US</option>
							</options>
						</constraints>
						<control type="spinner" format="string"/>
					</setting>
				</group>
			</category>
		</section>
	</settings>
```

