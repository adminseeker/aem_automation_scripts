#!/usr/bin/env python3
import requests

host="localhost"
port="4502"
user="admin"
password="admin"

auth=(user,password)

def get_filters_from_file(file=None):
    f = open(file,"r")
    filters=[]
    for i in f.readlines():
        if i.strip() == "":
            continue
        filter=i.strip()
        filters.append(filter)
    return filters

def filter_validator(filter_path=""):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/de/tree.jsp?path="+filter_path
    response = requests.get(url,auth=auth,headers=headers)
    if response.status_code==200:
        print(filter_path+" : valid")
        return True
    print(filter_path+" : invalid")
    return False

def main():
    invalid_filters=[]
    try:
        f=open("filters.txt","r")
        if len(f.readlines())==0:
            raise Exception("No Filters Present in filters.txt!")
    except Exception as e:
        print(e)
        return
    filters=get_filters_from_file("filters.txt")
    if len(filters)==0:
        print("No Filters Present in filters.txt!")
        return
    for filter in filters:
        if not filter_validator(filter):
            invalid_filters.append(filter)

    print("Invalid Filters Count: "+str(len(invalid_filters)))
    if len(invalid_filters)!=0:
        print("Invalid Filter Paths: ")
        for filter in invalid_filters:
            print(filter)



main()