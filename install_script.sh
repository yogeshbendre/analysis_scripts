#!/bin/bash

ls > /root/mylog2.txt
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo ${DIR} > /root/mylog3.txt
cd ${DIR}
pwd > mylog.txt
rm -rf master.zip
rm -rf analysis_scripts-master/*.*
wget http://github.com/yogeshbendre/analysis_scripts/archive/master.zip
unzip master.zip
rm -rf master.zip
cd analysis_scripts-master/
chmod 777 base_script.sh
./base_script.sh > myout.txt 2> myerr.txt
