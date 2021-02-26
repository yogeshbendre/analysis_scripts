# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 11:58:23 2019

@author: ybendre
"""

import os
import string
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

mytextoutputfile = '/var/log/vmware/serviceHealthState.txt'
vcName = None



def getFromVmonFile(vmonFile,mintimestamp):
    global vcName
    hostname = vcName
    mycsvdata = None
    try:
            
        mylines = BDT.runCommand('tail -n 1000 '+vmonFile).split('\n')[:-1]
        
        for l in reversed(mylines):
            print(l)
            try:
                
                mytime = dt.strptime(l.split(',')[0],'%Y-%m-%d %H:%M:%S')
                mytimestamp = mytime.timestamp()
                if(mytimestamp<mintimestamp):
                    continue
                
                
                l1 = l.translate(str.maketrans('', '', string.punctuation))
                myservicedata = l.split('[query_service_health_vmon.py:81]')[1].strip().split(" ")
                myservice = myservicedata[0]
                myhealth = myservicedata[2].replace("[","").replace("'","").replace(",","")
                mymsg = "NA"
                mydict = {"HEALTHY":1,"HEALTHY_WITH_WARNINGS":0,"DEGRADED":-1,"UNKNOWN":-2}
                myhealthcode = -3
                if myhealth.upper() in mydict.keys():
                    myhealthcode = mydict[myhealth.upper()]
                try:
                    mymsg = l1.split("defaultmessage")[1].strip()
                    if len(mymsg)<2:
                        mymsg = 'NA'
                except Exception as e5:
                    print(str(e5))
                    
                d1 = str(round(mytimestamp))+"|"+str(hostname)+"|"+str(myservice)+"|"+str(myhealth)+"|"+str(mymsg)+"|"+str(myhealthcode)+"\n"
                print("New Entry: "+d1)
                
                if mycsvdata is None:
                    mycsvdata = ''
                mycsvdata = mycsvdata+d1
            except Exception as e4:
                print('getFromCatalinaFile failed: '+str(e4))
            
            
    except Exception as e3:
        print('getFromCatalinaFile failed: '+str(e3))
    
    
    
    return mycsvdata
    

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
    parser.add_argument("-d","--deltafolder", type=str,help="Specify path for delta folder. File name would be <serviceName>_delta.txt")
    
    
    
    args = parser.parse_args()
        
    
    if args.folder:
        outputFolder = args.folder
        if(outputFolder[-1]!='/'):
            outputFolder=outputFolder+'/'
        mytextoutputfile = outputFolder+'/serviceHealthStatus.txt'
        
        
    if args.deltafolder:
        deltafolder=args.deltafolder
        if(deltafolder[-1]!='/'):
            deltafolder=deltafolder+'/'
        
        mydeltaoutputfile = deltafolder+ 'serviceHealthStatus_delta.txt'
    
            
    if args.vcName:
        vcName = args.vcName
    else:
        try:
            vcName = socket.gethostname()
        except Exception as e0:
            vcName = 'localhost'
            print(str(e0))
    
    vmonFile = "/var/log/vmware/vmon/service_health_status.log" 
    
    try:
        #pushHeaderAndCreateFile()
        currtime = dt.now()
        backtimestamp = currtime - td(minutes=10)
        backtimestamp = backtimestamp.timestamp()
        mintimestamp = None
        try:
            with open('mylastchecktime.txt','r') as fp:
                mylastchecktime = fp.read().split('\n')[0]
                mintimestamp = int(mylastchecktime)
                print('Found last check till: '+mintimestamp)
        except Exception as e10:
            print("Appearantly first run: "+str(e10))
            mintimestamp = backtimestamp
            
                
        
        mycsvdata = getFromVmonFile(vmonFile,mintimestamp)
        with open('mylastchecktime.txt','w') as fp:
            fp.write(str(round(currtime.timestamp())))
        
        #myheader = 'date|vcName|component|pid|boot_time_in_sec|last_started_at|last_triggered_at\n'
        myheader = 'date|vcName|service|status|message|statusCode\n'
        RDF.pushToFullFile(mytextoutputfile,myheader,mycsvdata)
        RDF.pushToDeltaFile(mydeltaoutputfile,myheader,mycsvdata)
        print(mycsvdata)
        
        
        
    
    except Exception as e:
        print("Component data collection failed: "+str(e))
        
    
    

