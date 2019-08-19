#write out current crontab
crontab -l > testmycron
#echo new cron into cron file
echo "*/5 * * * * /root/analysis_scripts/install_scripts.sh" >> testmycron
#install new cron file
crontab testmycron
#rm mycron
crontab -l
