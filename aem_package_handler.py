#!/usr/bin/env python3
import requests
import time
import yaml
from yaml.loader import SafeLoader




host="localhost"
port="4502"
user="admin"
password="admin"


remoteHost="localhost"
remotePort="4503"
remoteUser="admin"
remotePassword="admin"

auth=(user,password)
remoteAuth=(remoteUser,remotePassword)


packages=[]

try:
    with open('packages.yaml', 'r') as f:
        data = list(yaml.load_all(f, Loader=SafeLoader))
        packages=data[0]['packages']
except:
    iscontinue=input("No packages.yaml found!, Do you want to continue? (some options may fail!)") 
    pass

url = "http://"+host+":"+port+"/crx/packmgr/"

def multipartify(data):
    return {key:(None,data[key]) for key in data}

def get_filters_from_file(file=None):
    f = open(file,"r")
    filters=[]
    for i in f.readlines():
        if i.strip() == "":
            continue
        filter=i.strip()
        filters.append({"root":filter,"rules":[]})
    return str(filters)

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

def create_package(auth=(),host="",port="",packageName="",groupName="my_packages",packageVersion=""):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/packmgr/"
    path="service/exec.json?cmd=create"
    endpoint=url+path
    data = {'packageName':packageName,'groupName':groupName,'packageVersion':packageVersion}
    response = requests.post(endpoint, auth=auth, headers=headers,data=data)
    print(str(response.status_code)+" "+ str(response.json()))

def add_filters(auth=(),host="",port="",packageName="",packageVersion="",groupName="my_packages",description="",filters_file_path=None):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/packmgr/"
    endpoint=url+"update.jsp"
    path=""
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    filters=get_filters_from_file(filters_file_path)
    path="/etc/packages/"+groupName+"/"+fullPackageName+".zip"
    data={"path":path,"packageName":packageName,"groupName":groupName,"version":packageVersion,"description":description,"filter":filters}
    response = requests.post(endpoint,headers=headers,auth=auth,files=multipartify(data))
    print(str(response.status_code)+" "+ str(response.json()))

def handle_package(auth=(),host="",port="",packageName="",packageVersion="",groupName="my_packages",action=""):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/packmgr/"
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    path='service/.json/etc/packages/'+groupName+'/'+fullPackageName+'.zip?cmd='+action
    endpoint=url+path
    response = requests.post(endpoint,headers=headers,auth=auth)
    print(str(response.status_code)+" "+ str(response.json()))

def download_package(auth=(),host="",port="",packageName="",packageVersion="",groupName="my_packages"):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    endpoint="http://"+host+":"+port+"/etc/packages/"+groupName+"/"+fullPackageName+".zip"
    response = requests.get(endpoint,auth=auth,headers=headers)
    open(fullPackageName+".zip","wb").write(response.content)

def download_packages_from_yml(auth=(),host="",port="",packages=[]):
    print(packages)
    for package in packages:
        download_package(auth=auth,host=host,port=port,packageName=package['name'],packageVersion=package['version'],groupName=package['groupName'])
        print("Downloaded Package: "+package['name'])


def build_packages_from_yml(auth=(),host="",port="",packages=[]):
    for package in packages:
        handle_package(auth=auth,host=host,port=port,packageName=package['name'],packageVersion=package['version'],groupName=package['groupName'],action="build")
        print("Built Package: "+package['name'])


def list_packages(auth=(),host="",port="",query=""):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/packmgr/"
    path='list.jsp?includeVersions=true&q='+query
    endpoint=url+path
    response = requests.post(endpoint,headers=headers,auth=auth)
    results=response.json()['results']
    for i in results:
        print(i['downloadName'])

def list_filters(auth=(),host="",port="",packageName="",packageVersion="",groupName=""):
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
        print(i['root'])
    print("Total: "+str(len(results)))

def upload_package(auth=(),host="",port="",file_path=None,install="false",force="true"):
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
    # print(response.status_code)
    print(str(response.status_code)+" "+ response.text.split("*").pop().split("<textarea>").pop().split("</textarea>")[0])
        
def run_automation(auth=(),remoteAuth=(),host="",port="",remoteHost="",remotePort="",packageName="",groupName="",packageVersion="",packageDescription=""):
    try:
        f=open("filters.txt","r")
        if len(f.readlines())==0:
            print("No Filters Present in filters.txt")
            raise Exception("No Filters Present in filters.txt")
    except Exception:
        print("Error with filters")
        return
    print("Creating Package....")
    time.sleep(2)
    create_package(auth=auth,host=host,port=port,packageName=packageName,groupName=groupName,packageVersion=packageVersion)
    print("--------------------------------------------------------------------------")
    print("Adding Filters....")
    time.sleep(2)
    add_filters(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion,groupName=groupName,description=packageDescription,filters_file_path="filters.txt")   
    print("--------------------------------------------------------------------------")
    print("Listing Filters....")
    time.sleep(2)
    list_filters(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion,groupName=groupName)
    print("--------------------------------------------------------------------------")
    print("Building Package....")
    time.sleep(2)
    handle_package(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion,groupName=groupName,action="build")
    print("--------------------------------------------------------------------------")
    print("Downloading Package....")
    time.sleep(2)
    download_package(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion,groupName=groupName)
    print("--------------------------------------------------------------------------")
    install=input("Upload And Install? (default: false) : ")
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    fullPackageName=fullPackageName+".zip"
    if install=="true":   
        print("Uploading And Installing Package....") 
        time.sleep(2)
        upload_package(auth=remoteAuth,host=remoteHost,port=remotePort,install=install,force="true",file_path=fullPackageName)

    elif install=="false":
        print("Uploading Package....")
        time.sleep(2)
        upload_package(auth=remoteAuth,host=remoteHost,port=remotePort,install=install,force="true",file_path=fullPackageName)
    else:
        print("incorrect Choice, taking default value as false")
        time.sleep(2)
        upload_package(auth=remoteAuth,host=remoteHost,port=remotePort,install="false",force="true",file_path=fullPackageName)
        
    print("--------------------------------------------------------------------------")
    print("Listing Remote Packages....")
    time.sleep(2)
    list_packages(auth=remoteAuth,host=remoteHost,port=remotePort,query=fullPackageName)
    print("--------------------------------------------------------------------------")
    print("Listing Remote Filters....")
    time.sleep(2)
    list_filters(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,packageVersion=packageVersion,groupName=groupName)
    print("--------------------------------------------------------------------------")
    if install=="true":
        replicate=input("Replicate? (default: false) : ")
        if replicate=="true":
            print("Replicating....")
            time.sleep(2)
            replicate_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,packageVersion=packageVersion,groupName=groupName)  
        else:
            print("Replication Aborted....")
    print("--------------------------------------------------------------------------")

def menu():
    return'''
        0  - Automate
        1  - List All AEM Packages
        2  - Search AEM Package
        3  - Create New Package
        4  - Add Filters to the Package
        5  - List Package Filters
        6  - Build Package
        7  - Build All Packages From packages.yaml
        8  - Install Package
        9  - Replicate Package
        10  - Delete Package
        11  - Download Package
        12  - Download All Packages From packages.yaml
        13  - Upload Package
        14 - List All Remote AEM Packages
        15 - List Remote Package Filters
        16 - Search Remote AEM Package
        17 - Create Remote AEM Package
        18 - Add Filters to Remote AEM Package
        19 - Build Remote Package
        20 - Build All Remote Packages From packages.yaml
        21 - Install Remote Package
        22 - Replicate Remote Package
        23 - Delete Remote Package
        24 - Download Remote Package
        25  - Download All Remote Packages From packages.yaml
        26 - Exit
    '''

def main():
    while True:
        print(menu())
        choice=input("Enter Choice: ")
        print("selected Choice: "+choice)
        if int(choice)<0 or int(choice) >26:
            print("Incorrect Choice, Please Try Again!")
            continue
        if choice=="26":
            break
        if choice=="0":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            packageDescription=input("Description (default=blank): ")
            run_automation(auth=auth,remoteAuth=remoteAuth,host=host,port=port,remoteHost=remoteHost,remotePort=remotePort,packageName=packageName,groupName=groupName,packageVersion=packageVersion,packageDescription=packageDescription)
            print("[+] Automation Successfull")
        elif choice=="1":
            list_packages(auth=auth,host=host,port=port)
        elif choice=="2":
            query=input("Search By Package Name: ")
            list_packages(auth=auth,host=host,port=port,query=query)
        elif choice=="3":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("package name required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            create_package(auth=auth,host=host,port=port,packageName=packageName,groupName=groupName,packageVersion=packageVersion)
            print("[+] Package Created")
        elif choice=="4":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            packageDescription=input("Description (default=blank): ")
            filePath=input("Enter Relative File Path Containing Filters: ")
            if(filePath==""):
                print("File Path required")
                continue
            add_filters(auth=auth,host=host,port=port,packageName=packageName,filters_file_path=filePath,packageVersion=packageVersion,groupName=groupName,description=packageDescription)
            print("[+] Filters Created")
        elif choice=="5":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("package name required")
                continue
            packageVersion=input("Version (default=blank): ")
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            list_filters(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion,groupName=groupName)
        elif choice=="6":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=auth,host=host,port=port,packageName=packageName,groupName=groupName,packageVersion=packageVersion,action="build")
            print("[+] Build Successfull")

        elif choice=="7":
            isBuild=input("Bulid All Packages from Yaml? (defualt=true): ")
            if isBuild=="false":
                print("[!]Build Cancelled")
                continue
            build_packages_from_yml(auth=auth,host=host,port=port,packages=packages)
            print("[+] Build Successfull")  

        elif choice=="8":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=auth,host=host,port=port,packageName=packageName,groupName=groupName,packageVersion=packageVersion,action="install")
            print("[+] Install Successfull")
        elif choice=="9":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            replicate_package(auth=auth,host=host,port=port,packageName=packageName,groupName=groupName,packageVersion=packageVersion)
            print("[+] Replication Successfull")              
        elif choice=="10":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=auth,host=host,port=port,packageName=packageName,groupName=groupName,packageVersion=packageVersion,action="delete")
            print("[+] Delete Successfull")            
        elif choice=="11":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            download_package(auth=auth,host=host,port=port,packageName=packageName,groupName=groupName,packageVersion=packageVersion)
            print("[+] Download Successfull")

        elif choice=="12":
            isDownload=input("Download All Packages from Yaml? (defualt=true): ")
            if isDownload=="false":
                print("[!]Download Cancelled")
                continue
            download_packages_from_yml(auth=auth,host=host,port=port,packages=packages)
            print("[+] Download Successfull")  
           
        elif choice=="13":
            force=input("force upload (default=true): ")
            if (force==""):
                force="true"
            install=input("install (default=false): ")
            if (install==""):
                install="false"
            filePath=input("Enter Relative File Path To Upload: ")
            if(filePath==""):
                print("File Path required")
                continue
            upload_package(auth=remoteAuth,host=remoteHost,port=remotePort,file_path=filePath,install=install,force=force)
            print("[+] Upload Successfull") 
        elif choice=="14":
            list_packages(auth=remoteAuth,host=remoteHost,port=remotePort)
        elif choice=="15":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("package name required")
                continue
            packageVersion=input("Version (default=blank): ")
            groupName=input("Group Name : ")
            if (groupName==""):
                groupName="my_packages"
            list_filters(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,packageVersion=packageVersion,groupName=groupName)
        elif choice=="16":
            query=input("Search By Package Name: ")
            list_packages(auth=remoteAuth,host=remoteHost,port=remotePort,query=query)
        elif choice=="17":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("package name required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            create_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,groupName=groupName,packageVersion=packageVersion)
            print("[+] Package Created") 
        elif choice=="18":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            packageDescription=input("Description (default=blank): ")
            filePath=input("Enter Relative File Path Containing Filters: ")
            if(filePath==""):
                print("File Path required")
                continue
            add_filters(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,filters_file_path=filePath,packageVersion=packageVersion,groupName=groupName,description=packageDescription)
            print("[+] Filters Added") 
        elif choice=="19":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,groupName=groupName,packageVersion=packageVersion,action="build")
            print("[+] Build Successfull") 

        elif choice=="20":
            isBuild=input("Bulid All Packages from Yaml? (defualt=true): ")
            if isBuild=="false":
                print("[!]Build Cancelled")
                continue
            build_packages_from_yml(auth=remoteAuth,host=remoteHost,port=remotePort,packages=packages)
            print("[+] Build Successfull")  

        elif choice=="21":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,groupName=groupName,packageVersion=packageVersion,action="install")
            print("[+] Install Successfull")
        elif choice=="22":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            replicate_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,groupName=groupName,packageVersion=packageVersion)
            print("[+] Replication Successfull") 
        elif choice=="23":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,groupName=groupName,packageVersion=packageVersion,action="delete")
            print("[+] Delete Successfull") 
        elif choice=="24":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            download_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,groupName=groupName,packageVersion=packageVersion)
            print("[+] Download Successfull")

        elif choice=="25":
            isDownload=input("Download All Packages from Yaml? (defualt=true): ")
            if isDownload=="false":
                print("[!]Download Cancelled")
                continue
            download_packages_from_yml(auth=remoteAuth,host=remoteHost,port=remotePort,packages=packages)
            print("[+] Download Successfull")  

        else:
            print("Incorrect Choice, Please Try Again!")
            continue
    
    print("[+] Script Exited!")


main()