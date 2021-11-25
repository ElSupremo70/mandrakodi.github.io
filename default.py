# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# XBMC entry point
# ------------------------------------------------------------

import os
import sys
import re
import xbmc
import xbmcaddon
import xbmcgui
import logging


addon_id = 'plugin.video.mandrakodi'
#selfAddon = xbmcaddon.Addon(id=addon_id)
debug = xbmcaddon.Addon(id=addon_id).getSetting("debug")

PY3 = sys.version_info[0] == 3

def logga(mess):
    if debug == "on":
        logging.warning('MANDRA_LOG: '+mess)

def getStartUrl():
    import json
    urlStart = ""
    urlBin="https://w3ubin.com/-gJWp2-gG.w3u"
    
    strJson = makeRequest(urlBin)
    if (strJson != ""):
        dataJson = json.loads(strJson)
        urlStart = dataJson["groups"][0]["stations"][3]["url"]

    return urlStart

def checkLauncher():
    home = ''
    if PY3:
        home = xbmc.translatePath(xbmcaddon.Addon(id=addon_id).getAddonInfo('path'))
    else:
        home = xbmc.translatePath(xbmcaddon.Addon(id=addon_id).getAddonInfo('path').decode('utf-8'))
    launcher_file = os.path.join(home, 'launcher.py')
    if os.path.exists(launcher_file)==True:
        resF = open(launcher_file)
        resolver_content = resF.read()
        resF.close()
        local_vers = re.findall("versione='(.*)'",resolver_content)[0]
        logga('local_vers '+local_vers)


        remoteLauncherUrl = xbmcaddon.Addon(id=addon_id).getSetting("baseUrl")
        w3ubinLauncherUrl = getStartUrl()
        if (w3ubinLauncherUrl != "" and remoteLauncherUrl != w3ubinLauncherUrl):
            remoteLauncherUrl = w3ubinLauncherUrl
            #xbmcaddon.Addon(id=addon_id).setSetting("baseUrl", remoteLauncherUrl)
            logga('BASE URL CHANGE '+remoteLauncherUrl)

        strSource = makeRequest(remoteLauncherUrl)
        if strSource is None or strSource == "":
            logga('We failed to get source from '+remoteLauncherUrl)
            msgBox("Non è stato possibile contattare la sorgente.[CR]L'addon potrebbe non essere aggiornato.")
            remote_vers = local_vers
        else:
            remote_vers = re.findall("versione='(.*)'",strSource)[0]
        logga('remote_vers '+remote_vers)
        if local_vers != remote_vers:
            logga('TRY TO UPDATE VERSION')
            f = open(launcher_file, "w")
            f.write(strSource)
            f.close()
            logga('VERSION UPDATE')
            msgBox("Codice Launcher aggiornato alla versione: "+remote_vers)

def makeRequest(url, hdr=None):
    html = ""
    if PY3:
	    import urllib.request as myRequest
    else:
	    import urllib2 as myRequest

    pwd = xbmcaddon.Addon(id=addon_id).getSetting("password")
    version = xbmcaddon.Addon(id=addon_id).getAddonInfo("version")
    if hdr is None:
        ua = "MandraKodi2@@"+version+"@@"+pwd
        hdr = {"User-Agent" : ua}
    try:
        req = myRequest.Request(url, headers=hdr)
        response = myRequest.urlopen(req)
        html = response.read().decode('utf-8')
        response.close()
    except:
        logga('Error to open url')
        pass
    return html

def msgBox(mess):
    dialog = xbmcgui.Dialog()
    dialog.ok("MandraKodi", mess)

if sys.argv[2] == "":
    logga("OPEN ADDON")
    checkLauncher()

logga("CALL PAR - "+sys.argv[2])
try:
    import launcher
    launcher.run()
except Exception as err:
    import traceback
    errMsg="ERROR_MANDRAKODI: {0}".format(err)
    logging.warning(errMsg+"\nPAR_ERR --> ")
    traceback.print_exc()
    dialog = xbmcgui.Dialog()
    mess = "Accidenti!\nSembra che la fonte selezionata non funzioni.\nProva a cambiare 'Fonte/Lista/Sezione'.\nSe il problema persiste, contatta il gruppo di supporto @mandrakodihelp."
    dialog.ok("Mandrakodi", mess)