python3 uiBootMonitor.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../delta1.txt -e ../delta2.txt > /var/log/vmware/uiout_analysis.txt 2> /var/log/vmware/uiout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s lookupsvc -n lookupsvc > /var/log/vmware/lookupsvcout_analysis.txt 2> /var/log/vmware/lookupsvcout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s sts -n vmware-stsd.launcher > /var/log/vmware/stsout_analysis.txt 2> /var/log/vmware/stsout_analysis.txt
#python3 vsanAnalysis.py > /var/log/vmware/vsanout_analysis.txt 2> /var/log/vmware/vsanout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s sps -n vmware-sps.launcher > /var/log/vmware/spsout_analysis.txt 2> /var/log/vmware/spsout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s content-library -n vmware-content-library.launcher > /var/log/vmware/clsout_analysis.txt 2> /var/log/vmware/clsout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s vpxd-svcs -n vmware-vpxd-svcs.launcher > /var/log/vmware/svcsout_analysis.txt 2> /var/log/vmware/svcsout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s vsan-health -n vmware-vsan-health > /var/log/vmware/vsanhealthout_analysis.txt 2> /var/log/vmware/vsanhealthout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s eam -n vmware-eam.launcher > /var/log/vmware/eamout_analysis.txt 2> /var/log/vmware/eamout_analysis.txt
python3 vmon_health_report.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ > /var/log/vmware/servicehealthout_analysis.txt 2> /var/log/vmware/servicehealthout_analysis.txt
cp /var/log/vmware/BootData.json /var/log/BootData.json
