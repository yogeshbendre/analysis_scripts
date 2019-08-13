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
    sname = sname.replace("vmware-","")
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
    d = BDT.runCommand("ls -lrt "+folder+" | grep "+fname_pattern).split("\\n")[-2].split(" ")[-1]
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
        
    
    

