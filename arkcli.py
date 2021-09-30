#!/usr/bin/python3
# encoding=utf8

import valve.source.a2s
import valve.source.master_server
import urllib
import json
import ast
import sys
import getopt
import datetime
import time
from datetime import datetime, timedelta
from datetime import datetime
from colorama import Fore
from colorama import Style
from colorama import init
import signal
import threading
import concurrent.futures

init()

signal.signal(signal.SIGINT, lambda x, y: sys.exit(1))

try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3

reload(sys)

if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib import urlopen
    sys.setdefaultencoding('utf8')

def genunoff(host,port,timeout,lock):
      info = query(host,port,"linfo","",timeout)
      servname = "{server_name}".format(**info).split(" - (v")[0]
      lock.acquire()
      print(servname + ":" + host + ":" + str(port) + ":" + servname)
      lock.release()

def genoff(host,p,timeout,lock):
      info = query(host,p,"loinfo","",timeout)      
      servname = "{server_name}".format(**info).split(" - (v")[0]
      fancyname = servname
      if 'Island' in servname:
        fancyname = "Island " + servname.split("Island")[1]
      if 'OfficialServer' in servname:
        fancyname = "Island " + servname.split("OfficialServer")[1].split(" ")[0]
      if 'Scorched' in servname:
        fancyname = "Scorched " + servname.split("ScorchedEarth")[1]
      if 'Ragnarok' in servname:
        fancyname = "Ragnarok " + servname.split("Ragnarok")[1]
      if 'Valguero' in servname:
        fancyname = "Valguero " + servname.split("Valguero")[1]
      if 'Extinction' in servname:
        fancyname = "Extinction " + servname.split("Extinction")[1]
      if 'GenOne' in servname:
        fancyname = "GenOne " + servname.split("GenOne")[1]
      if 'Aberration' in servname:
        fancyname = "Aberration " + servname.split("Aberration")[1]
      if 'Center' in servname:
        fancyname = "Center " + servname.split("Center")[1]
      if 'CrystalIsles' in servname:
        fancyname = "Crystal Isles " + servname.split("CrystalIsles")[1]
      if 'SmallTribes' in servname:
        fancyname = fancyname.split(" -SmallTribes")[0] + " SmallTribes " + fancyname.split(" -SmallTribes")[1]
      if 'Hardcore' in servname:
        fancyname = fancyname.split(" -Hardcore")[0] + " Hardcore " + fancyname.split(" -Hardcore")[1]
      if 'ARKpocalypse' in servname:
        fancyname = fancyname.split(" -ARKpocalypse")[0] + " ARKpocalypse " + fancyname.split(" -ARKpocalypse")[1]
      if 'Conquest' in servname:
        fancyname = fancyname.split(" -Conquest")[0] + " Conquest " + fancyname.split(" -Conquest")[1]
      if 'CrossArk' in servname:
        if 'PrimPlusCrossArk' in servname:
          fancyname = fancyname.split(" -PrimPlusCrossArk")[0] + " PrimPlusCrossArk " + fancyname.split(" -PrimPlusCrossArk")[1]
        else:
          fancyname = fancyname.split(" -CrossArk")[0] + " CrossArk " + fancyname.split(" -CrossArk")[1]
      output = fancyname + ":" + host + ":" + str(p) + ":" + servname
      lock.acquire()
      print(output)
      lock.release()

def evo_event(o_color):
  url = "http://arkdedicated.com/dynamicconfig.ini"
  file = urlopen(url)
  for line in file:
    line = str(line.split(b"\n")[0])
    if 'TamingSpeedMultiplier' in line:
      if o_color:
        print(Fore.YELLOW + "Taming:                          " + Fore.CYAN + line.split("=")[1][:3] + "x" + Style.RESET_ALL)
      else:
        print("Taming:                          " + line.split("=")[1][:3] + "x") 
    if 'Harvest' in line:
      if o_color:
        print(Fore.YELLOW + "Harvest:                         " + Fore.CYAN + line.split("=")[1][:3] + "x" + Style.RESET_ALL) 
      else:
        print("Harvest:                         " + line.split("=")[1][:3] + "x")
    if 'XP' in line:
      if o_color:
        print(Fore.YELLOW + "XP:                              " + Fore.CYAN + line.split("=")[1][:3] + "x" + Style.RESET_ALL)
      else:
        print("XP:                              " + line.split("=")[1][:3] + "x")
    if 'Baby' in line:
      if o_color:
        print(Fore.YELLOW + "Breeding:                        " + Fore.CYAN + line.split("=")[1][:3] + "x" + Style.RESET_ALL)
      else:
        print("Breeding:                        " + line.split("=")[1][:3] + "x")

def query(ip,port,type,sname="unknown",timeout="5"):
  server_address = (ip,port)
  with valve.source.a2s.ServerQuerier(server_address,timeout=int(timeout)) as server:
    if type == "linfo":
      try:
        info = server.info()
        return info
      except valve.source.NoResponseError:
        pass

    if type == "loinfo":
      try:
        info = server.info()
        return info
      except valve.source.NoResponseError:
        pass

    if type == "info":
      try:
        info = server.info()
        return 0,info
      except valve.source.NoResponseError:
        return 1,None

    if type == "players":
      try:
        players = server.players()
        return 0,players
      except valve.source.NoResponseError:
        return 1,None

    if type == "rules":
      try:
        rules = server.rules()
        return 0,rules
      except valve.source.NoResponseError:
        return 1,None

    if type == "ping":
      try:
        #ping = server.ping()
        #changed because version of python-valve in pip for python3 has a typo not fixed in 3 years
        t_send = time.time()
        pfake = server.info()
        ping = (time.time() - t_send) * 1000.0
        return 0,ping
      except valve.source.NoResponseError:
        return 1,None

def tgenlog(server,timeout,o_color,lock):
  ip = server[0]
  port = server[1]
  sname = server[2]
  status, result = query(ip,port,"info",sname,timeout)
  datetimeobj = datetime.now()
  date = datetimeobj.strftime("%Y/%m/%d %H:%M:%S")
  lock.acquire()
  if status == 0:
    pcount = "{player_count}/{max_players}".format(**result)
    sername = "{server_name}".format(**result)
    servname = sername.split(" - (v")[0]
    serversion = sername.split(" - (v")[1].split(")")[0]
    if o_color:
      output = Style.BRIGHT + "server."+ servname + Style.RESET_ALL +  " players=" + Fore.CYAN + pcount + Style.RESET_ALL + " name=" + Fore.CYAN + servname + Style.RESET_ALL + " ver=" + Fore.CYAN + serversion + Style.RESET_ALL
      print(Fore.YELLOW + "["+date+"] " + Style.RESET_ALL + output)
    else:
      output = "server."+ servname + " players=" + pcount + " name=" + servname + " ver=" + serversion
      #output = "server."+ sname + " players={player_count}/{max_players} name={server_name}".format(**result).replace(" - "," ver=").replace        #("(","").replace(")","")
      print("["+date+"] " + output)
  if status == 1:
    if o_color:
      print(Fore.YELLOW + "["+date+"] " + Style.RESET_ALL + Style.BRIGHT + "server."+ sname + Fore.RED + " timeout" + Style.RESET_ALL)
    else:
      print("["+date+"] server."+ sname + " timeout")
  lock.release()

def genlog(server,timeout,o_color):
  ip = server[0]
  port = server[1]
  sname = server[2]
  status, result = query(ip,port,"info",sname,timeout)
  datetimeobj = datetime.now()
  date = datetimeobj.strftime("%Y/%m/%d %H:%M:%S")  
  if status == 0:
    pcount = "{player_count}/{max_players}".format(**result)
    sername = "{server_name}".format(**result)
    servname = sername.split(" - (v")[0]
    serversion = sername.split(" - (v")[1].split(")")[0]
    if o_color:
      output = Style.BRIGHT + "server."+ servname + Style.RESET_ALL +  " players=" + Fore.CYAN + pcount + Style.RESET_ALL + " name=" + Fore.CYAN + servname + Style.RESET_ALL + " ver=" + Fore.CYAN + serversion + Style.RESET_ALL
      print(Fore.YELLOW + "["+date+"] " + Style.RESET_ALL + output)
    else:
      output = "server."+ servname + " players=" + pcount + " name=" + servname + " ver=" + serversion
      #output = "server."+ sname + " players={player_count}/{max_players} name={server_name}".format(**result).replace(" - "," ver=").replace        #("(","").replace(")","")
      print("["+date+"] " + output)
  if status == 1:
    if o_color:
      print(Fore.YELLOW + "["+date+"] " + Style.RESET_ALL + Style.BRIGHT + "server."+ sname + Fore.RED + " timeout" + Style.RESET_ALL)
    else:
      print("["+date+"] server."+ sname + " timeout")

def servdown(color):
  if color:
    print(Fore.RED + "[*] Error retrieving information from server (timeout)" + Style.RESET_ALL)
  else:
    print("[*] Error retrieving information from server (timeout)")

def header(color,header):
  if color:
    print(Fore.MAGENTA + "========================================")
    print(Style.BRIGHT + header + Style.RESET_ALL)
    print(Fore.MAGENTA + "========================================" + Style.RESET_ALL)
  else:
    print("========================================")
    print(header)
    print("========================================")

def usage():
  print("ARK Servers Tester CLI")
  print("Show information about ARK servers using A2S Steam Queries and ARK Web API")
  print("Usage: ")
  print("arkcli.py --server [SERVERNAME] [OPTION]...")
  print("arkcli.py --server [SERVERNAME] -l [OPTION]...")
  print("arkcli.py -k [TYPE]")
  print("arkcli.py -e")

  print("""
	OPTIONS
	-C			Colorize output
	-H			Print headers
	-v		        Verbose. Double vv to increase verbosity level (-vv)
        -T n                    Set number of threads for concurrent operations (def.8)

	SERVER FILE
	-S file			Use alternative servers file instead of servers.txt

        SERVER INFO
        -s	--server=	First or forth field of servers.txt. Multiple -s are allowed
        -s all                   Picks all servers on the server file                               
	-i			Show basic info
	-p			Show player list
	-r			Show server rules
	-P			Show server ping

        LOG PRINTING
	-l			Show server status in log format
	-w n			In conjunction with -l it loops every n seconds 
	-t n			Set request timeout seconds (def.2)

        SERVERS LIST
        -k type			Retrieve server list. Types are (o) official and (u) unofficial

	EVO EVENT
	-e			Show official server rates
	""")

def main():
  serverlist = "servers.txt"
  o_info = False
  o_server = False
  o_players = False
  o_rules = False
  o_ping = False
  o_log = False
  o_watch = False
  o_serverlist = False
  o_evo = False
  o_color = False
  o_header = False
  o_verbose = False
  timeout = 2
  found = False
  verbosity = 0
  threads = 8
  slist = []
  try:
    opts, args = getopt.getopt(sys.argv[1:], "S:s:w:t:k:T:iprPleCvH", ["server="])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  if not opts:
    usage()
    sys.exit(2)
  for o, a in opts:
    if o == "-S":
      serverlist = a
    elif o in ("-s", "--server"):
      o_server = True
      found = False
      f = open(serverlist, "r")
      for x in f:
        if a in(x.split(':')[0],x.split(':')[3]) or a == "all":
          ip = x.split(':')[1]
          port = int(x.split(':')[2])
          sname = x.split(':')[3].replace("\n", "")
          slist.append([ip,port,sname])
          found = True
      if found == False:
        print("Server name not found! (" + a + ")")
        sys.exit(2)

    elif o == "-k":
      o_serverlist = True
      type = a
    elif o == "-e":
      o_evo = True
    elif o == "-i":
      o_info = True 
    elif o == "-p":
      o_players = True
    elif o == "-r":
      o_rules = True
    elif o == "-P":
      o_ping = True
    elif o == "-l":
      o_log = True
    elif o == "-C":
      o_color = True
    elif o == "-v":
      o_verbose = True
      verbosity = verbosity + 1
    elif o == "-H":
      o_header = True
    elif o == "-w":
      o_watch = True
      wtime = a
    elif o == "-T":
      o_threads = True
      threads = a
    elif o == "-t":
      o_timeout = True
      timeout = a

    else:
      usage()
      sys.exit(2)

  for server in slist:
    ip = server[0]
    port = server[1]
    sname = server[2]

    if o_verbose == True:
      if o_color:
        print("[*] Querying " + Fore.CYAN + sname + Style.RESET_ALL + " (" + Fore.YELLOW + ip + Style.RESET_ALL + ":" + Fore.YELLOW + str(port) + Style.RESET_ALL + ")...")
      else:
        print("[*] Querying " + sname + " (" + ip + ":" + str(port) + ")...")
  
    if o_info == True and o_server == True:
      status, result = query(ip,port,"info")
      if o_header:
        header(o_color,"Server Basic Information")
      if status == 0:
        pcount = "{player_count}/{max_players}".format(**result)
        sername = "{server_name}".format(**result)
        servname = sername.split(" - (v")[0]
        serversion = sername.split(" - (v")[1].split(")")[0]
        if o_color:
          print(Fore.YELLOW + "Server name:                     " + Fore.CYAN + servname + Style.RESET_ALL)
          print(Fore.YELLOW + "Server version:                  " + Fore.CYAN + serversion + Style.RESET_ALL)
          print(Fore.YELLOW + "Players counter:                 " + Fore.CYAN + pcount + Style.RESET_ALL)
        else:
          print("Server name:                     " + servname)
          print("Server version:                  " + serversion)
          print("Players counter:                 " + pcount)
      if status == 1:
        servdown(o_color)

    if o_players == True and o_server == True:
      status, result = query(ip,port,"players")
      if o_header:
        header(o_color,"Players")
      if status == 0:
        for player in sorted(result["players"],key=lambda p: p["score"], reverse=True):
          name = "{name}".format(**player)
          duration = "{duration}".format(**player)
          sec = timedelta(seconds=float(duration))
          d = datetime(1,1,1) + sec
          if o_color:
            print(Fore.YELLOW + "%-30s   " % (name) + Fore.CYAN + "%dd %dh %dm %ds" % (d.day-1, d.hour, d.minute, d.second) + Style.RESET_ALL)
          else:
            print("%-30s   %dd %dh %dm %ds" % (name,d.day-1, d.hour, d.minute, d.second))
      if status == 1:
        servdown(o_color)

    if o_rules == True and o_server == True:
      status, result = query(ip,port,"rules")
      if o_header:
        header(o_color,"Server Rules")
      if status == 0:
        s = "{rules}".format(**result)
        drules = s.replace("'","\"")
        xrules = eval(drules)
        for i in xrules:
         if i == "LEGACY_i":
           if o_color:
             print(Fore.YELLOW + "Legacy Server:                   " + Fore.CYAN + xrules['LEGACY_i'] + Style.RESET_ALL)
           else:
             print("Legacy Server:                   " + xrules['LEGACY_i'])
         elif i == "ALLOWDOWNLOADCHARS_i":
           if o_color:
             print(Fore.YELLOW + "Allow Download Chars:            " + Fore.CYAN + xrules['ALLOWDOWNLOADCHARS_i'] + Style.RESET_ALL)
           else:
             print("Allow Download Chars:            " + xrules['ALLOWDOWNLOADCHARS_i'])
         elif i == "SERVERUSESBATTLEYE_b":
           if o_color:
             print(Fore.YELLOW + "Server Uses BattleEye:           " + Fore.CYAN + xrules['SERVERUSESBATTLEYE_b'] + Style.RESET_ALL)
           else:
             print("Server Uses BattleEye:           " + xrules['SERVERUSESBATTLEYE_b'])
         elif i == "HASACTIVEMODS_i":
           if o_color:
             print(Fore.YELLOW + "Server has active mods:          " + Fore.CYAN + xrules['HASACTIVEMODS_i'] + Style.RESET_ALL)
           else:
             print("Server has active mods:          " + xrules['HASACTIVEMODS_i'])
         elif i == "MATCHTIMEOUT_f":
           if o_color:
             print(Fore.YELLOW + "Match Timeout:                   " + Fore.CYAN + xrules['MATCHTIMEOUT_f'] + Style.RESET_ALL)
           else:
             print("Match Timeout:                   " + xrules['MATCHTIMEOUT_f'])
         elif i == "ClusterId_s":
           if o_color:
             print(Fore.YELLOW + "Cluster ID:                      " + Fore.CYAN + xrules['ClusterId_s'] + Style.RESET_ALL)
           else:
             print("Cluster ID:                      " + xrules['ClusterId_s'])
         elif i == "SESSIONFLAGS":
           if o_color:
             print(Fore.YELLOW + "Session Flags:                   " + Fore.CYAN + xrules['SESSIONFLAGS'] + Style.RESET_ALL)
           else:
             print("Session Flags:                   " + xrules['SESSIONFLAGS'])
         elif i == "OFFICIALSERVER_i":
           if o_color:
             print(Fore.YELLOW + "Official Server:                 " + Fore.CYAN + xrules['OFFICIALSERVER_i'] + Style.RESET_ALL)
           else:
             print("Official Server:                 " + xrules['OFFICIALSERVER_i'])
         elif i == "SESSIONISPVE_i":
           if o_color:
             print(Fore.YELLOW + "Session Is PVE:                  " + Fore.CYAN + xrules['SESSIONISPVE_i'] + Style.RESET_ALL)
           else:
             print("Session Is PVE:                  " + xrules['SESSIONISPVE_i'])
         elif i == "ALLOWDOWNLOADITEMS_i":
           if o_color:
             print(Fore.YELLOW + "Allow Download Items:            " + Fore.CYAN + xrules['ALLOWDOWNLOADITEMS_i'] + Style.RESET_ALL)
           else:
             print("Allow Download Items:            " + xrules['ALLOWDOWNLOADITEMS_i'])
         elif i == "NUMOPENPUBCONN":
           if o_color:
             print(Fore.YELLOW + "Num Open Pub Connections:        " + Fore.CYAN + xrules['NUMOPENPUBCONN'] + Style.RESET_ALL)
           else:
             print("Num Open Pub Connections:        " + xrules['NUMOPENPUBCONN'])
         elif i == "SEARCHKEYWORDS_s":
           if o_color:
             print(Fore.YELLOW + "Search Keywords:                 " + Fore.CYAN + xrules['SEARCHKEYWORDS_s'] + Style.RESET_ALL)
           else:
             print("Search Keywords:                 " + xrules['SEARCHKEYWORDS_s'])
         elif i == "OWNINGNAME":
           if o_color:
             print(Fore.YELLOW + "Owning Name:                     " + Fore.CYAN + xrules['OWNINGNAME'] + Style.RESET_ALL)
           else:
             print("Owning Name:                     " + xrules['OWNINGNAME'])
         elif i == "DayTime_s":
           if o_color:
             print(Fore.YELLOW + "Daytime:                         " + Fore.CYAN + xrules['DayTime_s'] + Style.RESET_ALL)
           else:
             print("Daytime:                         " + xrules['DayTime_s'])
         elif i == "P2PPORT":
           if o_color:
             print(Fore.YELLOW + "P2P Port:                        " + Fore.CYAN + xrules['P2PPORT'] + Style.RESET_ALL)
           else:
             print("P2P Port:                        " + xrules['P2PPORT'])
         elif i == "ModId_l":
           if o_color:
             print(Fore.YELLOW + "Mod ID List:                     " + Fore.CYAN + xrules['ModId_l'] + Style.RESET_ALL)
           else:
             print("Mod ID List:                     " + xrules['ModId_l'])
         elif i == "Networking_i":
           if o_color:
             print(Fore.YELLOW + "Networking:                      " + Fore.CYAN + xrules['Networking_i'] + Style.RESET_ALL)
           else:
             print("Networking:                      " + xrules['Networking_i'])
         elif i == "GameMode_s":
           if o_color:
             print(Fore.YELLOW + "GameMode:                        " + Fore.CYAN + xrules['GameMode_s'] + Style.RESET_ALL)
           else:
             print("GameMode:                        " + xrules['GameMode_s'])
         elif i == "P2PADDR":
           if o_color:
             print(Fore.YELLOW + "P2P Address:                     " + Fore.CYAN + xrules['P2PADDR'] + Style.RESET_ALL)
           else:
             print("P2P Address:                     " + xrules['P2PADDR'])
         elif i == "CUSTOMSERVERNAME_s":
           if o_color:
             print(Fore.YELLOW + "Custom Server Name:              " + Fore.CYAN + xrules['CUSTOMSERVERNAME_s'] + Style.RESET_ALL)
           else:
             print("Custom Server Name:              " + xrules['CUSTOMSERVERNAME_s'])
         elif i == "OWNINGID":
           if o_color:
             print(Fore.YELLOW + "Owning ID:                       " + Fore.CYAN + xrules['OWNINGID'] + Style.RESET_ALL)
           else:
             print("Owning ID:                       " + xrules['OWNINGID'])
         elif i == "ServerPassword_b":
           if o_color:
             print(Fore.YELLOW + "Server Password:                 " + Fore.CYAN + xrules['ServerPassword_b'] + Style.RESET_ALL)
           else:
             print("Server Password:                 " + xrules['ServerPassword_b'])
         else:
           if o_color:
             print(Fore.YELLOW + "%-32s" % i + " " + Fore.CYAN + xrules[i] + Style.RESET_ALL)
           else:
             print("%-32s" % i + " " + xrules[i])
      if status == 1:
        servdown(o_color)

    if o_ping == True and o_server == True:
      status, result = query(ip,port,"ping")
      if o_header:
        header(o_color,"Server Ping")
      if status == 0:
        if o_color:
          print(Fore.YELLOW + "ping:                            " + Fore.CYAN + str(result).split(".")[0] + Style.RESET_ALL)
        else:
          print("ping:                            " + str(result).split(".")[0])
      if status == 1:
        servdown(o_color)

  if o_serverlist == True:
    if type == "o":
      url = "http://arkdedicated.com/officialservers.ini"
      file = urlopen(url)
      with concurrent.futures.ThreadPoolExecutor(max_workers=int(threads)) as executor:
        lock = threading.Lock()
        for line in file:
          decoded_line = line.decode("utf-8")
          host = decoded_line.split("\n")[0].split(" //")[0]
          for p in (27015,27017,27019,27021,27023):
            res = executor.submit(genoff, host, p, timeout, lock)
    elif type == "u":
      #masterserverquery()
      with valve.source.master_server.MasterServerQuerier() as msq:
        servers = msq.find(
            duplicates="skip",
            gamedir="ark_survival_evolved"
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(threads)) as executor:
          lock = threading.Lock()
          for host, port in servers:
            res = executor.submit(genunoff, host, port, timeout, lock)
    else:
      print("-k needs an argument: (o|u)")
      exit(0)
  if o_evo == True:
    if o_header:
      header(o_color,"Evolution Event")
    evo_event(o_color)

  if o_log == True and o_server == True:
    if o_watch == False:
      for server in slist:
        genlog(server, timeout, o_color)
    else:
      while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(threads)) as executor:
          lock = threading.Lock()
          for server in slist:
            res = executor.submit(tgenlog, server, timeout, o_color, lock)
        time.sleep(int(wtime))

if __name__ == "__main__":
  main()
