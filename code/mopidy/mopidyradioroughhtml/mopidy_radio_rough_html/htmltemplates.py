
main_html= u"""<!doctype html>
<html>
<head>
    <title>Radio Rough [%TITLE%] </title>
    <meta name="description" content"Radio Rough">
    [%REFRESH%]
</head>
<body>

<h1>Radio Rough [%TITLE%] </h1>
[%COMMENTTEXT%]
[%SEARCH%]
[%PLAYCONTROL%]
[%VOLUMECONTROL%]
[%ITEMS%]
[%GLOBAL%]
</body>
"""


## search 
search_html=u"""<br/><div align="left">
<form align="center" action="/radiorough/search">
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
playback_control_html=u"""<table width="100%">
<tr>
<td>[%TRACKTITLE%]<br>[%TRACKTIMES%]</td>
<td>
<div align="right"><pre><a href="/radiorough/playback?action=previous"><img src="/radiorough/icons/previous.png" alt="previous" title="restart/previous" height="20"></a>   <a href="/radiorough/playback?action=rew10m"><img src="/radiorough/icons/rewind-4.png" alt="skip back 10m" title="skip back 10m" height="20"></a>   <a href="/radiorough/playback?action=rew3m"><img src="/radiorough/icons/rewind-3.png" alt="skip back 3m" title="skip back 3m" height="20"></a>   <a href="/radiorough/playback?action=rew20s"><img src="/radiorough/icons/rewind-2.png" alt="skip back 20s" title="skip back 20s" height="20"></a>   <a href="/radiorough/playback?action=playpause"><img src="/radiorough/icons/play_pause.png" alt="play/pause" title="play/pause" height="20"></a>   <a href="/radiorough/playback?action=ffwd20s"><img src="/radiorough/icons/ffwd-2.png" alt="skip forward 20s" title="skip forward 20s" height="20"></a>   <a href="/radiorough/playback?action=ffwd3m"><img src="/radiorough/icons/ffwd-3.png" alt="skip forward 3m" title="skip forward 3m" height="20"></a>   <a href="/radiorough/playback?action=ffwd10m"><img src="/radiorough/icons/ffwd-4.png" alt="skip fowrard 10m" title="skip forward 10m" height="20"></a>   <a href="/radiorough/playback?action=next"><img src="/radiorough/icons/next.png" alt="next" title="next" height="20"></a></pre></div>
</td></tr></table>
<hr>
"""
playback_tools_html="""
<div align="left"><pre><a href="/radiorough/playback?action=previous"><img src="/radiorough/icons/previous.png" alt="previous" title="restart/previous" height="20"></a>   <a href="/radiorough/playback?action=rew10m"><img src="/radiorough/icons/rewind-4.png" alt="skip back 10m" title="skip back 10m" height="20"></a>   <a href="/radiorough/playback?action=rew3m"><img src="/radiorough/icons/rewind-3.png" alt="skip back 3m" title="skip back 3m" height="20"></a>   <a href="/radiorough/playback?action=rew20s"><img src="/radiorough/icons/rewind-2.png" alt="skip back 20s" title="skip back 20s" height="20"></a>   <a href="/radiorough/playback?action=playpause"><img src="/radiorough/icons/play_pause.png" alt="play/pause" title="play/pause" height="20"></a>   <a href="/radiorough/playback?action=ffwd20s"><img src="/radiorough/icons/ffwd-2.png" alt="skip forward 20s" title="skip forward 20s" height="20"></a>   <a href="/radiorough/playback?action=ffwd3m"><img src="/radiorough/icons/ffwd-3.png" alt="skip forward 3m" title="skip forward 3m" height="20"></a>   <a href="/radiorough/playback?action=ffwd10m"><img src="/radiorough/icons/ffwd-4.png" alt="skip fowrard 10m" title="skip forward 10m" height="20"></a>   <a href="/radiorough/playback?action=next"><img src="/radiorough/icons/next.png" alt="next" title="next" height="20"></a></pre></div>
<hr>"""

## volume
# requests defined
#	volume(vol) 
volume_html=u"""<div align="left"><pre><a href="/radiorough/volume?vol=0"><img src="/radiorough/icons/volume_mute.png" alt="mute" title="mute" height="20"></a>   <a href="/radiorough/volume?vol=25"><img src="/radiorough/icons/volume-1.png" alt="quiet" title="quiet" height="20"></a>   <a href="/radiorough/volume?vol=50"><img src="/radiorough/icons/volume-2.png" alt="a bit louder" title="a bit louder" height="20"></a>   <a href="/radiorough/volume?vol=75"><img src="/radiorough/icons/volume-3.png" alt="louder" title="louder" height="20"></a>   <a href="/radiorough/volume?vol=100"><img src="/radiorough/icons/volume-4.png" alt="loud" title="loud" height="20"></a></pre></div>
"""

## list items
# non-playable
# template parameters:
# 	TITLE should look like "name - artists" or "name - album" or "name"
# 	TYPENAMEURI should look like this type="[%REFTYPE%]"&name="[%NAME%]"&uri="[%URI%]"
# requests defined:
# 	request(reftype, name, uri)

non_playable_item_html=u"""
<h4><a href="/radiorough/request?[%TYPENAMEURI%]">[%TITLE%]</a></h4>
"""

# playable list items
# template parameters:
# 	URI - playable ref uri
# 	TITLE should look like "name - artists" or "name - album" or "name"
# 	NAME - playable ref name
# requests defined:
#	track(action = "play_now" | "play_next" | "remove_from_queue" | "add_to_queue" | "loop_this", uri)
#	favorites(action= "add" | "remove", name, uri)
playable_item_html=u"""<tr>
<td>
<h4><a href="/radiorough/track?action=play_now&uri=[%URI%]">[%TITLE%]</a></h4>
</td>
<td>
<div align="left"><pre><a href="/radiorough/track?action=play_now&uri=[%URI%]"><img src="/radiorough/icons/play.png" alt="play" title="play" height="16"></a>   <a href="/radiorough/track?action=play_next&uri=[%URI%]"><img src="/radiorough/icons/play_next.png" alt="play next" title="play next" height="16"></a>   <a  href="/radiorough/track?action=add_to_queue&uri=[%URI%]"><img src="/radiorough/icons/queue_add.png" alt="add to queue" title="add to queue" height="16"></a>   <a href="/radiorough/track?action=loop_this&uri=[%URI%]"><img src="/radiorough/icons/loop_this.png" alt="loop this" title="loop this" height="16"></a>   <a href="/radiorough/favorites?action=add&name=[%NAME%]&uri=[%URI%]"><img src="/radiorough/icons/favorites_add.png" alt="remove from favorites" title="remove from favorites" height="16"></a></pre></div>
</td>
</tr>"""

playable_item_html_favorited=u"""<tr>
<td>
<h4><a href="/radiorough/track?action=play_now&uri=[%URI%]">[%TITLE%]</a></h4>
</td>
<td>
<div align="left"><pre><a href="/radiorough/track?action=play_now&uri=[%URI%]"><img src="/radiorough/icons/play.png" alt="play" title="play" height="16"></a>   <a href="/radiorough/track?action=play_next&uri=[%URI%]"><img src="/radiorough/icons/play_next.png" alt="play next" title="play next" height="16"></a>   <a  href="/radiorough/track?action=add_to_queue&uri=[%URI%]"><img src="/radiorough/icons/queue_add.png" alt="add to queue" title="add to queue" height="16"></a>   <a href="/radiorough/track?action=loop_this&uri=[%URI%]"><img src="/radiorough/icons/loop_this.png" alt="loop this" title="loop this" height="16"></a>   <a href="/radiorough/favorites?action=remove&name=[%NAME%]&uri=[%URI%]"><img src="/radiorough/icons/favorited.png" alt="remove from favorites" title="remove from favorites" height="16"></a></pre></div>
</td>
</tr>"""

comment_html=u"""<tr>
<td colspan="2">
&nbsp;&nbsp;&nbsp;   [%COMMENTTEXT%]
</td>
</tr>"""

## global toolbar
# template parameters
# 	LOOPALL - loopall_html if currently looking at the queue empty string otherwise
# requests defined
#   global("refresh_onoff")
global_toolbar_html=u"""<hr>


<div align="center"><pre><a href="/radiorough/request?type=directory&name=Favourites&uri=rough%2Bfavourites"><img src="/radiorough/icons/favorited.png" alt="show favorites" title="show favorites" height="20"></a>   <a href="/radiorough/request?type=directory&name=Queue&uri=rough%2Bqueue"><img src="/radiorough/icons/queue_show.png" alt="show queue" title="show queue" height="20"></a>   <a href="/radiorough/request?type=directory&name=History&uri=rough%2Bhistory"><img src="/radiorough/icons/history.png" alt="show history" title="show history" height="20"></a>   <a href="/radiorough/global?action=refresh_onoff"><img src="/radiorough/icons/settings.png" alt="show settings" title="show settings" height="20"></a>[%LOOPALL%]</pre></div>

<hr>"""
loop_all_html=u"""   <a href="/radiorough/global?action=loopall"><img src="/radiorough/icons/loop_this.png" alt="loop all" title="loop all" height="20"></a>"""

