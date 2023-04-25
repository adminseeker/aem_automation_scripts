import sys
import base64
import yaml
import requests
from yaml.loader import SafeLoader

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

config_file="content-deploy-config.yaml"

def config_sharepoint_init(config_file=""):
    try:
        username=""
        password=""
        site_url=""
        file_url=""
        with open(config_file, 'r') as f:
            data = list(yaml.load_all(f, Loader=SafeLoader))
            username=data[0]['sharepoint']['username']    
            password=base64.b64decode(data[0]['sharepoint']['password']).decode("utf-8")
            site_url=data[0]['sharepoint']['siteurl']
            file_url=data[0]['sharepoint']['fileurl']
        return UserCredential(username,password),site_url,file_url
    except Exception as e:
        print("Error in reading config file: "+str(e))

def get_file_name(fileName=""):
     file_path=fileName
     if "/" in file_path and "\\" not in file_path:
             file_path=fileName.split("/").pop()
             return file_path
     elif "\\" in file_path and "/" not in file_path:
             file_path=fileName.split("\\").pop()
             return file_path
     elif  "/" not in file_path and "\\" not in file_path:
            file_path=fileName
            return file_path
     else:
        print("Error in File Name")
        return fileName

def get_sharepoint_ctx(site_url="",user_credentials=None):
    return ClientContext(site_url).with_credentials(user_credentials)

def get_sharepoint_files(ctx=None,file_url=""):
    target_folder = ctx.web.get_folder_by_server_relative_url(file_url)
    file_names = []  
    sub_folders = target_folder.files   
    ctx.load(sub_folders)  
    ctx.execute_query()  
    for file in sub_folders:
        file_names.append(file.properties["Name"])
    return file_names

def get_sharepoint_folders(ctx=None,file_url=""):
    target_folder = ctx.web.get_folder_by_server_relative_url(file_url)
    file_names = []  
    sub_folders = target_folder.folders   
    ctx.load(sub_folders)  
    ctx.execute_query()  
    for file in sub_folders:
        file_names.append(file.properties["Name"])
    return file_names

def choose_package_to_install(ctx=None, file_url=""):
    while True:
        try:
            print("Fetching Packages in Sharepoint.....")
            files=get_sharepoint_files(ctx=ctx,file_url=file_url)
            i=0
            print("Available Packages In Sharepoint: ")
            for name in files:
                i=i+1
                print(str(i)+" - "+name)
            file_option=int(input("Choose Package: "))
            if type(file_option)!=int or file_option > len(files) or file_option<1:
                raise Exception("Invalid Option!")
            return files[file_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue
        
def choose_release_year(ctx=None, file_url=""):
    while True:
        try:
            files=get_sharepoint_folders(ctx=ctx,file_url=file_url)
            i=0
            print("Release Years: ")
            for name in files:
                i=i+1
                print(str(i)+" - "+name)
            file_option=int(input("Choose Release Year: "))
            if type(file_option)!=int or file_option > len(files) or file_option<1:
                raise Exception("Invalid Option!")
            return files[file_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue

def choose_release_date(ctx=None, file_url="",release_year=""):
    while True:
        try:
            files=get_sharepoint_folders(ctx=ctx,file_url=file_url+"/"+release_year)
            i=0
            print("Release Dates: ")
            for name in files:
                i=i+1
                print(str(i)+" - "+name)
            file_option=int(input("Choose Release Date: "))
            if type(file_option)!=int or file_option > len(files) or file_option<1:
                raise Exception("Invalid Option!")
            return files[file_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue

def download_package_from_sharepoint(ctx=None,file_url=""):
    try:
        package=choose_package_to_install(ctx=ctx,file_url=file_url)
        print("Downloading Package:  "+package+"....")
        with open(package, "wb") as local_file:
            if not file_url.endswith("/"):
                file_url+="/"
            ctx.web.get_file_by_server_relative_url(file_url+package).download(local_file)
            ctx.execute_query()
        print("Package: "+package+" Downloaded!")
        return package
    except Exception as e:
        print("Exception in downloading package from sharepoint method: "+str(e))
        sys.exit(-1)
        
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

def choose_installation_method():
    while True:
        try:
            modes=["Replication Via Author","Manual"]
            i=0
            print("Available Installation Modes: ")
            for name in modes:
                i=i+1
                print(str(i)+" - "+name)
            install_option=int(input("Choose Installation Method: "))
            if type(install_option)!=int or install_option > len(modes) or install_option<1:
                raise Exception("Invalid Option!")
            return modes[install_option-1]
        except Exception as e:
            print("Invalid Option!")
            continue

def upload_package(auth=(),host="",port="",file_path=None,install="false",force="true"):
    try:
        headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
        path="crx/packmgr/service.jsp"
        url="http://"+host+":"+port+"/"
        endpoint=url+path
        fileName=file_path
        if len(fileName.split("/"))!=0:
            file_path=fileName.split("/").pop()
        if len(fileName.split("\\"))!=0:
            file_path=fileName.split("\\").pop()
        files={'file': (get_file_name(file_path),open(file_path,'rb'),'application/octet-stream')}
        data={"force":force,"install":install}
        response = requests.post(endpoint,headers=headers,auth=auth,data=data,files=files)
        if response.status_code==200:
            print("Uploaded Successfully!")
            name=response.text.split("<name>")[1].split("</name>")[0]
            group=response.text.split("<group>")[1].split("</group>")[0]
            version=response.text.split("<version>")[1].split("</version>")[0]
            return name,group,version
        else:
            print("Upload Package Error!")
    except Exception as e:
        print("Exception in upload package: "+str(e))
        sys.exit(-1)
  
def replicate_package(auth=(),host="",port="",packageName="",packageVersion="",groupName=""):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    path="crx/packmgr/service/script.html/etc/packages/"+groupName+"/"
    url="http://"+host+":"+port+"/"
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    fullPackageName=fullPackageName+".zip"   
    endpoint=url+path+fullPackageName
    data={'cmd':'replicate'}
    print(endpoint)
    response = requests.post(endpoint,headers=headers,auth=auth,data=data)
    print(str(response.status_code)+" "+ response.text.split("*").pop().split("<textarea>").pop().split("</textarea>")[0])
    
def replication_via_author(environment=None,package_path=""):
    try:
        author_present=False
        author_instance={}
        for instance in environment:
            if instance['type']=="author":
                author_present=True
                author_instance=instance
                break
        if not author_present:
            raise Exception("Author Not Found! Please Try another installation Methods or Update config file with author info")
        install="false"
        install_option=input("Do you want to install (y/n): ")
        while(install_option.strip()!="y" and install_option.strip()!="Y" and install_option.strip()!="n" and install_option.strip()!="N"):
            print("Invalid Option!")
            install_option=input("Do you want to install (y/n): ")
        if install_option=="y" or install_option=="Y":
            install="true"
        elif install_option=="n" or install_option=="N":
            install="false"
            print("Installation Cancelled!")
        package_name,group,version=upload_package(auth=(author_instance["username"],author_instance["password"]),host=author_instance['host'],port=author_instance["port"],file_path=package_path,install=install,force=True)
        if install=="true":
            replicate_option=input("Do you want to replicate (y/n): ")
            while(replicate_option.strip()!="y" and replicate_option.strip()!="Y" and replicate_option.strip()!="n" and replicate_option.strip()!="N"):
                print("Invalid Option!")
                replicate_option=input("Do you want to replicate (y/n): ")
            if replicate_option=="y" or replicate_option=="Y":
                replicate_package(auth=(author_instance["username"],author_instance["password"]),host=author_instance['host'],port=author_instance["port"],packageName=package_name,packageVersion=version,groupName=group)
            elif replicate_option=="n" or replicate_option=="N":
                print("Replication Cancelled!")
    except Exception as e:
        print("Exception in Replication Via Author Install: "+str(e))
        sys.exit(-1)
            
def manual_install(environment=None,package_path=""):
    try:
        publishers=[]
        author={}
        for instance in environment:
            if instance['type']=="author":
                author=instance
            else:
                publishers.append(instance)
        for instance in publishers:
            print(".......................................................................")
            print("Current Instance: "+instance['name'])
            upload_option=input("Do you want to upload package "+package_path+"? (y/n): ")
            while(upload_option.strip()!="y" and upload_option.strip()!="Y" and upload_option.strip()!="n" and upload_option.strip()!="N"):
                print("Invalid Option!")
                upload_option=input("Do you want to upload package "+package_path+"? (y/n): ")
            if upload_option=="y" or upload_option=="Y":
                install="false"
                install_option=input("Do you want to install package "+package_path+"? (y/n): ")
                while(install_option.strip()!="y" and install_option.strip()!="Y" and install_option.strip()!="n" and install_option.strip()!="N"):
                    print("Invalid Option!")
                    install_option=input("Do you want to install package "+package_path+"? (y/n): ")
                if install_option=="y" or install_option=="Y":
                    install="true"
                elif install_option=="n" or install_option=="N":
                    install="false"
                    print("Installation Cancelled!")
                upload_package(auth=(instance["username"],instance["password"]),host=instance['host'],port=instance["port"],file_path=package_path,install=install,force=True)
            elif upload_option=="n" or upload_option=="N":
                print("Upload Cancelled for the instance: "+instance['name'])
                
        if len(author.keys()) !=0 :
            instance=author
            print(".......................................................................")
            print("Current Instance: "+instance['name'])
            upload_option=input("Do you want to upload package "+package_path+"? (y/n): ")
            while(upload_option.strip()!="y" and upload_option.strip()!="Y" and upload_option.strip()!="n" and upload_option.strip()!="N"):
                print("Invalid Option!")
                upload_option=input("Do you want to upload package "+package_path+"? (y/n): ")
            if upload_option=="y" or upload_option=="Y":
                install="false"
                install_option=input("Do you want to install package "+package_path+"? (y/n): ")
                while(install_option.strip()!="y" and install_option.strip()!="Y" and install_option.strip()!="n" and install_option.strip()!="N"):
                    print("Invalid Option!")
                    install_option=input("Do you want to install package "+package_path+"? (y/n): ")
                if install_option=="y" or install_option=="Y":
                    install="true"
                elif install_option=="n" or install_option=="N":
                    install="false"
                    print("Installation Cancelled!")
                upload_package(auth=(instance["username"],instance["password"]),host=instance['host'],port=instance["port"],file_path=package_path,install=install,force=True)
            elif upload_option=="n" or upload_option=="N":
                print("Upload Cancelled for the instance: "+instance['name'])
            
    except Exception as e:
        print("Exception in Manual Install: "+str(e))
        sys.exit(-1)
        
def install_package(config_file="",package_path=""):
    try:
        env=choose_environment(config_file=config_file)
        environment=get_environment(config_file=config_file,env=env)
        install_method=choose_installation_method()
        if "Replication Via Author" in install_method:
            replication_via_author(environment=environment,package_path=package_path)                                       
        elif "Manual" in install_method:
            manual_install(environment=environment,package_path=package_path)
        else:
            raise Exception("Invalid Option")
    except Exception as e:
        print("Exception in Install package: "+str(e))
        sys.exit(-1)
        
def main():
    print("Connecting to Sharepoint....")
    user_credentials,site_url,file_url = config_sharepoint_init(config_file=config_file)
    ctx=get_sharepoint_ctx(site_url=site_url,user_credentials=user_credentials)
    year=choose_release_year(ctx=ctx,file_url=file_url)
    date=choose_release_date(ctx=ctx,file_url=file_url,release_year=year)
    package=download_package_from_sharepoint(ctx=ctx,file_url=file_url+"/"+year+"/"+date)
    install_package(config_file=config_file,package_path=package)
    print("End Of Script!")
    
main()    

