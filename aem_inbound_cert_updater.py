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
            folder=data[0]['inboundcertsfolder']
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

def upload_to_truststore(host="",port="",auth=(),cer_file_path=None):
    try:
        endpoint="http://"+host+":"+port+"/libs/granite/security/post/truststore"
        cerfp=open(cer_file_path,"rb")
        files={
            "certificate":cerfp
        }
        response = requests.post(endpoint,auth=auth,files=files)
        print("Uploaded Successfully To Truststore!")
        print("Response Status Code: "+str(response.status_code))
        cerfp.close()
    except Exception as e:
        print("Uploaded To Truststore Failed!")
        print("Exception Error Occured In Truststore Upload! error: "+str(e))

def upload_to_keystore(host="",port="",auth=(),alias="",cer_file_path=None,der_file_path=None):
    try:
        endpoint="http://"+host+":"+port+"/home/users/system/authentication-service.ks.html"
        cerfp=open(cer_file_path,"rb")
        derfp=open(der_file_path,"rb")
        files={
            "alias":alias,
            "pk":derfp,
            "cert-chain":cerfp
        }
        
        response = requests.post(endpoint,auth=auth,files=files)
        print("Uploaded Successfully To Keystore!")
        print("Response Status Code: "+str(response.status_code))
        cerfp.close()
        derfp.close()
    except Exception as e:
        print("Uploaded To Keystore Failed!")
        print("Exception Error Occured In Keystore Upload! error: "+str(e))

def get_private_key_from_pemfile(filepath=""):
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
        
def upload_pemfile(host="",port="",auth=(),filepath="",osgipath=""):
    try:
        privatekey=get_private_key_from_pemfile(filepath=filepath)
        updates=[]
        updates.append(create_update(osgipath=osgipath,key="getUSBankPrivateKey",value=privatekey))
        update_certs_crx_de_values(host=host,port=port,auth=auth,updates=updates)
        print("PEM File Uploaded Successfully: ")
        print(filepath)                
    except Exception as e:
        print("Uploading PEM File Failed!")
        print("Exception Error Occured In PEM file Upload! error: "+str(e))
        
def get_truststore_certs(host="",port="",auth=()):
    try:
        endpoint="http://"+host+":"+port+"/libs/granite/security/truststore.json"
        response = requests.get(endpoint,auth=auth)
        alias_list=response.json()['aliases']
        result=[]
        for alias in alias_list:
            to_Add={}
            to_Add["alias"]=alias['alias']
            to_Add["subject"]=alias['subject']
            to_Add["notBefore"]=alias['notBefore']
            to_Add["notAfter"]=alias['notAfter']
            result.append(to_Add)
        return result
    except Exception as e:
        print("Fetching Truststore Certs Failed!")
        print("Exception Error Occured In Fetching Truststore Certs! error: "+str(e))

def get_keystore_certs(host="",port="",auth=()):
    try:
        endpoint="http://"+host+":"+port+"/home/users/system/authentication-service.ks.json"
        response = requests.get(endpoint,auth=auth)
        alias_list=response.json()['aliases']
        result=[]
        for alias in alias_list:
            to_Add={}
            to_Add["alias"]=alias['alias']
            chain=alias['chain'][0]
            to_Add["subject"]=chain['subject']
            to_Add["notBefore"]=chain['notBefore']
            to_Add["notAfter"]=chain['notAfter']
            result.append(to_Add)
        return result
    except Exception as e:
        print("Fetching Keystore Certs Failed!")
        print("Exception Error Occured In Fetching Keystore Certs! error: "+str(e))

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

def upload_all_certs(host="",port="",auth=(),folder="",inbound_osgi_privatekey_path=""):
    try:
        if not folder.endswith("/"):
            folder=folder+"/"
        files=get_filenames(folder)
        success_uploads=[]
        for file in files:
            if file.endswith(".der"):
                filename=file.split(".der")[0]
                der_file=folder+file
                cer_file=""
                if os.path.isfile(folder+filename+".cer"):
                    cer_file=folder+filename+".cer"
                elif os.path.isfile(folder+filename+".crt"):
                    cer_file=folder+filename+".crt"
                else:
                    raise Exception(".cer/.crt file not found for file: "+file)
                
                alias=input("Enter Cert Alias for the der file "+"\""+file+"\""+": ")
                upload_to_keystore(host=host,port=port,auth=auth,alias=alias,cer_file_path=cer_file,der_file_path=der_file)
                success_uploads.append(der_file)
            if file.endswith(".crt") or file.endswith(".cer"):
                upload_to_truststore(host=host,port=port,auth=auth,cer_file_path=folder+file)
                success_uploads.append(folder+file)
            if file.endswith(".pem"):
                if inbound_osgi_privatekey_path=="":
                    raise Exception("osgipath for private key file not passed!")
                upload_pemfile(host=host,port=port,auth=auth,filepath=folder+file,osgipath=inbound_osgi_privatekey_path)
                
        if len(success_uploads)!=0:
            print("Certs Uploaded Successfully: ")
            for file in success_uploads:
                print(file)
        else:
            print("No Certs Were Uploaded!")
    except Exception as e:
        print("Error In Uploading Certs! error: "+str(e))

def get_certs_from_instance(environment=[],hostoption=0):
    try:
        instances=[]
        i=0
        for instance in environment:
            toadd={}
            toadd['host']=instance['host']
            toadd['port']=instance['port']
            toadd['auth']=(instance['username'],instance['password'])
            instances.append(toadd)
        if type(hostoption)!=int or hostoption > len(instances) or hostoption<1:
            raise Exception("Invalid Option!")
        instance=instances[hostoption-1]
        truststore_certs=get_truststore_certs(host=instance['host'],port=instance['port'],auth=instance['auth'])
        keystore_certs=get_keystore_certs(host=instance['host'],port=instance['port'],auth=instance['auth'])
        return (truststore_certs,keystore_certs)
    except Exception as e:
        print("Error In Listing Certs! error: "+str(e)) 

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

def choose_cert_type(config_file="",cert_variation="",environment=[]):
    while True:
        try:
            # cert_types=get_certtypes(config_file=config_file,cert_variation=cert_variation)
            available_certs=environment[0]['inboundosgipaths']
            i=0
            print("Available Inbound Cert Types: ")
            for cert_type in available_certs:
                i=i+1
                print(str(i)+" - "+cert_type)
            cert_type_option=int(input("Choose Inbound Cert Type: "))
            if type(cert_type_option)!=int or cert_type_option > len(available_certs) or cert_type_option<1:
                raise Exception("Invalid Option!")
            return list(available_certs.keys())[cert_type_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue        
        
def choose_cert_file(config_file=""):
    while True:
        try:
            cert_files=get_filenames(folder=get_certs_folder(config_file=config_file))
            i=0
            print("Available Inbound Cert files: ")
            for cert_file in cert_files:
                i=i+1
                print(str(i)+" - "+cert_file)
            cert_file_option=int(input("Choose Inbound Cert file: "))
            if type(cert_file_option)!=int or cert_file_option > len(cert_files) or cert_file_option<1:
                raise Exception("Invalid Option!")
            return cert_files[cert_file_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue
        
def upload_cert(host="",port="",auth=(),certpath="",cert_type="",instance={},pair_cer_path="",der_alias="",update_crx_de=False):
    try:
        if not certpath.endswith(".pem"):
            if (certpath.endswith(".cer") or certpath.endswith(".crt")) and pair_cer_path=="":
                pre_upload_truststore=get_truststore_certs(host=host,port=port,auth=auth)
                upload_to_truststore(host=host,port=port,auth=auth,cer_file_path=certpath)
                post_upload_truststore=get_truststore_certs(host=host,port=port,auth=auth)
                uploaded_cert={}
                for post_cert in post_upload_truststore:
                    if post_cert not in pre_upload_truststore:
                        uploaded_cert=post_cert
                print("Uploaded Cert To Truststore: ")
                print(uploaded_cert)
                if update_crx_de:
                    osgipath=instance['inboundosgipaths'][cert_type]
                    updates=[]
                    updates.append(create_update(osgipath=osgipath,key="idpCertAlias",value=uploaded_cert['alias']))
                    update_certs_crx_de_values(host=host,port=port,auth=auth,updates=updates)                                
            elif certpath.endswith(".der") and pair_cer_path!="" and der_alias!="":
                pre_upload_keystore=get_keystore_certs(host=host,port=port,auth=auth)
                upload_to_keystore(host=host,port=port,auth=auth,alias=der_alias,cer_file_path=pair_cer_path,der_file_path=certpath)
                post_upload_keystore=get_keystore_certs(host=host,port=port,auth=auth)
                uploaded_cert={}
                for post_cert in post_upload_keystore:
                    if post_cert not in pre_upload_keystore:
                        uploaded_cert=post_cert
                print("Uploaded Cert To Keystore: ")
                print(uploaded_cert)
                if update_crx_de:
                    osgipath=instance['inboundosgipaths'][cert_type]
                    if len(uploaded_cert)==0:
                        for post_cert in post_upload_keystore:
                            if der_alias in post_cert.values():
                                uploaded_cert=post_cert
                    updates=[]
                    updates.append(create_update(osgipath=osgipath,key="spPrivateKeyAlias",value=uploaded_cert['alias']))
                    update_certs_crx_de_values(host=host,port=port,auth=auth,updates=updates)                      
            else:
                raise Exception("Invalid Arguments!")
        else:
            upload_pemfile(host=host,port=port,auth=auth,filepath=certpath,osgipath=instance['inboundosgipaths'][cert_type])
                        
    except Exception as e:
        print("Error In Uploading Cert File "+certpath+"! error: "+str(e))

def upload_certs_to_environment(config_file="",environment=[],name="",certs_folder="",certpath="",cert_type=""):
    try:
        print("Starting Upload Process to all instances in "+name+"....")
        update_crx_de_option=input("Do you want to update crx de values? (y/n): ")
        update_crx_de=False
        if update_crx_de_option.strip()!="":
            if update_crx_de_option=="y" or update_crx_de_option=="Y":
                update_crx_de=True
            elif update_crx_de_option=="n" or update_crx_de_option=="N":
                update_crx_de_option=False
            else:
                print("Invalid Option!") 
        while(update_crx_de_option.strip()==""):
            update_crx_de_option=input("Do you want to update crx de values? (y/n): ")
            if update_crx_de_option=="y" or update_crx_de_option=="Y":
                update_crx_de=True
            elif update_crx_de_option=="n" or update_crx_de_option=="N":
                update_crx_de_option=False
            else:
                print("Invalid Option!")
        if certpath.endswith(".cer") or certpath.endswith(".crt") or certpath.endswith(".pem") :
            for instance in environment:
                print("Uploading In Instance: "+instance['host']+":"+instance['port']+".....")
                upload_cert(host=instance['host'],port=instance['port'],auth=(instance['username'],instance['password']),certpath=certs_folder+certpath,cert_type=cert_type,instance=instance,pair_cer_path="",der_alias="",update_crx_de=update_crx_de)
                print("Uploaded to Instance: "+instance['host']+":"+instance['port']+" Successfully!")
        elif certpath.endswith(".der"):
            print("Choose cer/crt to pair with der file in keystore: ")
            cer_file=choose_cert_file(config_file=config_file)
            print("selected cer file: "+cer_file+" , selected der file: "+certpath)
            der_alis=input("Type Alias for der file in keystore: ")
            while(der_alis.strip()==""):
                der_alis=input("Type Alias for der file in keystore: ")
            for instance in environment:
                print("Uploading In Instance: "+instance['host']+":"+instance['port']+".....")
                upload_cert(host=instance['host'],port=instance['port'],auth=(instance['username'],instance['password']),certpath=certs_folder+certpath,cert_type=cert_type,instance=instance,pair_cer_path=certs_folder+cer_file,der_alias=der_alis,update_crx_de=update_crx_de)
                print("Uploaded to Instance: "+instance['host']+":"+instance['port']+" Successfully!")
        print("Upload Process to all instances in "+name+" Completed Successfully!")
    except Exception as e:
        print("Error In Uploading Cert to environment: "+name+"! error: "+str(e))
        
def view_current_certs(environment=[],instance={}):
    print("Current Certs in instance - "+instance["host"]+":"+instance["port"]+":- ")
    truststore_certs,keystore_certs=get_certs_from_instance(environment=environment,hostoption=environment.index(instance)+1)
    print("Trust Store Certs: ")
    for i in truststore_certs:
        print(i)
    print("Key Store Certs: ")
    for i in keystore_certs:
        print(i)
        
def view_current_alias(instance={},cert_type=""):
    try:
        endpoint="http://"+instance["host"]+":"+instance["port"]+"/crx/server/crx.default/jcr:root"+instance["inboundosgipaths"][cert_type]+".json"
        response = requests.get(endpoint,auth=(instance["username"],instance["password"]))
        if cert_type!="privatekey":
            print(cert_type+" alias for instance: "+instance["host"]+":"+instance["port"]+":- ")
            print("idpCertAlias: "+response.json()["idpCertAlias"])
            print("spPrivateKeyAlias: "+response.json()["spPrivateKeyAlias"])
        else:
            print("PrivateKey for instance: "+instance["host"]+":"+instance["port"]+":- ")
            print("getUSBankPrivateKey: "+response.json()["getUSBankPrivateKey"])
    except Exception as e:
        print("Exception Error Occured In Fetching cert value! error: "+str(e))

def choose_hostoption(environment=[]):
    while True:
        try:
            instances=environment
            i=0
            print("Available Instances: ")
            for instance in instances:
                i=i+1
                print(str(i)+" - "+instance["host"]+":"+instance["port"])
            instance_option=int(input("Choose Instance: "))
            if type(instance_option)!=int or instance_option > len(instances) or instance_option<1:
                raise Exception("Invalid Option!")
            return instances[instance_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue

def actions_menu():
    while True:
        try:
            options=["view current certs","view current cert values in crx de","upload certs"]
            i=0
            for option in options:
                i=i+1
                print(str(i)+" - "+option) 
            selected_option=int(input("Choose Option: "))
            if type(selected_option)!=int or selected_option > len(options) or selected_option<1:
                raise Exception("Invalid Option!")
            return options[selected_option-1]          
        except:
            print("Invalid Option!")
            continue

def upload_process(config_file="",certs_folder="",environment=[],env=""):
    cert_type=choose_cert_type(config_file=config_file,cert_variation="inbound",environment=environment)
    print("Selected Inbound Cert Type: "+cert_type)
    cert_file=choose_cert_file(config_file=config_file)
    print("Selected Cert File: "+cert_file)
    upload_certs_to_environment(config_file=config_file,environment=environment,name=env,certs_folder=certs_folder,certpath=cert_file,cert_type=cert_type)

def main(config_file=config_file):
    env=choose_environment(config_file=config_file)
    certs_folder=get_certs_folder(config_file=config_file)
    print("Selected Environment: "+env)
    environment=get_environment(config_file=config_file,env=env)
    action=actions_menu()
    if action=="upload certs":
        upload_process(config_file=config_file,certs_folder=certs_folder,environment=environment,env=env)
    elif action=="view current certs":
        instance=choose_hostoption(environment=environment)
        view_current_certs(environment=environment,instance=instance)
    elif action=="view current cert values in crx de":
        instance=choose_hostoption(environment=environment)
        cert_type=choose_cert_type(config_file=config_file,cert_variation="inbound",environment=environment)
        view_current_alias(instance=instance,cert_type=cert_type)
    print("End of Script!")

main(config_file=config_file)