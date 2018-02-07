#!/usr/bin/env python

"""
 
 Script to monitor Ambari to ensure that host services are running.
 The server and services are listed in the CLUSTER dictionary. 
 The 'desired state' for all listed services should be 'STARTED' and
 the current 'state' should be the same. If the REST state is something
 else ( for instance 'installed' ) then the test will fail.
 This script relys on the python requests library

"""
import requests
import json
import collections
import sys

USER,PASSWORD = 'admin','admin'

# Add hosts and components as needed. Not all components need to be monitored.
CLUSTER = {'01':['METRICS_MONITOR','ZOOKEEPER_SERVER','ZKFC'],
            '02':['METRICS_MONITOR','NIMBUS','JOURNALNODE','ZKFC'],
            '03':['ZOOKEEPER_SERVER'],
            '07':['SUPERVISOR'],
            '08':['SUPERVISOR'],
            '09':['SUPERVISOR'],
            '10':['METRICS_MONITOR']}


AMBURL = "http://pilot-01.corp.local:8080/api/v1/clusters/pilot/hosts/pilot-%s.corp.local/host_components/%s"

def test_component_service(host_name, service_name):
    test_url = AMBURL%(host_name,service_name)
    ssr = requests.get(test_url, auth= (USER, PASSWORD))
    dstate =  ssr.json()['HostRoles']['desired_state'] 
    cstate =  ssr.json()['HostRoles']['state']  
    if dstate == cstate:
        print(host_name+" : "+ service_name + " Is running fine")
    else:
        print(host_name +" : "+service_name+" : **** Service is in installed state. Something is wrong ****")
        sys.exit(1)
    
    

def main():
    # Sort the Dict to make sure we start with sspilot-01
    d = collections.OrderedDict(sorted(CLUSTER.items()))
    for server, components in d.iteritems():
        for test_status in components:
            test_component_service(server,test_status)


if __name__ == "__main__":
    main()


