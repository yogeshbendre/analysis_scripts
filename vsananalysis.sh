echo "Report As On"
date
echo
echo "Datastore Capacity"
echo
echo exit | rvc administrator@vsphere.local:Admin\!23@localhost -a --cmd="ls localhost/$$MYDATACENTERNAME$$/datastores/" | grep vsan
echo
echo "Disk Stats"
echo
echo exit | rvc administrator@vsphere.local:Admin\!23@localhost --cmd="vsan.disks_stats localhost/$$MYDATACENTERNAME$$/computers/$$MYCLUSTERNAME$$"
echo
echo "Resync Dashboard"
echo
echo exit | rvc administrator@vsphere.local:Admin\!23@localhost --cmd="vsan.resync_dashboard localhost/$$MYDATACENTERNAME$$/computers/$$MYCLUSTERNAME$$"
echo
echo "Cluster State"
echo
echo exit | rvc administrator@vsphere.local:Admin\!23@localhost --cmd="vsan.check_state localhost/$$MYDATACENTERNAME$$/computers/$$MYCLUSTERNAME$$"
echo
echo "Object Status Report"
echo
echo exit | rvc administrator@vsphere.local:Admin\!23@localhost --cmd="vsan.obj_status_report localhost/$$MYDATACENTERNAME$$/computers/$$MYCLUSTERNAME$$ -t"
echo
echo "Cluster Info"
echo
echo exit | rvc administrator@vsphere.local:Admin\!23@localhost --cmd="vsan.cluster_info localhost/$$MYDATACENTERNAME$$/computers/$$MYCLUSTERNAME$$"
