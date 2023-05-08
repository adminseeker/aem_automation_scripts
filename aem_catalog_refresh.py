#!/usr/bin/python

import requests
import concurrent.futures
import yaml
from yaml.loader import SafeLoader

config_file="content-deploy-config.yaml"

def get_environment_names(config_file=""):
    try:
        names=[]
        with open(config_file, 'r') as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            environments=data[0]['environments']
            names=list(environments.keys())
        return names
    except Exception as e:
        print("Error in reading config file: "+str(e)) 
        
def choose_environment(config_file=""):
    while True:
        try:
            env_names=get_environment_names(config_file=config_file)
            i=0
            print("Available Environments: ")
            for name in env_names:
                i=i+1
                print(str(i)+" - "+name)
            env_option=int(input("Choose Environment: "))
            if type(env_option)!=int or env_option > len(env_names) or env_option<1:
                raise Exception("Invalid Option!")
            return env_names[env_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue
        
def get_environment(config_file="",env=""):
    try:
        environment=""
        with open(config_file, 'r') as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            environment=data[0]['environments'][env]    
        return environment
    except Exception as e:
        print("Error in reading config file: "+str(e)) 

def get_catalog_refresh_urls(config_file=""):
    try:
        urls=[]
        with open(config_file, 'r') as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            urls=data[0]['catalogrefresh'] 
        return urls
    except Exception as e:
        print("Error in reading config file: "+str(e)) 

def get_result(url):
    try:
        resp = requests.get(url=url,verify=False)
        return url+" : "+resp.text
    except Exception as e:
        print("Error in Get request: "+str(e)) 

def exceute_concurrently(urls=[]):
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for url in urls:
                futures.append(executor.submit(get_result, url=url))
            for future in concurrent.futures.as_completed(futures):
                print(future.result())
    except Exception as e:
        print("Error in executing concurrent process: "+str(e)) 
        
def exceute_synchronously(urls=[]):
    try:
        for url in urls:
            res=get_result(url)
            print(res)
    except Exception as e:
        print("Error in executing concurrent process: "+str(e))   

def create_urls_sync(environment=None,config_file=config_file):
    try:
        urls={}
        catalogpaths=get_catalog_refresh_urls(config_file=config_file)
        for instance in environment:
            if instance['type']=="publish":
                paths=[]
                for path in catalogpaths:
                    url="http://"+instance["host"]+":"+instance["port"]+path
                    paths.append(url)
                urls[instance['name']]=paths
        return urls
    except Exception as e:
        print("Error in creating urls async: "+str(e))
        
def create_urls_async(environment=None,config_file=config_file):
    try:
        urls={}
        catalogpaths=get_catalog_refresh_urls(config_file=config_file)
        for path in catalogpaths:
            paths=[]
            for instance in environment:
                if instance['type']=="publish":
                    url="http://"+instance["host"]+":"+instance["port"]+path
                    paths.append(url)
            urls[path.split("/").pop()]=paths
        return urls
    except Exception as e:
        print("Error in creating urls async: "+str(e))
        
def choose_refresh_method():
    while True:
        try:
            modes=["Auto","Manual"]
            i=0
            print("Available Refresh Modes: ")
            for name in modes:
                i=i+1
                print(str(i)+" - "+name)
            install_option=int(input("Choose Refresh Method: "))
            if type(install_option)!=int or install_option > len(modes) or install_option<1:
                raise Exception("Invalid Option!")
            return modes[install_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue

def refresh(config_file="",environment={},mode=""):
    try:
        if mode=="Auto":
            urls=create_urls_async(environment=environment,config_file=config_file)
            for host in list(urls.keys()):
                print("Catalog Refresh of "+host+" in progress......")
                exceute_concurrently(urls=urls[host])
        elif mode=="Manual":
            urls=create_urls_sync(environment=environment,config_file=config_file)
            for host in list(urls.keys()):
                refresh="false"
                refresh_option=input("Do you want to refresh "+host+" (y/n): ")
                while(refresh_option.strip()!="y" and refresh_option.strip()!="Y" and refresh_option.strip()!="n" and refresh_option.strip()!="N"):
                    print("Invalid Option!")
                    refresh_option=input("Do you want to refresh "+host+" (y/n): ")
                if refresh_option=="y" or refresh_option=="Y":
                    refresh="true"
                elif refresh_option=="n" or refresh_option=="N":
                    refresh="false"
                    print("refresh Cancelled!")
                if refresh=="true":
                    print("Catalog Refresh of "+host+" in progress......")
                    exceute_synchronously(urls[host])
    except Exception as e:
        print("Error in refreshing: "+str(e))
        
def main(config_file=""):
    env=choose_environment(config_file=config_file)
    environment=get_environment(config_file=config_file,env=env)
    mode=choose_refresh_method()
    refresh(config_file=config_file,environment=environment,mode=mode)
    print("End Of Script!")
    
    
main(config_file=config_file)
