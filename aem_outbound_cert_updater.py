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
            
def get_certtypes(config_file="",cert_variation=""):
    try:
        cert_types=""
        with open(config_file, 'r') as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            cert_types=data[0]['certtypes'][cert_variation]    
        return cert_types
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
        
        # Epsilon-PROD-SAML.epsilon.com.crt
# print(get_public_key_from_file("cert-uploads/outbound/try.cer"))
# print(get_private_key_from_file("cert-uploads/outbound/Epsilon-prod-saml.pem"))
print(get_private_key_from_file("cert-uploads/outbound/try.pem"))