#write out current crontab
crontab -l > testmycron
#echo new cron into cron file
{
cat testmycron | grep "install_script.sh" &&
echo "Cron already exist"
} || {
echo "Setup cron" 
echo "*/5 * * * * /root/analysis_scripts/install_script.sh" >> testmycron
#install new cron file
crontab testmycron
}
#rm mycron
crontab -l
