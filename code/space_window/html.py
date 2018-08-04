
_html_template_main=u"""
<!doctype html>
<html>
<head>
    <title>Space Window</title>
    <meta name="description" content"Space Window">
    <meta name="viewport" content="width=device-width">
    <meta http-equiv="Cache-Control" content="no-cache, no-store,must-revalidate"/>
    <meta http-equiv="Pragma" content="no-cache"/>
    <meta http-equiv="Expires" content="-1"/>
<style>
        body {
            color: #ff8000;
            background-color: #200020;
            font-family: "Comic Sans MS";
            border-radius: 5px; 
            }
        input[type=text]{
            color: #ff8000;
            background-color: #200020;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
            }
        input[type=submit]{
            color: #ff8000;
            background-color: #200020;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
            }
        button[type=submit]{
            color: #ff8000;
            background-color: #200020;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
            }
        input[type=password]{
            color: #ff8000;
            background-color: #800080;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
          }
</style>
</head>
<body>
<h1>Space Window</h1>
<br><br>
HTML_BODY
</body>

"""           
_main_table=u"""

<div align="left">
<form align="center" action="/play_remove">
    <table width=100%>
    STREAM_ROWS
    </table>
    </form></div>
    <br/>
    <hr/>
    <br/>
    <div align="left">
    <form align="center" action="/add_link">
    <input type="text" name="name" value="NAME">
    <input type="text" name="link" value="LINK">
    <input type="text" name="quality" value="best">
    <input type="hidden" name="hiddenadd_CNT" value="ADDLINK">
    <input type="submit" value="Add">
</form></div>
<br/>
<hr/>
<br/>
<table width=100%>
<tr>
<td>
    <form action="/slideshow">
    <input type="hidden" name="hiddennasa_CNT" value="NASAPOD">
    <input type="submit" value="Nasa POD">
    </form>
</td><td>
    <form action="/next">
    <input type="hidden" name="hiddenplay_CNT" value="NEXT">
    <input type="submit" value="Play next">
    </form>
</td><td>
    <form action="/rough">
    <input type="hidden" name="hiddenrough_CNT" value="ROUGH">
    <input type="submit" value="Radio Rough">
    </form>
<!--</td><td>
    <form action="/kodi">
    <input type="hidden" name="hiddenkodi_CNT" value="KODI">
    <input type="submit" value="kodi :)">
    </form>-->
</td>
<td>
    <form action="/shutdown">
    <input type="hidden" name="hiddenshutdown_CNT" value="SHUTDOWN">
    <input type="submit" value="Shutdown">
    </form>
</td><td>
    <form action="/wifi">
    <input type="hidden" name="hiddenwifi_CNT" value="WIFI">
    <input type="submit" value="Change WiFi">
    </form>
</td>
</tr>
</table>    
"""

_cnt=0
def build_html(body):
    global _cnt
    html = _html_template_main.replace('HTML_BODY',body)
    _cnt+=1
    cntstr='%i' % _cnt
    return html.replace('CNT',cntstr)

def get_main_html(rows_html):
    global _cnt
    html = _html_template_main.replace('HTML_BODY',_main_table).\
        replace('STREAM_ROWS',rows_html)
    _cnt+=1
    cntstr='%i' % _cnt
    return html.replace('CNT',cntstr)
