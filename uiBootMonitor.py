# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 09:22:48 2019

@author: ybendre
"""
import os
import subprocess as sp
from datetime import datetime as dt, timedelta as td
import json
import socket
import argparse
import sys
import inspect
import RCADataFilesUtility as RDF

bootDataJSON = '/var/log/vmware/BootData.json'
uiBootDataJSON = '/var/log/vmware/uiBootData.json'
mytextoutputfile = '/var/log/vmware/uiBootData.txt'
mytextoutputfile2 = '/var/log/vmware/uiPluginData.txt'
mydeltaoutputfile = '/var/log/vmware/uiDataDelta.txt'
mydeltaoutputfile2 = '/var/log/vmware/uiPluginDelta.txt'
uiLogFile = '/var/log/vmware/vsphere-ui/logs/vsphere-ui-runtime.log.stdout'
uiErrFile = '/var/log/vmware/vsphere-ui/logs/vsphere-ui-runtime.log.stderr'
uiVirgoFile = '/var/log/vmware/vsphere-ui/logs//vsphere_client_virgo.log'


corePluginFinishTime = None
corePluginFinishTimestamp = None

def runCommand(mycmd):
    print("Run Command: "+mycmd)
    try:
        d = str(sp.check_output(mycmd,shell=True))
        d = d.replace("b'","")
        d=d[:-1]
        print(d)    
        return d
    
    except Exception as e:
        print("runCommand failed: "+str(e))
        return None


def processed(uiPID):
    
    try:
        print("Check PID: "+uiPID)
        uiBootData = json.load(open(uiBootDataJSON,"r"))
        print(uiBootData)
        if "vspher-ui_"+str(uiPID) in uiBootData.keys():
            return(True)
        else:
            return(False)
    except Exception as e:
        print("processed failed: "+str(e)+". But it's ok, may be first run.")
        return(False)


def markProcessed(uiPID):
    uiBootData = {}
    try:
        uiBootData = json.load(open(uiBootDataJSON,"r"))
        
    except Exception as e:
        print("Mark Processed failed: "+str(e)+". But it's ok, may be first run.")
        uiBootData = {}
    
    try:
        uiBootData["vsphere-ui_"+str(uiPID)]="Done"
        json.dump(uiBootData,open(uiBootDataJSON,"w"))
    except Exception as e2:
        print("Mark Processed failed: "+str(e2))



def getuiTimesFromJson():
    
    uiData = json.load(open(bootDataJSON,"r"))
    myuiTimes = []
    myuiData ={}
    for p in uiData.keys():
        try:
#            print("Trying now")

            parts = p.split("_")
#            print(p)

#            print(parts)

            if parts[0]=='vsphere-ui':
                if processed(parts[1]):
                    continue
                print("Unprocessed instance")
                print(p)
                d1 = uiData[p]
                print(d1)
                mytimestamp = d1.split("|")[0].replace('\n','')
                print(mytimestamp)


                myuiTimes.append(int(mytimestamp))
                myuiData[mytimestamp]=d1
        except Exception as e3:
            print("getuiTimesFromJson failed: "+str(e3))
    
    myuiTimes.sort()
    print("Finished getuiTimesFromJson")
    return(myuiTimes,myuiData)
    
    

def parseCompTimes(mycomplogs,hostname,uiPID,uiPIDTime,uiStartTime):
    
    mycsvdata = None
    mytimeddata = {}
    try:
        
        uiPIDTime = dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f")
        uiStartTime = dt.strptime(uiStartTime,"%Y-%m-%d %H:%M:%S.%f")
        
        f = uiPIDTime.timestamp()
        t = uiStartTime.timestamp()
        mprevtimestamp = f
        mprevtime = uiPIDTime
        if(len(mycomplogs[-1])<2):
            mycomplogs = mycomplogs[:-1]
        mylen = len(mycomplogs)
        mnum = 0
        for m in mycomplogs:

            try:
                mnum = mnum + 1 
                #print(m)
                #[2019-07-15T15:59:07.653Z]
                if ":" not in m[:20]:
                    continue
                
                myprobabletimestamp = m.split(' ')[0]
                mtime = ''
                mtimestamp = 0
                if '[' in myprobabletimestamp:
                    mtime = myprobabletimestamp.replace("Z","").replace("T"," ").replace("[","").replace("]","")
                    mtimestamp = dt.strptime(mtime,"%Y-%m-%d %H:%M:%S.%f").timestamp()
                else:
                    myprobabletimestamp = str(uiStartTime).split(' ')[0] +' '+myprobabletimestamp
                    mtime = myprobabletimestamp.replace(",",".")
                    mtimestamp = dt.strptime(mtime,"%Y-%m-%d %H:%M:%S.%f").timestamp()
            
                if mtimestamp<f:
                    continue
                print("Log: "+str(m))
                mtimestamp0=""
                mcomp=""
                mtook=""
                mtime1 = ""
                mtime0 = ""
                if "End of configuration" in m:
                    mtimestamp0 = f
                    
                    mcomp = "Configuration" 
                    mtime1 = mtime
                    mtime0 = uiPIDTime
                    mtook = round(mtimestamp - mtimestamp0)
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                    
                elif "Registering current configuration" in m:
                    mtimestamp0 = mprevtimestamp
                    mcomp = "Register Configuration" 
                    mtime1 = mtime
                    mtime0 = mprevtime
                    mtook = round(mtimestamp - mtimestamp0)
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                
                elif "Platform bundles started" in m:
                    
                    mtimestamp0 = mprevtimestamp
                    mcomp = "Start Platform Bundles" 
                    mtime1 = mtime
                    mtime0 = mprevtime
                    mtook = round(mtimestamp - mtimestamp0)
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                
                elif "Core plugins deployed" in m:
                    mtimestamp0 = mprevtimestamp
                    mcomp = "Deploy Core Plugins" 
                    mtime1 = mtime
                    mtime0 = mprevtime
                    mtook = round(mtimestamp - mtimestamp0)
                    global corePluginFinishTime
                    global corePluginFinishTimestamp
                    
                    corePluginFinishTime = mtime1
                    corePluginFinishTimestamp = mtimestamp
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                
                elif mnum >= mylen:
                    #Last message
                    print("This may be last message too")
                    mtimestamp0 = mprevtimestamp
                    mcomp = "Deploy Other Plugins" 
                    mtime1 = mtime
                    mtime0 = mprevtime
                    mtook = round(mtimestamp - mtimestamp0)
                    
                    mprevtimestamp = mtimestamp
                    mprevtime = mtime1
                
                else:
                    continue
                
                
                if len(str(mprevtime))>25:
                        mprevtime = mprevtime[:-3]
                d1 = str(mtimestamp0)+"|"+str(hostname)+"|"+str(mcomp)+"|"+str(uiPID)+"|"+str(mtook)+"|"+str(mtime1)+"|"+str(mtime0)+"|"+str(mcomp)+"\n"
                print(d1)
                mytimeddata[mtimestamp0] = d1
                if d1 is not None:
                    if mycsvdata is None:
                        mycsvdata=""
                    mycsvdata = mycsvdata+d1
                
            except Exception as e2:
                print("parseCompTimes failed: "+str(e2))
        
        try:
            myout = runCommand('cat '+uiErrFile+' | grep -B 1 " ms"')
            messages = myout.split('\\n--\\n')
            for m in messages:
                try:
                    mytime1 = None
                    print(m)
                    if ' AM ' in m:
                        mytime1 = m.split(' AM ')[0]+' AM'
                    elif ' PM ' in m:
                        mytime1 = m.split(' PM ')[0]+' PM'
                
                    mytime1 = dt.strptime(mytime1,'%b %d, %Y %I:%M:%S %p')
                    mytimestamp1 = mytime1.timestamp()
                    mytime1 = str(mytime1)+'.000'
                
                    mytook = int(m.split(' ms')[0].split(' ')[-1])/1000
                    mycomp = m.split('INFO: ')[1].split(' in ')[0].replace("'","").title()
                    
                    mytimestamp0 = mytimestamp1 - mytook
                    mytime0 = dt.fromtimestamp(mytimestamp0)
                    
                    mytimestamp1 = round(mytimestamp1)
                    mytimestamp0 = round(mytimestamp0)
                    mytook = round(mytook)
                    d1 = str(mytimestamp0)+"|"+str(hostname)+"|"+str(mycomp)+"|"+str(uiPID)+"|"+str(mytook)+"|"+str(mytime1)+"|"+str(mytime0)+"|"+str(mycomp)+"\n"
                    mytimeddata[mytimestamp0] = d1
                except Exception as e4:
                    print('parseCompTimes failed: '+str(e4))
                
            
        except Exception as e3:
            print('parseCompTimes failed: during stderr file, '+str(e3))
        
        
        try:
            mytimelist = list(mytimeddata.keys())
            print(mytimelist)
            mytimelist.sort()
            mysortedcsvdata=None
            
            for t in mytimelist:
                if mysortedcsvdata is None:
                    mysortedcsvdata = ''
                mysortedcsvdata = mysortedcsvdata + mytimeddata[t]
            
            if mysortedcsvdata is not None:
                mycsvdata = mysortedcsvdata
        except Exception as e5:
            print('parseCompTimes failed: '+str(e5))
        
        
        return(mycsvdata,mytimeddata)
        
        
    except Exception as e:
        print("parseCompTimes failed: "+str(e))
        return(None)


def convertToDict(myoutend,myoutbegin):
    
    myplugindict = {}
    print('Converter')
    print('In '+str(inspect.stack()[0][3]))
    
    myoutbegin = myoutbegin.split("\\n")
    myoutend = myoutend.split("\\n")
    
    
    for p in myoutbegin:
        try:
            if len(p)<5:
                continue
        
            ptime = p.split(' ')[0][1:-1].replace('T',' ').replace('Z','')
            ptimestamp = dt.strptime(ptime,'%Y-%m-%d %H:%M:%S.%f').timestamp()
            pname = p.split('Params=')[1].split(',')[0]
            print('begin: '+pname)
            
            if pname not in myplugindict.keys():
                myplugindict[pname] = {'trials':[],'results':[],'next_processed_ind':0}
            
            myplugindict[pname]['trials'].append({'time':ptime,'timestamp':ptimestamp})
        
        except Exception as e1:
            print(str(inspect.stack()[0][3])+' failed: '+str(e1))
            
    for p in myoutend:
        try:
            if len(p)<5:
                continue
        
            ptime = p.split(' ')[0][1:-1].replace('T',' ').replace('Z','')
            ptimestamp = dt.strptime(ptime,'%Y-%m-%d %H:%M:%S.%f').timestamp()
            pname = p.split('Params=')[1].split(',')[0]
            print('End '+pname)
            if pname not in myplugindict.keys():
                continue
            
            
            mybegintimestamp = myplugindict[pname]['trials'][myplugindict[pname]['next_processed_ind']]['timestamp']
            mybegintime = myplugindict[pname]['trials'][myplugindict[pname]['next_processed_ind']]['time']
            ptook = ptimestamp - mybegintimestamp
            print(myplugindict[pname])
            
            if(ptook<0):
                continue
            print('Found')
            verdict = 'Success'
            if 'PACKAGE_DEPLOY_FAIL' in p:
                verdict = 'Fail'
                
            myplugindict[pname]['results'].append({'begintime':mybegintime,'begintimestamp':mybegintimestamp,'endtime':ptime,'endtimestamp':ptimestamp,'took':ptook,'verdict':verdict})
            myplugindict[pname]['next_processed_ind'] = myplugindict[pname]['next_processed_ind']+1
        
        except Exception as e2:
            print(str(inspect.stack()[0][3])+' failed: '+str(e2))
        
    
    return myplugindict
    
    
  
def parsePluginTimes(mycomplogs,hostname,uiPID,uiPIDTime,uiStartTime):
    
    mycsvdata = None
    mytimeddata = {}
    try:
        
        uiPIDTime = dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f")
        uiStartTime = dt.strptime(uiStartTime,"%Y-%m-%d %H:%M:%S.%f")
        
        f = uiPIDTime.timestamp()
        t = uiStartTime.timestamp()
        myoutend = runCommand('cat '+uiVirgoFile+' | grep "PACKAGE_DEPLOY_END\|PACKAGE_DEPLOY_FAIL"')
#        myoutfail = runCommand('cat '+uiVirgoFile+' | grep "PACKAGE_DEPLOY_FAIL"')
        myoutbegin = runCommand('cat '+uiVirgoFile+' | grep "PACKAGE_DEPLOY_BEGIN"')
        print('Got all the data needed')
        myplugindict = convertToDict(myoutend,myoutbegin)
        print('Got plugin dict')
        print(myplugindict)
        
        for pname in myplugindict.keys():
            print('Plugin '+pname)
            for p in myplugindict[pname]['results']:
                print('Data '+str(p))
                try:
                    
                    if p['begintimestamp']<f:
                        continue
                    
                    print("Log: "+str(pname)+" "+str(p))
                    d1 = str(round(p['begintimestamp']))+"|"+str(hostname)+"|"+str(pname)+"|"+str(uiPID)+"|"+str(round(p['took']))+"|"+str(p['endtime'])+"|"+str(p['begintime'])+'|'+str(pname)+" ("+str(p['verdict'])+")\n"
                    print(d1)
                    timekey = round(p['begintimestamp'])
                    if timekey not in mytimeddata:
                        mytimeddata[timekey] = ""
                    mytimeddata[timekey] = mytimeddata[timekey] + d1
                except Exception as e2:
                    print("parsePluginTimes failed: "+str(e2))
            
        mysortedtime=list(mytimeddata.keys())
        mysortedtime.sort()
        
        for t in mysortedtime:
            if mycsvdata is None:
                mycsvdata = ''
            mycsvdata = mycsvdata+mytimeddata[t]
        
        
        
        return(mycsvdata,mytimeddata)
        
        
    except Exception as e:
        print("parsePluginTimes failed: "+str(e))
        return(None,None)
    


def mergedCSV(mytimeddata1,mytimeddata2):
    mytimes1=list(mytimeddata1.keys())
    mytimes1.sort()
    mytimes2=list(mytimeddata2.keys())
    mytimes2.sort()
    
    i=0
    j=0
    print("Merge Data")
    mycsvdata = ''
    mycorecsv = ''
    myothercsv = ''
    isCore = True
    smallerTimestamp = None
    while(i<len(mytimes1) and j<len(mytimes2)):
        datatoAppend = ''
        if(mytimes1[i]<mytimes2[j]):
            smallerTimestamp = mytimes1[i]
            datatoAppend = mytimeddata1[mytimes1[i]]
            i=i+1
        else:
            smallerTimestamp = mytimes2[j]
            datatoAppend = mytimeddata2[mytimes2[j]]
            j=j+1
        print(datatoAppend)
        mycsvdata = mycsvdata + datatoAppend
        if smallerTimestamp > corePluginFinishTimestamp:
            print("Core plugins are over here")
        #if 'Deploy Other Plugins' in datatoAppend:
            isCore = False
        if isCore:
            mycorecsv = mycorecsv + datatoAppend
        else:
            myothercsv = myothercsv + datatoAppend
    
    while(i<len(mytimes1)):
        mycsvdata = mycsvdata + mytimeddata1[mytimes1[i]]
        
        if mytimes1[i] > corePluginFinishTimestamp:
        #if 'Deploy Other Plugins' in mytimeddata1[mytimes1[i]]:
            isCore = False
        if isCore:
            mycorecsv = mycorecsv + mytimeddata1[mytimes1[i]]
        else:
            myothercsv = myothercsv + mytimeddata1[mytimes1[i]]
    
        i=i+1
            
    while(j<len(mytimes2)):
        mycsvdata = mycsvdata + mytimeddata2[mytimes2[j]]
        if mytimes2[j] > corePluginFinishTimestamp:
        #if 'Deploy Other Plugins' in mytimeddata2[mytimes2[j]]:
            isCore = False
        if isCore:
            mycorecsv = mycorecsv + mytimeddata2[mytimes2[j]]
        else:
            myothercsv = myothercsv + mytimeddata2[mytimes2[j]]
    
        j=j+1
    
    if len(mycsvdata)<5:
        return (None,None,None)
    else:
        return (mycsvdata,mycorecsv,myothercsv)
    




def getuiComponentTimesFromUiFile(hostname,uiPID,uiPIDTime,uiStartTime):
    csvdata = None
    
    try:
        
        mylogs = ""
        with open(uiLogFile,"r") as fp:
            mylogs = fp.read().split("\n")
        csvdata,mytimeddata1 = parseCompTimes(mylogs,hostname,uiPID,uiPIDTime,uiStartTime)
        mylogs = runCommand('cat '+uiLogFile+' | grep "Type=START"').split('\\n')
        csvdata2,mytimeddata2 = parsePluginTimes(mylogs,hostname,uiPID,uiPIDTime,uiStartTime)
        
        try:
            mergeddata,mycorecsv,myothercsv = mergedCSV(mytimeddata1,mytimeddata2)
            csvdata2 = mergeddata
        except Exception as e2:
            print('mergedCSV failed: '+str(e2))
            
    
    except Exception as e:
        print("getuiComponentTimesFromUiFile faile: "+str(e))    
    
    return(csvdata,csvdata2,mycorecsv,myothercsv)
            
def grepUiComponentTimes(hostname):            
    csvdata = None
    try:
        
        myuiTimes,myuiData = getuiTimesFromJson()
        mycsvdata = ""
        print(myuiTimes)
        
        print(myuiData)
        
        t = myuiTimes[-1]
        uiRestartInstance = myuiData[str(t)]
        print("Processing: "+uiRestartInstance)        
        mytimedata = uiRestartInstance.split('|')
        uiStartTime = mytimedata[-2].replace("\n","")
        uiPIDTime = mytimedata[-1].replace("\n","")
        uiPID = mytimedata[3].replace("\n","")
        
        if processed(uiPID):
            print("Already Processed PID: "+uiPID)
            return(None, None, None, None)
        
        print(str(uiPID)+" "+uiPIDTime+" "+uiStartTime)
        uiTook = round(dt.strptime(uiStartTime,"%Y-%m-%d %H:%M:%S.%f").timestamp()-dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())
        print("Received my data")
        csvdata,plugindata,mycorecsvdata,myothercsvdata = getuiComponentTimesFromUiFile(hostname,uiPID,uiPIDTime,uiStartTime)
        uidt = ""+str(dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())+"|"+str(hostname)+"|vsphere-ui Green|"+str(uiPID)+"|"+str(uiTook)+"|"+str(uiStartTime)[:-3]+"|"+str(uiPIDTime)[:-3]+"|Service vsphere-ui Green"
        
        try:
            print("CorePluginTimes: ")
            print(corePluginFinishTime)
            print(corePluginFinishTimestamp)
            if corePluginFinishTime is not None:
                uiTook = round(corePluginFinishTimestamp-dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())
                cpft = str(dt.strptime(uiPIDTime,"%Y-%m-%d %H:%M:%S.%f").timestamp())+"|"+str(hostname)+"|vsphere-ui|"+str(uiPID)+"|"+str(uiTook)+"|"+str(corePluginFinishTime)+"|"+str(uiPIDTime)[:-3]+"|Core Plugins of vsphere-ui Started"
                uidt = cpft + "\n" + uidt
        except Exception as e10:
            print("Couldn't get coreplugin finish time : "+str(e10))
        
        print("Received CSV Data")
        if csvdata is not None:
            csvdata = uidt+"\n"+csvdata
            markProcessed(uiPID)
        
        if plugindata is not None:
            plugindata = uidt+"\n"+plugindata
        
        if mycorecsvdata is not None:
            mycorecsvdata = uidt+"\n"+mycorecsvdata
        
        
        #print(csvdata)    
        
        return(csvdata,plugindata,mycorecsvdata,myothercsvdata)
            
        

    except Exception as e:
        print("grepuiComponentTimes failed: "+str(e))            
        
if __name__ == "__main__":

    vcName = "localhost"
    outputFolder = "/var/log/vmware/"
    helpstring = "Options: -v <vcname> -f <output folder path>"
    opts = None
    args = None
    
    try:
        vcName = socket.gethostname()
    except Exception as e0:
        print(str(e0))
    
    
    
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--vcName", help="Specify vCenter Name. Default: system hostname",type=str)
    parser.add_argument("-f","--folder", type=str,help="Specify output folder. Default: /var/log/vmware")
    parser.add_argument("-d","--deltafile", type=str,help="Specify path for delta file.")
    parser.add_argument("-e","--plugindeltafile", type=str,help="Specify path for plugin delta file.")
    
    args = parser.parse_args()
    
    if args.folder:
        outputFolder = args.folder
        if(outputFolder[-1]!='/'):
            outputFolder=outputFolder+'/'
        mytextoutputfile = outputFolder+'uiBootData.txt'
        mytextoutputfile2 = outputFolder+'uiPluginData.txt'
        #myjsonoutputfile = outputFolder+'BootData.json'
    if args.deltafile:
        #deltaoutputFolder = args.deltafolder
        #if(deltaoutputFolder[-1]!='/'):
#            deltaoutputFolder=deltaoutputFolder+'/'
        mydeltaoutputfile = args.deltafile
        #myjsonoutputfile = outputFolder+'BootData.json'

    if args.plugindeltafile:
        #deltaoutputFolder = args.deltafolder
        #if(deltaoutputFolder[-1]!='/'):
#            deltaoutputFolder=deltaoutputFolder+'/'
        mydeltaoutputfile2 = args.plugindeltafile
        
    if args.vcName:
        vcName = args.vcName
    
    try:
        #pushHeaderAndCreateFile()
        mycsvdata,myplugindata,mycorecsvdata,myothercsvdata = grepUiComponentTimes(vcName)
        
        
        #myheader = 'date|vcName|component|pid|boot_time_in_sec|last_started_at|last_triggered_at\n'
        myheader = 'date|vcName|component|pid|boot_time_in_sec|last_started_at|last_triggered_at|status\n'
        if mycsvdata is not None:
            #RDF.pushToDeltaFile(mydeltaoutputfile,myheader,mycsvdata)
            RDF.pushToFullFile(mytextoutputfile,myheader,mycsvdata)
        
        if myplugindata is not None:
            print(myplugindata)
            #RDF.pushToDeltaFile(mydeltaoutputfile2,myheader,myplugindata)
            RDF.pushToFullFile(mytextoutputfile2,myheader,myplugindata)
            
            mytextoutputfile3 = mytextoutputfile2.replace('Plugin','CorePlugin')
            RDF.pushToFullFile(mytextoutputfile3,myheader,mycorecsvdata)
            mytextoutputfile4 = mytextoutputfile2.replace('Plugin','OtherPlugin')
            RDF.pushToFullFile(mytextoutputfile4,myheader,myothercsvdata)
            RDF.pushToDeltaFile(mydeltaoutputfile,myheader,mycorecsvdata)
            RDF.pushToDeltaFile(mydeltaoutputfile2,myheader,myothercsvdata)
        
        
        
    
    except Exception as e:
        print("ui component data collection failed: "+str(e))
        
    
    

