
## search 
search_html="""<div align="left">
<form align="center" action="/search">
<input type="text" name="query" value="">
<input type="submit" value="Search">
</form></div>

<hr>"""


## playback control
# template parameters
# 	TRACKTITLE - title of currently playing track
# 	TRACKTIMES - current_tm/track length if both exist
# requests defined
#   playback( action = "prev" | "rew10m" | "rew3m" | "rew20s" | "playpause" | "ffwd20s" | "ffwd3m" | "ffwd10m" | "next" )
playback_control_html="""<table width="100%">
<tr>
<td>[%TRACKTITLE%]<br>[%TRACKTIMES%]</td>
<td>
<div align="right"><pre><a href="/playback?action="previous""><img src="icons/previous.png" alt="previous" title="restart/previous" height="20"></a>   <a href="/playback?action="rew10m""><img src="icons/rewind-4.png" alt="skip back 10m" title="skip back 10m" height="20"></a>   <a href="/playback?action="rew3m""><img src="icons/rewind-3.png" alt="skip back 3m" title="skip back 3m" height="20"></a>   <a href="/playback?action="rew20s""><img src="icons/rewind-2.png" alt="skip back 20s" title="skip back 20s" height="20"></a>   <a href="/playback?action="playpause""><img src="icons/play_pause.png" alt="play/pause" title="play/pause" height="20"></a>   <a href="/playback?action="ffwd20s""><img src="icons/ffwd-2.png" alt="skip forward 20s" title="skip forward 20s" height="20"></a>   <a href="/playback?action="ffwd3m""><img src="icons/ffwd-3.png" alt="skip forward 3m" title="skip forward 3m" height="20"></a>   <a href="/playback?action="ffwd10m""><img src="icons/ffwd-4.png" alt="skip fowrard 10m" title="skip forward 10m" height="20"></a>   <a href="/playback?action="next""><img src="icons/next.png" alt="next" title="next" height="20"></a></pre></div>
</td></tr></table>
<hr>
"""

## volume
# requests defined
#	volume(vol) 
volume_html="""<div align="left"><pre><a href="/volume&vol="0""><img src="icons/volume_mute.png" alt="mute" title="mute" height="20"></a>   <a href="/volume&vol="25"><img src="icons/volume-1.png" alt="quiet" title="quiet" height="20"></a>   <a href="/volume&vol="50""><img src="icons/volume-2.png" alt="a bit louder" title="a bit louder" height="20"></a>   <a href="/volume&vol="75""><img src="icons/volume-3.png" alt="louder" title="louder" height="20"></a>   <a href="/volume&vol="100""><img src="icons/volume-4.png" alt="loud" title="loud" height="20"></a></pre></div>
"""

## list items
# non-playable
# template parameters:
# 	TITLE should look like "name - artists" or "name - album" or "name"
# 	TYPENAMEURI should look like this type="[%REFTYPE%]"&name="[%NAME%]"&uri="[%URI%]"
# requests defined:
# 	request(reftype, name, uri)

non_playable_item_html="""<tr>
<td>
<h3><a href="/request?[%TYPENAMEURI%]">[%TITLE%]</a></h3>
</td>
<td>
</td>
</tr>"""

# playable list items
# template parameters:
# 	URI - playable ref uri
# 	TITLE should look like "name - artists" or "name - album" or "name"
# 	NAME - playable ref name
# 	FAVORITESACTION - add or remove depending of whether it is in favorites already
# requests defined:
#	track(action = "play_now" | "play_next" | "add_to_queue" | "loop_this", uri)
#	favorites(action= "add" | "remove", name, uri)

playable_item_html="""<tr>
<td>
<h3><a href="/track?action="play_now"&uri="[%URI%]"">[%TITLE%]</a></h3>
</td>
<td>
<div align="left"><pre><a href="/track?action="play_now"&uri="[%URI%]""><img src="icons/play.png" alt="play" title="play" height="16"></a>   <a href="/track?action="play_next"&uri="[%URI%]"""><img src="icons/play_next.png" alt="play next" title="play next" height="16"></a>   <a  href="/track?action="add_to_queue"&uri="[%URI%]""><img src="icons/queue_add.png" alt="add to queue" title="add to queue" height="16"></a>   <a href=" href="/track?action="loop_this"&uri="[%URI%]""><img src="icons/loop_this.png" alt="loop this" title="loop this" height="16"></a>   <a href=" href="/favourites?action="[%FAVORITESACTION%]"&name="[%NAME%]"&uri="[%URI%]""><img src="icons/favorited.png" alt="remove from favorites" title="remove from favorites" height="16"></a></pre></div>
</td>
</tr>"""

comment_html="""<tr>
<td colspan="2">
&nbsp;&nbsp;&nbsp;   [%COMMENTTEXT%]
</td>
</tr>"""

## global toolbar
# template parameters
# 	LOOPALL - loopall_html if currently looking at the queue empty string otherwise
# requests defined
#   global(action = "show_favorites" | "show_queue" | "show_history" | "refresh_onoff")
global_toolbar_html="""<hr>


<div align="center"><pre><a href="/global?action="show_favorites""><img src="icons/favorited.png" alt="show favourites" title="show favorites" height="20"></a>   <a href="/global?action="show_queue""><img src="icons/queue_show.png" alt="show queue" title="show queue" height="20"></a>   <a href="/global?action="show_history""><img src="icons/history.png" alt="show history" title="show history" height="20"></a>   <a href="/global?action="refresh_onoff""><img src="icons/settings.png" alt="show settings" title="show settings" height="20"></a>[%LOOPALL%]</pre></div>

<hr>"""
loop_all_html="""   <a href="/loopall"><img src="icons/loop_this.png" alt="loop all" title="loop all" height="20"></a>"""

