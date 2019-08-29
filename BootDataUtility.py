# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:00:00 2019

@author: ybendre
"""
import os
import subprocess as sp
from datetime import datetime as dt, timedelta as td
import json
import socket
import argparse
import sys


bootDataJSON = '/var/log/vmware/BootData.json'




def runCommand(mycmd):
    print("Run Command: "+mycmd)
    try:
        d = sp.check_output(mycmd,shell=True)
        #d = d.replace("b'","")
        d = d.decode("utf-8")
        d=d[:-1]
        print(d)    
        return d
    
    except Exception as e:
        print("runCommand failed: "+str(e))
        return None


def processed(PID,myfile,service):
    
    try:
        print("Check PID: "+PID)
        BootData = json.load(open(myfile,"r"))
        print(BootData)
        if service+"_"+str(PID) in BootData.keys():
            return(True)
        else:
            return(False)
    except Exception as e:
        print("processed failed: "+str(e)+". But it's ok, may be first run.")
        return(False)


def markProcessed(PID,myfile,service):
    BootData = {}
    try:
        BootData = json.load(open(myfile,"r"))
        
    except Exception as e:
        print("Mark Processed failed: "+str(e)+". But it's ok, may be first run.")
        BootData = {}
    
    try:
        BootData[service+"_"+str(PID)]="Done"
        json.dump(BootData,open(myfile,"w"))
    except Exception as e2:
        print("Mark Processed failed: "+str(e2))


def getLastBootInstance(service_name):
    
    try:
        myData = json.load(open(bootDataJSON,"r"))
        mysTimes = []
        mysData ={}
        for p in myData.keys():
            try:
                parts = p.split("_")
                if parts[0]==service_name:
                    print("Instance")
                    print(p)
                    d1 = myData[p]
                    print(d1)
                    mytimestamp = d1.split("|")[0].replace('\n','')
                    print(mytimestamp)
                    mysTimes.append(int(mytimestamp))
                    mysData[mytimestamp]=d1
            except Exception as e3:
                print("getLastBootInstance failed: "+str(e3))
        
        mysTimes.sort()
        print("Finished getLastBootInstance")
        t = mysTimes[-1]
        myRestartInstance = mysData[str(t)]
        mytimedata = myRestartInstance.split('|')
        myInfo = {}
        
        StartTime = mytimedata[-2].replace("\n","")
        PIDTime = mytimedata[-1].replace("\n","")
        PID = mytimedata[3].replace("\n","")
        mytook = mytimedata[4].replace("\n","")
        
        myInfo["StartTime"] = StartTime
        myInfo["PIDTime"] = PIDTime
        myInfo["PID"] = PID
        try:
            myRestartInstance = myRestartInstance.replace(mytook,str(round(float(mytook)))).replace("\n","")
        
        except Exception as e8:
            print(str(e8))
        
        return(myInfo,myRestartInstance)
    
    except Exception as e2:
        print("getLastBootInstance failed: "+str(e2))
        return None
    
