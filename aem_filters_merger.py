#!/usr/bin/env python3
import requests
import yaml
from yaml.loader import SafeLoader


host="localhost"
port="4502"
user="admin"
password="admin"

auth=(user,password)

packages=[]

with open('packages.yaml', 'r') as f:
    data = list(yaml.load_all(f, Loader=SafeLoader))
    packages=data[0]['packages']

def get_filters(auth=(),host="",port="",packageName="",packageVersion="",groupName=""):
    filters=[]
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/packmgr/"
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    path='list.jsp?includeVersions=false&q='+fullPackageName+".zip"
    endpoint=url+path
    response = requests.get(endpoint,auth=auth,headers=headers)
    # results=response.json()['results'][0]['filter']
    results=[]
    for result in response.json()['results']:
        if result['version']==packageVersion and result['group']==groupName:
            results=result['filter']
    for i in results:
        filters.append(i['root'])
    return filters


def merge_filters(auth=(),host="",port="",packages=[]):
    merged_filter_list=[]
    for package in packages:
        filters=get_filters(auth=auth,host=host,port=port,packageName=package['name'],packageVersion=package['version'],groupName=package['groupName'])
        print("filters count for package: "+"Name:"+package['name']+","+"Version:"+package['version']+","+"Group:"+package['groupName'] + " is: "+str(len(filters)))
        merged_filter_list+=filters
    
    print("filters count before removing duplicates: "+str(len(merged_filter_list)))
    return list(set(merged_filter_list))

def main():
    final_filters_list=merge_filters(auth,host,port,packages)
    print("Final Filters Count: "+str(len(final_filters_list)))
    if len(final_filters_list)==0:
        return
    f=open("merged_filters.txt","wb")
    for filter in final_filters_list:
        i=bytes(filter+"\n","ascii")
        f.write(i)
    f.close()
    print("Written filters to merged_filters.txt")

main()