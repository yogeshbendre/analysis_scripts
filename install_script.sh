
rm -rf master.zip
rm -rf analysis_scripts-master/*.*
wget http://github.com/yogeshbendre/analysis_scripts/archive/master.zip
unzip master.zip
rm -rf master.zip
cd analysis_scripts-master/
chmod 777 base_script.sh
./base_script.sh