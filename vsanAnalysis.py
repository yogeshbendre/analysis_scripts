# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 11:54:26 2019

@author: ybendre
"""
import subprocess as sp
import os

outputdir = '/etc/vmware-vpx/docRoot/vsan/'


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

def getObjectNameListFromRVCList(objlist,objtype):
    
    mylist = []
    for o in objlist:
            print(o)
            try:
                
                if '('+objtype+')' in o:
                    objname = getObjectNameFromRVCList(o,objtype)
                    mylist.append(objname)
            except Exception as e:
                print("getObjetNameListFromRVCList failed: "+str(e))
        
    return(mylist)
        

def getObjectNameFromRVCList(objentry,objtype):
    
    objname = ' '.join(objentry.split(' ')[1:])
    objname = objname.split('('+objtype+')')[0]
    objname = objname.replace(' ','').replace('\\n','').replace('\\x1b[0m','').replace('\\x1b[31m','')
    return objname
    

def getDCToClusterMap():

    try:
        
        d = runCommand('echo exit | rvc administrator@vsphere.local:Admin\!23@localhost --cmd="ls localhost/" 2> bla.txt')
        print(d)
        out = d.split("\\n")
        mydclist = getObjectNameListFromRVCList(out,'datacenter')
            
            
        print(mydclist)
        mymap = {}
        for dc in mydclist:
            
            myclusterlist = []
            try:
                d = runCommand('echo exit | rvc administrator@vsphere.local:Admin\!23@localhost --cmd="ls localhost/'+dc+'/computers" 2> bla.txt')
                out = d.split('\\n')
                myclusterlist = getObjectNameListFromRVCList(out,'cluster')
            except Exception as e2:
                print("getDCToClusterMap failed : "+dc+" -> "+str(e2))
            mymap[dc] = myclusterlist
        
        return mymap
            
        
    except Exception as e:
        print(str(e))
        

def getRedVsanClusters():
    myredclusterlist = ['UWSIM-9','VsanTest']
    
    
    return myredclusterlist


def getMyDC(clusterName,dctoclustermap):
    
    mydc = None
    
    for dc in dctoclustermap.keys():
        if clusterName in dctoclustermap[dc]:
            mydc = dc
            break
    
    return mydc
    

def analyzeRedVsanClusters():
    
    myredclusters = getRedVsanClusters()
    mymap = getDCToClusterMap()
    print(mymap)
    print(myredclusters)
    
    try:
        os.mkdir(outputdir)
    except Exception as e:
        print("Failed to create output dir: "+str(e))
    
    # <button class="tablinks" onclick="openTab(event, 'register')" id="defaultOpen">rest/register</button>
    #<div id="register" class="tabcontent">
   #<h3>rest/register</h3>
   #</div>
    myclusterReports = {}

    for rc in myredclusters:
        try:
            print("Check: "+rc)
            mydc = getMyDC(rc,mymap)
            print("Datacenter: "+mydc)
            with open('vsananalysis.sh','r') as fp:
                myscript = fp.read()
                myscript = myscript.replace('$$MYDATACENTERNAME$$',mydc).replace('$$MYCLUSTERNAME$$',rc)
                with open(rc+'.sh','w') as fp2:
                    fp2.write(myscript)
            
            
            myout = runCommand("chmod 777 "+rc+".sh")
            myout = runCommand("./"+rc+".sh > "+rc+"_report.txt")
            with open(rc+"_report.txt","r") as fp:
                myclusterReports[rc] = str(fp.read())
        
                    
                    
        except Exception as e2:
            print("Failed to process "+rc+" : "+str(e2))
        
    
    
    buttonString = ""
    divString = ""
    buttonTemp = '<button class="tablinks" onclick="openTab(event, \'CLUSTERNAME\')" id="defaultOpen">CLUSTERNAME</button>'
    divTemp = '<div id="CLUSTERNAME" class="tabcontent">\nCLUSTERDATA\n</div>'
    
    try:
        for cluster in myclusterReports.keys():
            mybutton = buttonTemp.replace('CLUSTERNAME',cluster)
            mydiv = "<p><pre>"+divTemp.replace('CLUSTERNAME',cluster).replace('CLUSTERDATA',myclusterReports[cluster])+"</pre></p>"
            buttonString = buttonString + "\n" + mybutton
            divString = divString + "\n" + mydiv
            buttonTemp = '<button class="tablinks" onclick="openTab(event, \'CLUSTERNAME\')">CLUSTERNAME</button>'
        
        with open("vsanreporttemp.html","r") as fp:
            myhtml = fp.read()
            myhtml = myhtml.replace("MYBUTTONS",buttonString).replace("MYDIVS",divString)
            with open(outputdir+"index.html","w") as fp2:
                fp2.write(myhtml)
            
            
    except Exception as e3:
        print(str(e3))


if __name__ == "__main__":
   
    analyzeRedVsanClusters()
