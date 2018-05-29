import os
from subprocess import Popen, call, PIPE
import errno
from types import *
import sys
import time
import shlex
import socket
import os.path
from collections import OrderedDict
import re
from config_util import Config
import logging
import socket

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

_hostapd_conf="""
interface=wlan0
driver=DriverName
#nl80211 - for raspberry native
#rtl871xdrv - for edimax
ssid=NameOfNetwork
hw_mode=g
channel=6
macaddr_acl=0
ignore_broadcast_ssid=0
"""

_wpa_block="""
\tnetwork={
\t        ssid="SSIDNAME"
\t        psk="SSIDPASSWORD"
\t        priority=10
\t}\n"""

_wpa_block_open="""
\tnetwork={
\t        ssid="SSIDNAME"
\t        auth_alg=OPEN
\t        key_mgmt=NONE
\t        priority=10
}\n"""

_wpa_header="""
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB

"""

config = Config('access_point.conf')

ap_name=config.get('access-point','name','UnusualWiFi')
_ap_driver=config.get('access-point','driver','nl80211')
# edimax driver is rtl871xdrv
_ap_interface=config.get('access-point','interface','wlan0')
ap_ip=config.get('access-point','ip','192.168.4.1')
_ap_iprange=config.get('access-point','iprange','192.168.4.2,192.168.4.20')

# run a program and wait for it to finish
def run(rcmd):
    cmd = shlex.split(rcmd)
    executable = cmd[0]
    executable_options=cmd[1:]    

    try:
        proc  = Popen(([executable] + executable_options), 
            stdout=PIPE, stderr=PIPE)
        response = proc.communicate()
        response_stdout, response_stderr = response[0], response[1]
    except OSError, e:
        if e.errno == errno.ENOENT:
            log.warn( 'Unable to locate %s.' % executable ) 
        else:
            log.warn('O/S error occured when trying to run %s: "%s"' % \
                (executable, str(e)))
        return None    
    except ValueError, e:
        log.warn('Value error when running %s' % executable) 
    else:
        if proc.wait() != 0:
            log.warn('Executable %s returned with the error: "%s"' \
                %(executable,response_stderr)) 
            return response
        else:
            return response_stdout

# checks which ssid we are conected to
def get_connected_ssid():
    w=run('sudo wpa_cli status')
    gs=re.search('^ssid=(.*)',w,re.M)
    if gs is None: return None
    if len(gs.groups()) == 0: 
        return None
    return gs.groups()[0]

# lists available wifi interfces
def _list_wifi_interfaces():
    s=run('sudo wpa_cli interface')
    p='Available interfaces:\n'
    return s[s.find(p)+len(p):].split()

# a class to return information about an interface
class interface_info:
    def __init__(self,interface, ip_address, is_wifi, ssid):
        self.interface=interface        # interface name
        self.ip_address=ip_address      # ip if connected, None otherwise
        self.is_wifi=is_wifi            # is this a wifi interface?
        self.ssid=ssid                  # ssid if connected, None otherwise

    def __repr__(self):
        return '%s : %s : %s : %s' % \
            (self.interface,self.ip_address,self.is_wifi,self.ssid)


# get information about interfaces
def get_ssid(iface):
    s=run('sudo iwconfig')
    ss=re.findall('%s.+ESSID:\"(.*)\" ' % iface,s)
    if len(ss)!=1: return None
    return ss[0]

def get_interfaces_info():
    s=run('sudo ip address show')
    m=re.findall('^\s*inet ([0-9\.]+).+\s(\S+)$',s,re.M)
    wifis=_list_wifi_interfaces()
    infos={}
    for (ip,iface) in m:
        if iface == 'lo' or iface == 'tun0' or ('p2p' in iface):continue
        is_wifi=iface in wifis
        ssid=None
        if is_wifi: ssid=get_ssid(iface)
        infos[iface]=interface_info(iface,ip,is_wifi,ssid)

    for w in wifis:
        if w not in infos and ('p2p' not in w):
            infos[w]=interface_info(w,None,True,None)
    ret=[infos[i] for i in infos]
    return ret

# get ip on a connected wifi
# if there are none, check lans
def get_ip():
    ifs=get_interfaces_info()
    for i in ifs:
        if i.is_wifi and i.ssid is not None:
            return i.ip_address

    for i in ifs:
        if not i.is_wifi:
            return i.ip_address

    return None


# check if we are connected to internet
def is_connected():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return True
    except socket.error:
        s.close()
        return False

# list available wifi networks 
def _get_networks(iface=_ap_interface, retry=20):
    while retry > 0:
        if 'OK' in run('sudo wpa_cli -i %s scan' % iface):
            networks=[]
            r = run('sudo wpa_cli -i %s scan_result' % iface).strip()
            if 'bssid' in r and len ( r.split('\n') ) >1 :
                for line in r.split('\n')[1:]:
                    b, fr, s, f = line.split()[:4]
                    ss = ' '.join(line.split()[4:]) #Hmm, dirty
                    networks.append( \
                        {'bssid':b, 'freq':fr, 'sig':s, 'ssid':ss, 'flag':f} )
                return networks
        retry-=1
        time.sleep(0.5)
        return None

# get data about available networks
# returns triplets (interface name, network name, WPA or OPEN)
def list_network_data(iface=_ap_interface):
    ns=_get_networks(iface)
    d=[]
    if ns is None: return d
    for n in ns:
        ssid=n['ssid']
        _type='OPEN'
        if 'WPA' in n['flag']:
            _type='WPA'
        elif 'WEP' in n['flag']:
            _type='WEP'
        d.append((iface,ssid,_type))
    return d

# get the name of this host
def get_host_name():
        return socket.gethostname()

# start access point
def start_ap():
    p=_get_config_path()
    run('sudo cp /etc/dnsmasq.conf %s/dnsmasq.conf.backup' % p)
    run('sudo cp /etc/default/hostapd %s/hostapd.backup' % p)
    run('sudo cp /etc/dhcpcd.conf %s/dhcpcd.conf.backup' % p)
    run('sudo cp /etc/wpa_supplicant/wpa_supplicant.conf'+\
         '%s/wpa_supplicant.conf.backup' % p)
    
    run('sudo cp /etc/hostapd/hostapd.conf %s/hostapd.conf.backup' % p)
    hostapd_conf=_hostapd_conf.replace('NameOfNetwork',_ap_name).\
        replace('DriverName',_ap_driver).replace('wlan0',_ap_interface)

    try:
        out=open('/etc/hostapd/hostapd.conf','w')
        out.write(hostapd_conf)
    finally:
        out.close()

    f=open('%s/dhcpcd.conf.ap' % p)
    file_text=f.read().replace('wlan0',_ap_interface).\
        replace('IP_ADDRESS',_ap_ip)
    f.close()
    f=open('/etc/dhcpcd.conf','w')
    f.write(file_text)
    f.close()

    f=open('%s/dnsmasq.conf.ap' % p)
    file_text=f.read().replace('wlan0',_ap_interface).\
        replace('IP_RANGE',_ap_iprange)
    f.close()
    f=open('/etc/dnsmasq.conf','w')
    f.write(file_text)
    f.close()
    

    run('sudo cp %s/hostapd.ap /etc/default/hostapd' % get_path())
    run('sudo cp %s/wpa_supplicant.empty '+\
        '/etc/wpa_supplicant/wpa_supplicant.conf' % p)
    
    
    run('sudo ip link set %s down' % _ap_interface)
    time.sleep(3)
    run('sudo ip link set %s up' % _ap_interface)
    time.sleep(1)
    run('sudo systemctl daemon-reload')
    time.sleep(1)
    run('sudo systemctl restart dhcpcd')
    time.sleep(1)
    run('sudo systemctl start dnsmasq')
    time.sleep(1)
    run('sudo systemctl start hostapd')
    time.sleep(1)
    run('sudo systemctl restart dnsmasq')
    time.sleep(1)
    run('sudo systemctl restart hostapd')

# stop access point and start wifi
def start_wifi():
    p=_get_config_path()
    wpa_backp='%s/wpa_supplicant.conf.backup' % p
    if os.path.is_file(wpa_backp):
        run('sudo cp %s /etc/wpa_supplicant/wpa_supplicant.conf' % wpa_backp)
    run('cp %s/dhcpcd.conf.backup /etc/dhcpcd.conf' % p)
    run('cp %s/dnsmasq.conf.backup /etc/dnsmasq.conf' % p)
    run('cp %s/hostapd.conf.backup /etc/hostapd/hostapd.conf' % p)
    run('cp %s/hostapd.backup /etc/default/hostapd' % p)

    run('sudo systemctl stop dnsmasq')
    time.sleep(1)
    run('sudo systemctl daemon-reload')
    time.sleep(1)
    run('sudo systemctl stop hostapd')
    time.sleep(1)
    run('sudo systemctl daemon-reload')
    time.sleep(1)
    run('sudo systemctl restart dhcpcd')
    time.sleep(1)
    run('sudo wpa_cli reconfigure')

def _parse_wpa_file(fname):
    wpa_networks=OrderedDict()
    if os.path.exists(fname):
        wpa_text=open(fname).read()
        token='network='
        blocks=wpa_text.split(token)
        wpa_header=blocks[0]
        c=0
        for n in blocks[1:]:
            ssid=re.findall('\sssid=(.*)',n)
            if len(ssid)!=1:
                ssid='complex %i' % c
                c+=1
            else:
                ssid=ssid[0].strip('"')
                if ssid in wpa_networks:
                    ssid+='%i' % c
                    c+=1
            wpa_networks[ssid]=token+n
        return (wpa_header,wpa_networks)
    else:
        return (_wpa_heder,wpa_networks)

def _save_wpa_file(wpa_header, wpa_networks_dict, fname):
    merged=wpa_header
    for k in wpa_networks_dict:
        merged+=wpa_networks_dict[k]

    try:
        out=open(fname,'w')
        out.write(merged)
    finally:
        out.close()


def _add_wpa_network(ssid,password,wpa_networks):
    for k in wpa_networks:
        n=wpa_networks[k]
        if 'priority' in n:
            n.replace('priority.*=.*$','')
            wpa_networks[k]=n

    if password is None or password.length==0:
        if ssid in wpa_networks:
            nblock=wpa_networks[ssid]
            nblock=nblock.replace('}','\tpriority=10\n}')
        else:
            if ssid in wpa_networks:
                del wpa_networks[ssid]
            nblock=_wpa_block_open.replace('SSIDNAME',ssid)
    else:
        if ssid in wpa_networks:
            del wpa_networks[ssid]
        nblock=_wpa_block.replace('SSIDNAME',ssid).replace('SSIDPASSWORD',password)

    wpa_networks[ssid]=nblock
    return wpa_networks        

# add wifi network or choose an existing one
# if invoked with an existing network and no password
# it will just set the priority of the chosen network high
def set_wifi(ssid,password):
    wpa_backp='%s/wpa_supplicant.conf.backup' % get_path()
    if os.path.is_file(wpa_backp):
        fname=wpa_backp
    else:
        fname='/etc/wpa_supplicant/wpa_supplicant.conf'
    (h,ns)=_read_wpa_file(fname)
    ns=_add_wpa_network(ssid,password,ns)
    _save_wpa_file(h,ns,fname)

def restart_wifi():
    run('sudo wpa_cli reconfigure')
    time.sleep(1)
    run('sudo ip link set %s down' % _ap_interface)
    time.sleep(3)
    run('sudo ip link set %s up' % _ap_interface)
    time.sleep(1)
