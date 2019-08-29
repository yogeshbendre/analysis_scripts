# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 11:58:23 2019

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
import BootDataUtility as BDT
#import BDT as BDT

serviceName=None
ServiceBootDataJSON = '/var/log/vmware/serviceBootData.json'
mytextoutputfile = '/var/log/vmware/uiBootData.txt'
mytextoutputfile2 = '/var/log/vmware/uiPluginData.txt'
mydeltaoutputfile = '/var/log/vmware/uiDataDelta.txt'
mydeltaoutputfile2 = '/var/log/vmware/uiPluginDelta.txt'
vcName = None
myPID = 0



def getTomcatTimeOfService(sname):
    sname = sname.lower()
    sname = sname.replace("vmware-","").replace("-","_")
    myf = getattr(sys.modules[__name__], "getTomcatTimeOf_%s" % sname)
    mycsv=myf()
    print("Recieved csv : "+str(mycsv))
    return(mycsv)


def getServiceComponentTimes(serviceName):
    
    try:
        mycsv = getTomcatTimeOfService(serviceName)
        print("Completed "+serviceName)
        return mycsv
    except Exception as e:
        print("getServiceComponentTime failed for : "+serviceName+" -> "+str(e))
        return None
    


def getLatestFile(folder,fname_pattern):
    d = BDT.runCommand("ls -lrt "+folder+" | grep "+fname_pattern)
    if "\\n" in d:
        d = d.split("\\n")[-2].split(" ")[-1]
    else:
        d = d.split("\n")[-2].split(" ")[-1]
    return d


def getFromCatalinaFile(catalinaFile):
    global vcName
    global myPID
    hostname = vcName
    mycsvdata = None
    try:
            myout = BDT.runCommand('cat '+catalinaFile+' | grep " Initialization processed in"')
            m = myout.split('\\n')[-2]
            try:
                mytime1 = m.split(" ")[0].replace("T"," ").replace("Z","")
                print("Log: "+m)
                mytime1 = dt.strptime(mytime1,'%Y-%m-%d %H:%M:%S.%f')
                mytimestamp1 = mytime1.timestamp()
                mytime1 = str(mytime1)+'.000'
            
                mytook = int(m.split(' ms')[0].split(' ')[-1])/1000
                mycomp = "Initialization Processed"
                
                mytimestamp0 = mytimestamp1 - mytook
                mytime0 = dt.fromtimestamp(mytimestamp0)
                
                mytimestamp1 = round(mytimestamp1)
                mytimestamp0 = round(mytimestamp0)
                mytook = round(mytook)
                d1 = str(mytimestamp0)+"|"+str(hostname)+"|"+str(mycomp)+"|"+str(myPID)+"|"+str(mytook)+"|"+str(mytime1)+"|"+str(mytime0)+"|"+str(mycomp)+" (Catalina)\n"
                print("New Entry: "+d1)
                
                if mycsvdata is None:
                    mycsvdata = ''
                mycsvdata = mycsvdata+d1
            except Exception as e4:
                print('getFromCatalinaFile failed: '+str(e4))
            
            
    except Exception as e3:
        print('getFromCatalinaFile failed: '+str(e3))
    
    
    try:
            myout = BDT.runCommand('cat '+catalinaFile+' | grep " Server startup in"')
            m = myout.split('\\n')[-2]
            try:
                mytime1 = m.split(" ")[0].replace("T"," ").replace("Z","")
                print("Log: "+m)
                mytime1 = dt.strptime(mytime1,'%Y-%m-%d %H:%M:%S.%f')
                mytimestamp1 = mytime1.timestamp()
                mytime1 = str(mytime1)+'.000'
            
                mytook = int(m.split(' ms')[0].split(' ')[-1])/1000
                mycomp = "Server Startup"
                
                mytimestamp0 = mytimestamp1 - mytook
                mytime0 = dt.fromtimestamp(mytimestamp0)
                
                mytimestamp1 = round(mytimestamp1)
                mytimestamp0 = round(mytimestamp0)
                mytook = round(mytook)
                d1 = str(mytimestamp0)+"|"+str(hostname)+"|"+str(mycomp)+"|"+str(myPID)+"|"+str(mytook)+"|"+str(mytime1)+"|"+str(mytime0)+"|"+str(mycomp)+" (Catalina)\n"
                print("New Entry: "+d1)
                
                if mycsvdata is None:
                    mycsvdata = ''
                mycsvdata = mycsvdata+d1
            except Exception as e4:
                print('getFromCatalinaFile failed: '+str(e4))
            
            
    except Exception as e3:
        print('getFromCatalinaFile failed: '+str(e3))
    
    
    
    return mycsvdata
    



def getFromStdErrFile(errFile):
    global vcName
    global myPID
    hostname = vcName
    mycsvdata = None
    try:
            myout = BDT.runCommand('cat '+errFile+' | grep -B 1 " ms"')
            messages = myout.split('\\n--\\n')
            for m in messages:
                try:
                    mytime1 = None
                    print("Log: "+m)
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
                    d1 = str(mytimestamp0)+"|"+str(hostname)+"|"+str(mycomp)+"|"+str(myPID)+"|"+str(mytook)+"|"+str(mytime1)+"|"+str(mytime0)+"|"+str(mycomp)+" (stderr)\n"
                    print("New Entry: "+d1)
                    
                    if mycsvdata is None:
                        mycsvdata = ''
                    mycsvdata = mycsvdata+d1
                except Exception as e4:
                    print('getFromStdErrFile failed: '+str(e4))
                
            
    except Exception as e3:
        print('getFromStdErrFile failed: during stderr file, '+str(e3))
    
    return mycsvdata
        

def grepIntoFile(filepath,pattern):
    myout = BDT.runCommand('cat '+filepath+' | grep "'+pattern+'"')
    print("Myoutput: "+myout)
    
    if '\\n' in myout:
        myout = myout.split("\\n")
    else:
        myout = myout.split('\n')
        
    
    myout = myout[:-1]
    print(len(myout))
    #print(myout)
    return myout
    
def getCLSEvents(logFile):
    mydict = {}
    #filename = "/root/ysbcls/cls.log"
    filename = logFile
    
    try:
        #Loading XML bean definitions
        myout = grepIntoFile(filename,"Loading XML bean definitions")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Loading XML bean definitions")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getCLSEvents failed for Package: "+str(e1))
        
    try:
        #Initializing
        myout = grepIntoFile(filename,"Initializing")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Initializing")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getCLSEvents failed for Initializing: "+str(e1))
        
    
    try:
        #Initializing
        myout = grepIntoFile(filename,"Registered the service")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Register Services")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getCLSEvents failed for Package: "+str(e1))
        
    try:
        #Server
        myout = grepIntoFile(filename,"TcServer")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Start Server")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getCLSEvents failed for Package: "+str(e1))
    mycsv = None
    try:
        mycsv = ''
        mytimes = list(mydict.keys())
        mytimes.sort()
        
        for t in mytimes:
            mycsv = mycsv + mydict[t]
        print("Built CSV Data:")
        print(mycsv)
        return mycsv
    except Exception as e6:
        print("getCLSEvents failed to sort:"+str(e6))
    
    

def getSVCSEvents(logFile):
    mydict = {}
    #filename = "/root/ysbcls/cls.log"
    filename = logFile
    
    try:
        #Loading XML bean definitions
        myout = grepIntoFile(filename,"Loading XML bean definitions")
        print(len(myout))
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Loading XML bean definitions")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getSVCSEvents failed for Package: "+str(e1))
        
    try:
        #Initializing
        myout = grepIntoFile(filename,"Initializing")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Initializing")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getCLSEvents failed for Initializing: "+str(e1))
        
    
    try:
        #Initializing
        myout = grepIntoFile(filename,"Registered the service")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Register Services")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getSVCSEvents failed for Package: "+str(e1))
        
    try:
        #Server
        myout = grepIntoFile(filename,"Server startup time:")
        msg = myout[0]
        print("My Message")
        print(msg)
        msg, mt = computeSingleSEventTime(msg,"Start Server"," ms")
        mydict[mt] = msg
    except Exception as e1:
        print("getSVCSEvents failed for Package: "+str(e1))
    mycsv = None
    try:
        mycsv = ''
        mytimes = list(mydict.keys())
        mytimes.sort()
        
        for t in mytimes:
            mycsv = mycsv + mydict[t]
        print("Built CSV Data:")
        print(mycsv)
        return mycsv
    except Exception as e6:
        print("getCLSEvents failed to sort:"+str(e6))
    


def getvSanHealthEvents(logFile):
    mydict = {}
    filename = logFile
    
    try:
        #Loaded bindings
        myout = grepIntoFile(filename,"Loaded bindings")
        print(len(myout))
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Loaded bindings")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getSVCSEvents failed for Package: "+str(e1))
        
    try:
        #Importing
        myout = grepIntoFile(filename," Importing")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Imports")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getCLSEvents failed for Initializing: "+str(e1))
        
    
    try:
        #Initialized
        myout = grepIntoFile(filename," Initialized")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Initialization")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getSVCSEvents failed for Package: "+str(e1))
        
    try:
        #started.
        myout = grepIntoFile(filename," started\.")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Server Started")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getSVCSEvents failed for Package: "+str(e1))
    
    mycsv = None
    try:
        mycsv = ''
        mytimes = list(mydict.keys())
        mytimes.sort()
        
        for t in mytimes:
            mycsv = mycsv + mydict[t]
        print("Built CSV Data:")
        print(mycsv)
        return mycsv
    except Exception as e6:
        print("getvSanHealthEvents failed to sort:"+str(e6))
    



def getSPSEvents(logFile):
    mydict = {}
    #filename = "/var/core/temp/sps.log.1"
    filename = logFile
    
    try:
        #Package Loads
        myout = grepIntoFile(filename," Package")
        msg,mt = computeSPSEventTime(myout[0],myout[-1],"Package Loading")
        print("My Message")
        print(msg)
        mydict[mt] = msg
    except Exception as e1:
        print("getSPSEvents failed for Package: "+str(e1))
        
    try:
        #Datastore processing
        myout = grepIntoFile(filename,"\[main\].*FCD Datastore Initialized")
        mydslen = len(myout)
        m1 = myout[0]
        myout = grepIntoFile(filename,"Added FCDDatastore")
        m2 = myout[-1]
        msg,mt = computeSPSEventTime(m1,m2,"Initialize and Add "+str(mydslen)+" Datastores")
        print("My Message")
        print(msg)
        
        mydict[mt] = msg
    except Exception as e2:
        print("getSPSEvents failed for Datastore Processing:"+str(e2))
        
    try:    
        #PBM
        myout = grepIntoFile(filename,"Starting PBM container")
        m1 = myout[0]
        
        myout = grepIntoFile(filename,"Starting background jobs in PBM")
        m2 = myout[0]
        
        msg,mt = computeSPSEventTime(m1,m2,"PBM Service")
        print("My Message")
        print(msg)
        
        mydict[mt] = msg
    except Exception as e3:
        print("getSPSEvents failed for PBM: "+str(e3))
    
    try:    
        #SMS
        myout = grepIntoFile(filename,"Starting SMS container")
        m1 = myout[0]
        
        myout = grepIntoFile(filename,"vCenter Storage Monitoring Service initialized successfully")
        m2 = myout[0]
        
        msg,mt = computeSPSEventTime(m1,m2,"SMS Service")
        print("My Message")
        print(msg)
        
        mydict[mt] = msg
    except Exception as e4:
        print("getSPSEvents failed for SMS:" + str(e4))
    
    try:
        #VSLM
        myout = grepIntoFile(filename,"Starting VSLM container")
        m1 = myout[0]
        
        myout = grepIntoFile(filename,"Starting background jobs in VSLM")
        m2 = myout[-1]
        msg,mt = computeSPSEventTime(m1,m2,"VSLM Service")
        print("My Message")
        print(msg)
        
        mydict[mt] = msg
    except Exception as e5:
        print("getSPSEvents failed for VSLM:"+str(e5))
    
    mycsv = None
    try:
        mycsv = ''
        mytimes = list(mydict.keys())
        mytimes.sort()
        
        for t in mytimes:
            mycsv = mycsv + mydict[t]
        print("Built CSV Data:")
        print(mycsv)
        return mycsv
    except Exception as e6:
        print("getSPSEvents failed to sort:"+str(e6))
    

def computeSPSEventTime(m1,m2,mycomp):
    global vcName
    global myPID
    hostname = vcName
    print("First: "+m1)
    print("Second: "+m2)
    mytime1 = m1.split(" ")[0].replace("T"," ").replace("Z","")
    mytime1 = dt.strptime(mytime1,'%Y-%m-%d %H:%M:%S.%f')
    mytimestamp1 = mytime1.timestamp()
    mytime1 = str(mytime1)
    
    mytime2 = m2.split(" ")[0].replace("T"," ").replace("Z","")
    mytime2 = dt.strptime(mytime2,'%Y-%m-%d %H:%M:%S.%f')
    mytimestamp2 = mytime2.timestamp()
    mytime2 = str(mytime2)
    
    mytook = round(mytimestamp2-mytimestamp1)
    d1 = str(round(mytimestamp1))+"|"+str(hostname)+"|"+str(mycomp)+"|"+str(myPID)+"|"+str(mytook)+"|"+str(mytime2)+"|"+str(mytime1)+"|"+str(mycomp)+"\n"            
    print(d1)
    return (d1,mytimestamp1)


def computeSingleSEventTime(m1,mycomp,pattern):
    global vcName
    global myPID
    hostname = vcName
    
    mytime2 = m1.split(" ")[0].replace("T"," ").replace("Z","")
    mytime2 = dt.strptime(mytime2,'%Y-%m-%d %H:%M:%S.%f')
    mytimestamp2 = mytime2.timestamp()
    mytime2 = str(mytime2)
    
    mytook = int(m1.split(pattern)[0].split(" ")[-1])
    
    mytimestamp1 = (1000*mytimestamp2 - mytook)/1000
    mytime1 = str(dt.fromtimestamp(mytimestamp1))
    
    mytook = round(mytook/1000)
    
    d1 = str(round(mytimestamp1))+"|"+str(hostname)+"|"+str(mycomp)+"|"+str(myPID)+"|"+str(mytook)+"|"+str(mytime2)+"|"+str(mytime1)+"|"+str(mycomp)+"\n"            
    
    return (d1,mytimestamp1)



def getFromvSanHealthLogFile(logFile):
    mycsvdata = None
    try:
            mycsvdata = getvSanHealthEvents(logFile)
            return mycsvdata
            
            
            
    except Exception as e3:
        print('getFromvSanHealthLogFile failed: '+str(e3))
    
    return mycsvdata

def getFromSPSLogFile(logFile):
    mycsvdata = None
    try:
            mycsvdata = getSPSEvents(logFile)
            return mycsvdata
            
            
            
    except Exception as e3:
        print('getFromSPSLogFile failed: '+str(e3))
    
    return mycsvdata




def getFromSVCSLogFile(logFile):
    mycsvdata = None
    try:
            mycsvdata = getSVCSEvents(logFile)
            return mycsvdata
            
            
            
    except Exception as e3:
        print('getFromSVCSLogFile failed: '+str(e3))
    
    return mycsvdata

def getFromCLSLogFile(logFile):
    mycsvdata = None
    try:
            mycsvdata = getCLSEvents(logFile)
            return mycsvdata
            
            
            
    except Exception as e3:
        print('getFromCLSLogFile failed: '+str(e3))
    
    return mycsvdata


def getTomcatTimeOf_lookupsvc():
    global serviceName
    global myPID
    global ServiceBootDataJSON
    mycsv = None
    mybootInfo,myrestartInstance = BDT.getLastBootInstance(serviceName)
    if mybootInfo is None:
        print("Could not find info about lookupsvc")
        return None
    else:
        print(mybootInfo)
        myPID = mybootInfo['PID']
        
        if(BDT.processed(myPID,ServiceBootDataJSON,serviceName)):
            print("Already processed latest instance: "+myrestartInstance)
            return None
        
        errFile = getLatestFile("/var/log/vmware/lookupsvc/","stderr")
        errFile = "/var/log/vmware/lookupsvc/"+errFile
        print(errFile)
        mycsv = getFromStdErrFile(errFile)
        mycsv=myrestartInstance+"|lookupsvc green (vmon)\n"+mycsv
        
        BDT.markProcessed(myPID,ServiceBootDataJSON,serviceName)
        
        
        
        return mycsv



def getTomcatTimeOf_eam():
    global serviceName
    global myPID
    global ServiceBootDataJSON
    mycsv = None
    mybootInfo,myrestartInstance = BDT.getLastBootInstance(serviceName)
    if mybootInfo is None:
        print("Could not find info about lookupsvc")
        return None
    else:
        print(mybootInfo)
        myPID = mybootInfo['PID']
        
        if(BDT.processed(myPID,ServiceBootDataJSON,serviceName)):
            print("Already processed latest instance: "+myrestartInstance)
            return None
        
        #errFile = getLatestFile("/var/log/vmware/eam/","stderr")
        errFile = "/var/log/vmware/eam/jvm.log.stderr"
        print(errFile)
        mycsv = getFromStdErrFile(errFile)
        mycsv=myrestartInstance+"|eam green (vmon)\n"+mycsv
        
        BDT.markProcessed(myPID,ServiceBootDataJSON,serviceName)
        
        
        
        return mycsv



def getTomcatTimeOf_sps():
    global serviceName
    global myPID
    global ServiceBootDataJSON
    mycsv = None
    mybootInfo,myrestartInstance = BDT.getLastBootInstance(serviceName)
    if mybootInfo is None:
        print("Could not find info about lookupsvc")
        return None
    else:
        print(mybootInfo)
        myPID = mybootInfo['PID']
        
        if(BDT.processed(myPID,ServiceBootDataJSON,serviceName)):
            print("Already processed latest instance: "+myrestartInstance)
            return None
        
        #errFile = getLatestFile("/var/log/vmware/lookupsvc/","stderr")
        logFile = "/var/log/vmware/vmware-sps/sps.log"
        print(logFile)
        mycsv = getFromSPSLogFile(logFile)
        mycsv=myrestartInstance+"|sps green (vmon)\n"+mycsv
        
        BDT.markProcessed(myPID,ServiceBootDataJSON,serviceName)
        
        
        
        return mycsv

def getTomcatTimeOf_vsan_health():
    global serviceName
    global myPID
    global ServiceBootDataJSON
    mycsv = None
    mybootInfo,myrestartInstance = BDT.getLastBootInstance(serviceName)
    if mybootInfo is None:
        print("Could not find info about lookupsvc")
        return None
    else:
        print(mybootInfo)
        myPID = mybootInfo['PID']
        
        if(BDT.processed(myPID,ServiceBootDataJSON,serviceName)):
            print("Already processed latest instance: "+myrestartInstance)
            return None
        
        #errFile = getLatestFile("/var/log/vmware/lookupsvc/","stderr")
        logFile = "/var/log/vmware/vsan-health/vmware-vsan-health-service.log"
        #logFile = "/var/core/temp/vsh.txt"
        print(logFile)
        mycsv = getFromvSanHealthLogFile(logFile)
        mycsv=myrestartInstance+"|vsan-health green (vmon)\n"+mycsv
        
        BDT.markProcessed(myPID,ServiceBootDataJSON,serviceName)
        
        
        
        return mycsv

    

def getTomcatTimeOf_content_library():
    global serviceName
    global myPID
    global ServiceBootDataJSON
    mycsv = None
    mybootInfo,myrestartInstance = BDT.getLastBootInstance(serviceName)
    if mybootInfo is None:
        print("Could not find info about lookupsvc")
        return None
    else:
        print(mybootInfo)
        myPID = mybootInfo['PID']
        
        if(BDT.processed(myPID,ServiceBootDataJSON,serviceName)):
            print("Already processed latest instance: "+myrestartInstance)
            return None
        
        #errFile = getLatestFile("/var/log/vmware/lookupsvc/","stderr")
        logFile = "/var/log/vmware/content-library/cls.log"
        print(logFile)
        mycsv = getFromCLSLogFile(logFile)
        mycsv=myrestartInstance+"|content-library green (vmon)\n"+mycsv
        
        BDT.markProcessed(myPID,ServiceBootDataJSON,serviceName)
        
        
        
def getTomcatTimeOf_vpxd_svcs():
    global serviceName
    global myPID
    global ServiceBootDataJSON
    mycsv = None
    mybootInfo,myrestartInstance = BDT.getLastBootInstance(serviceName)
    if mybootInfo is None:
        print("Could not find info about lookupsvc")
        return None
    else:
        print(mybootInfo)
        myPID = mybootInfo['PID']
        
        if(BDT.processed(myPID,ServiceBootDataJSON,serviceName)):
            print("Already processed latest instance: "+myrestartInstance)
            return None
        
        #errFile = getLatestFile("/var/log/vmware/lookupsvc/","stderr")
        
        logFile = "/var/log/vmware/vpxd-svcs/vpxd-svcs.log"
        #logFile = "/var/core/temp/mysvcs.log"
        
        print(logFile)
        mycsv = getFromSVCSLogFile(logFile)
        mycsv=myrestartInstance+"|vpxd-svcs green (vmon)\n"+mycsv
        
        BDT.markProcessed(myPID,ServiceBootDataJSON,serviceName)
        
        
        return mycsv



def getTomcatTimeOf_sts():
    global serviceName
    global myPID
    mycsv = None
    mybootInfo,myrestartInstance = BDT.getLastBootInstance(serviceName)
    if mybootInfo is None:
        print("Could not find info about lookupsvc")
        return None
    else:
        print(mybootInfo)
        myPID = mybootInfo['PID']
        if(BDT.processed(myPID,ServiceBootDataJSON,serviceName)):
            print("Already processed latest instance: "+myrestartInstance)
            return None
        catalinaFile = getLatestFile("/var/log/vmware/sso/tomcat","catalina")
        catalinaFile = "/var/log/vmware/sso/tomcat/"+ catalinaFile
        print(catalinaFile)
        mycsv = getFromCatalinaFile(catalinaFile)
        mycsv=myrestartInstance+"|sts green (vmon)\n"+mycsv
        
        BDT.markProcessed(myPID,ServiceBootDataJSON,serviceName)
        
        
        
        return mycsv




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
    parser.add_argument("-s","--serviceName", type=str,help="Specify the name of service")
    parser.add_argument("-f","--folder", type=str,help="Specify output folder. Default: /var/log/vmware")
    parser.add_argument("-d","--deltafolder", type=str,help="Specify path for delta folder. File name would be <serviceName>_delta.txt")
    
    
    args = parser.parse_args()
        
    if args.serviceName:
        serviceName = args.serviceName
    else:
        print("No service name specified, exiting. Try --help for more info.")
        exit()
    
    ServiceBootDataJSON = '/var/log/vmware/'+serviceName+'BootData.json'
    
    
    if args.folder:
        outputFolder = args.folder
        if(outputFolder[-1]!='/'):
            outputFolder=outputFolder+'/'
        mytextoutputfile = outputFolder+serviceName+'BootData.txt'
        
        
    if args.deltafolder:
        deltafolder=args.deltafolder
        if(deltafolder[-1]!='/'):
            deltafolder=deltafolder+'/'
        
        mydeltaoutputfile = deltafolder+ serviceName + '_delta.txt'
    
            
    if args.vcName:
        vcName = args.vcName
    else:
        try:
            vcName = socket.gethostname()
        except Exception as e0:
            vcName = 'localhost'
            print(str(e0))
    
    
    try:
        #pushHeaderAndCreateFile()
        mycsvdata = getServiceComponentTimes(serviceName)
        
        
        #myheader = 'date|vcName|component|pid|boot_time_in_sec|last_started_at|last_triggered_at\n'
        myheader = 'date|vcName|component|pid|boot_time_in_sec|last_started_at|last_triggered_at|status\n'
        RDF.pushToFullFile(mytextoutputfile,myheader,mycsvdata)
        RDF.pushToDeltaFile(mydeltaoutputfile,myheader,mycsvdata)
        print(mycsvdata)
        
        
        
    
    except Exception as e:
        print("Component data collection failed: "+str(e))
        
    
    

