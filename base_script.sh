python3 uiBootMonitor.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../delta1.txt -e ../delta2.txt > /var/log/vmware/uiout_analysis.txt 2> /var/log/vmware/uiout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s lookupsvc > /var/log/vmware/lookupsvcout_analysis.txt 2> /var/log/vmware/lookupsvcout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s sts > /var/log/vmware/stsout_analysis.txt 2> /var/log/vmware/stsout_analysis.txt
python3 vsanAnalysis.py > /var/log/vmware/vsanout_analysis.txt 2> /var/log/vmware/vsanout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s sps > /var/log/vmware/spsout_analysis.txt 2> /var/log/vmware/spsout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s content-library > /var/log/vmware/clsout_analysis.txt 2> /var/log/vmware/clsout_analysis.txt
python3 service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s vpxd-svcs > /var/log/vmware/svcsout_analysis.txt 2> /var/log/vmware/svcsout_analysis.txt
