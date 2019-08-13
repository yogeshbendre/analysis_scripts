python uiBootMonitor.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../delta1.txt -e ../delta2.txt
python service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s lookupsvc
python service_tomcat_component_times.py -f /var/log/vmware/vapi/monitoring/SYSTEM-LEVEL-UTILIZATION/ -d ../ -s sts