#!/usr/bin/env python3
import requests
import time
import os
import sys
import yaml
from yaml.loader import SafeLoader


config_file="certs-script-config.yaml"


def get_certs_folder(config_file=""):
    try:
        folder=""
        with open(config_file, 'r') as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            folder=data[0]['outboundcertsfolder']
            if not folder.endswith("/"):
                folder+="/"    
        return folder
    except Exception as e:
        print("Error in reading config file: "+str(e))

def get_environment(config_file="",env=""):
    try:
        environment=""
        with open(config_file, 'r') as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            environment=data[0]['environments'][env]    
        return environment
    except Exception as e:
        print("Error in reading config file: "+str(e))
        
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

def get_filenames(folder=None):
    return os.listdir(folder)

def get_private_key_from_file(filepath=""):
    try:
        key=""
        with open(filepath) as file:
            copy=False
            content=file.readlines()
            if len(content) <2 or "-----END PRIVATE KEY-----" in content[0]:
                content[0]=content[0].replace("\n","")
                return content[0]
            file.seek(0)
            for line in file:
                if line.strip()=="-----BEGIN PRIVATE KEY-----":
                    key+="-----BEGIN PRIVATE KEY-----"
                    copy=True
                    continue
                elif line.strip()=="-----END PRIVATE KEY-----":
                    key+="-----END PRIVATE KEY-----"
                    copy=False
                    continue
                elif copy:
                    key+=line

        key=key.replace("\n","")
        if key=="":
            raise Exception("private Key Not Found")
        return key
    except Exception as e:
        print("Exception Error Occured In Fetching Private key! error: "+str(e))

def get_public_key_from_file(filepath=""):
    try:
        key=""
        with open(filepath) as file:
            copy=False
            content=file.readlines()
            if len(content) <2 or "-----END CERTIFICATE-----" in content[0]:
                content[0]=content[0].replace("\n","")
                return content[0]
            file.seek(0)
            for line in file:
                if line.strip()=="-----BEGIN CERTIFICATE-----":
                    key+="-----BEGIN CERTIFICATE-----"
                    copy=True
                    continue
                elif line.strip()=="-----END CERTIFICATE-----":
                    key+="-----END CERTIFICATE-----"
                    copy=False
                    continue
                elif copy:
                    key+=line

        key=key.replace("\n","")
        if key=="":
            raise Exception("Public Key Not Found")
        return key
    except Exception as e:
        print("Exception Error Occured In Fetching Public key! error: "+str(e))

def create_update(osgipath="",key="",value=""):
    return "^"+osgipath+"/"+key+" : "+"\""+value+"\""

def update_certs_crx_de_values(host="",port="",auth=(),updates=[]):
    try:
        endpoint="http://"+host+":"+port+"/crx/server/crx.default/jcr:root"
        payload=""
        for update in updates:
            payload+=update+"\n"
        files={
            ":diff": (None,payload)
        }        
        response = requests.post(endpoint,auth=auth,files=files)
        print("Updated Following Values: ")
        for update in updates:
            print(update)
        print("Response Status Code: "+str(response.status_code))
    except Exception as e:
        print("Update Values Failed!")
        print("Exception Error Occured In update crx de values! error: "+str(e))

def get_outbound_cert_values(host="",port="",auth=(),osgipath="",key=""):
    try:
        endpoint="http://"+host+":"+port+"/crx/server/crx.default/jcr:root"+osgipath+".json"
        response = requests.get(endpoint,auth=auth)
        return response.json()[key]
    except Exception as e:
        print("Exception Error Occured In Fetching cert value! error: "+str(e))
        

def upload_cert(host="",port="",auth=(),instance={},key="",value=""):
    try:
        updates=[]
        updates.append(create_update(osgipath=instance["outboundosgipath"],key=key,value=value))
        update_certs_crx_de_values(host=host,port=port,auth=auth,updates=updates)                
    except Exception as e:
        print("Error In Uploading Cert Value "+instance["host"]+":"+instance["port"]+"! error: "+str(e))

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

def get_cert_types(config_file=""):
    try:
        cert_types=""
        with open(config_file, 'r') as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            cert_types=data[0]['certtypes']['outbound']    
        return cert_types
    except Exception as e:
        print("Error in reading config file: "+str(e))    

def get_cert_variations(config_file="",cert_type=""):
    try:
        cert_variations=""
        with open(config_file, 'r') as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            cert_variations=data[0]['certtypes']['outbound'][cert_type]    
        return cert_variations
    except Exception as e:
        print("Error in reading config file: "+str(e))    

def choose_cert_type(config_file=""):
    while True:
        try:
            cert_types=get_cert_types(config_file=config_file)
            i=0
            print("Available Outbound Cert Types: ")
            for cert_type in cert_types:
                i=i+1
                print(str(i)+" - "+cert_type)
            cert_type_option=int(input("Choose Outbound Cert Type: "))
            if type(cert_type_option)!=int or cert_type_option > len(cert_types) or cert_type_option<1:
                raise Exception("Invalid Option!")
            return list(cert_types.keys())[cert_type_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue
        
def choose_cert_variation(config_file="",cert_type=""):
    while True:
        try:
            cert_variations=get_cert_variations(config_file=config_file,cert_type=cert_type)
            i=0
            print("Available "+cert_type+" Cert Types: ")
            for cert_variation in cert_variations:
                i=i+1
                print(str(i)+" - "+cert_variation)
            cert_variation_option=int(input("Choose "+cert_type+" Cert Type: "))
            if type(cert_variation_option)!=int or cert_variation_option > len(cert_variations) or cert_variation_option<1:
                raise Exception("Invalid Option!")
            return cert_variations[cert_variation_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue
        
        
def choose_cert_file(config_file=""):
    while True:
        try:
            cert_files=get_filenames(folder=get_certs_folder(config_file=config_file))
            i=0
            print("Available Outbound Cert files: ")
            for cert_file in cert_files:
                i=i+1
                print(str(i)+" - "+cert_file)
            cert_file_option=int(input("Choose Outbound Cert file: "))
            if type(cert_file_option)!=int or cert_file_option > len(cert_files) or cert_file_option<1:
                raise Exception("Invalid Option!")
            return cert_files[cert_file_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue


def upload_certs_to_environment(config_file="",environment=[],name="",filepath="",key=""):
    try:
        
        print("Starting Upload Process to all instances in "+name+"....")
        for instance in environment:
            print("Uploading In Instance: "+instance['host']+":"+instance['port']+".....")
            if "private" in key.lower():
                value=get_private_key_from_file(filepath)                
                upload_cert(host=instance['host'],port=instance['port'],auth=(instance['username'],instance['password']),instance=instance,key=key,value=value)
            else:
                value=get_public_key_from_file(filepath)                
                upload_cert(host=instance['host'],port=instance['port'],auth=(instance['username'],instance['password']),instance=instance,key=key,value=value)
            print("Uploaded to Instance: "+instance['host']+":"+instance['port']+" Successfully!")
            print("Upload Process to all instances in "+name+" Completed Successfully!")
    except Exception as e:
        print("Error In Uploading Cert to environment: "+name+"! error: "+str(e))

def main(config_file=""):
    env=choose_environment(config_file=config_file)
    certs_folder=get_certs_folder(config_file=config_file)
    print("Selected Environment: "+env)
    environment=get_environment(config_file=config_file,env=env)
    cert_type=choose_cert_type(config_file=config_file)
    print("Selected Outbound Cert Type: "+cert_type)
    cert_variation=choose_cert_variation(config_file=config_file,cert_type=cert_type)
    print("Selected "+cert_type+" Cert Type: "+cert_variation)
    cert_file=choose_cert_file(config_file=config_file)
    print("Selected Cert File: "+cert_file)
    upload_certs_to_environment(config_file=config_file,environment=environment,name=env,filepath=certs_folder+cert_file,key=cert_variation)
    print("End of Script!")       

main(config_file=config_file)
