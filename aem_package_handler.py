#!/usr/bin/env python3
import requests
import json


host="localhost"
port="4502"
user="admin"
password="admin"


remoteHost="localhost"
remotePort="4503"
remoteUser="admin"
remotePassword="admin"

auth=(user,password)
remoteAuth=(user,password)

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
    print("[+] Package Created")

# def create_remote_package(packageName="",groupName="my_packages",packageVersion=""):
#     url="http://"+remoteHost+":"+remotePort+"/crx/packmgr/"
#     path="service/exec.json?cmd=create"
#     endpoint=url+path
#     data = {'packageName':packageName,'groupName':groupName,'packageVersion':packageVersion}
#     response = requests.post(endpoint, auth=remoteAuth, headers=headers,data=data)
#     print(str(response.status_code)+" "+ str(response.json()))
#     print("[+] Package Created")

def add_filters(auth=(),host="",port="",packageName="",packageVersion="",groupName="my_packages",description="",filters_file_path=None):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/packmgr/"
    endpoint=url+"update.jsp"
    path=""
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    filters=get_filters_from_file(filters_file_path)
    path="/etc/packages/my_packages/"+fullPackageName+".zip"
    data={"path":path,"packageName":packageName,"groupName":groupName,"version":packageVersion,"description":description,"filter":filters}
    response = requests.post(endpoint,headers=headers,auth=auth,files=multipartify(data))
    print(str(response.status_code)+" "+ str(response.json()))
    print("[+] Filters Added")

# def add_remote_filters(packageName="",packageVersion="",groupName="my_packages",description="",filters_file_path=None):
#     url="http://"+remoteHost+":"+remotePort+"/crx/packmgr/"
#     endpoint=url+"update.jsp"
#     path=""
#     fullPackageName=packageName
#     if(packageVersion!=""):
#         fullPackageName=fullPackageName+"-"+packageVersion
#     filters=get_filters_from_file(filters_file_path)
#     path="/etc/packages/my_packages/"+fullPackageName+".zip"
#     data={"path":path,"packageName":packageName,"groupName":groupName,"version":packageVersion,"description":description,"filter":filters}
#     response = requests.post(endpoint,headers=headers,auth=remoteAuth,files=multipartify(data))
#     print(str(response.status_code)+" "+ str(response.json()))
#     print("[+] Filters Added")

def handle_package(auth=(),host="",port="",packageName="",packageVersion="",action=""):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/packmgr/"
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    path='service/.json/etc/packages/my_packages/'+fullPackageName+'.zip?cmd='+action
    endpoint=url+path
    response = requests.post(endpoint,headers=headers,auth=auth)
    print(str(response.status_code)+" "+ str(response.json()))
    print("[+] Package "+action+" Successfull")

def download_package(auth=(),host="",port="",packageName="",packageVersion=""):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    endpoint="http://"+host+":"+port+"/etc/packages/my_packages/"+fullPackageName+".zip"
    response = requests.get(endpoint,auth=auth,headers=headers)
    open(fullPackageName+".zip","wb").write(response.content)
    print("[+] Package Downloaded")

def list_packages(auth=(),host="",port="",query=""):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/packmgr/"
    path='list.jsp?includeVersions=true&q='+query
    endpoint=url+path
    response = requests.post(endpoint,headers=headers,auth=auth)
    results=response.json()['results']
    for i in results:
        print(i['downloadName'])
    print("[+] Package List Successfull")

# def list_remote_packages(query=""):
#     url="http://"+remoteHost+":"+remotePort+"/crx/packmgr/"
#     path='list.jsp?includeVersions=true&q='+query
#     endpoint=url+path
#     response = requests.post(endpoint,headers=headers,auth=remoteAuth)
#     results=response.json()['results']
#     for i in results:
#         print(i['downloadName'])
#     print("[+] Package List Successfull")

def list_filters(auth=(),host="",port="",packageName="",packageVersion=""):
    headers = {'Referer': 'http://'+host+':'+port+'/crx/packmgr/index.jsp'}
    url="http://"+host+":"+port+"/crx/packmgr/"
    fullPackageName=packageName
    if(packageVersion!=""):
        fullPackageName=fullPackageName+"-"+packageVersion
    path='list.jsp?includeVersions=false&q='+fullPackageName+".zip"
    endpoint=url+path
    response = requests.get(endpoint,auth=auth,headers=headers)
    results=response.json()['results'][0]['filter']
    for i in results:
        print(i['root'])
    print("[+] Filters List Successfull")

# def list_remote_filters(packageName="",packageVersion=""):
#     url="http://"+remoteHost+":"+remotePort+"/crx/packmgr/"
#     fullPackageName=packageName
#     if(packageVersion!=""):
#         fullPackageName=fullPackageName+"-"+packageVersion
#     path='list.jsp?includeVersions=false&q='+fullPackageName+".zip"
#     endpoint=url+path
#     response = requests.get(endpoint,auth=remoteAuth,headers=headers)
#     results=response.json()['results'][0]['filter']
#     for i in results:
#         print(i['root'])
#     print("[+] Filters List Successfull")


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
    print("[+] Package Uploaded")

# def handle_remote_package(packageName="",packageVersion="",action=""):
#     url="http://"+remoteHost+":"+remotePort+"/crx/packmgr/"
#     fullPackageName=packageName
#     if(packageVersion!=""):
#         fullPackageName=fullPackageName+"-"+packageVersion
#     path='service/.json/etc/packages/my_packages/'+fullPackageName+'.zip?cmd='+action
#     endpoint=url+path
#     response = requests.post(endpoint,headers=headers,auth=remoteAuth)
#     print(str(response.status_code)+" "+ str(response.json()))
#     print("[+] Package "+action+" Successfull")

# def download_remote_package(packageName="",packageVersion=""):
#     fullPackageName=packageName
#     if(packageVersion!=""):
#         fullPackageName=fullPackageName+"-"+packageVersion
#     endpoint="http://"+remoteHost+":"+remotePort+"/etc/packages/my_packages/"+fullPackageName+".zip"
#     response = requests.get(endpoint,auth=remoteAuth,headers=headers)
#     open(fullPackageName+".zip","wb").write(response.content)
#     print("[+] Package Downloaded")

def menu():
    return'''
        1  - List All AEM Packages
        2  - Search AEM Package
        3  - Create New Package
        4  - Add Filters to the Package
        5  - List Package Filters
        6  - Build Package
        7  - Install Package
        8  - Delete Package
        9  - Download Package
        10  - Upload Package
        11 - List All Remote AEM Packages
        12 - List Remote Package Filters
        13 - Search Remote AEM Package
        14 - Create Remote AEM Package
        15 - Add Filters to Remote AEM Package
        16 - Build Remote Package
        17 - Install Remote Package
        18 - Delete Remote Package
        19 - Download Remote Package
        20 - Exit
    '''

def main():
    while True:
        print(menu())
        choice=input("Enter Choice: ")
        print("selected Choice: "+choice)
        if int(choice)<1 or int(choice) >20:
            print("Incorrect Choice, Please Try Again!")
            continue
        if choice=="20":
            break
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
        elif choice=="5":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("package name required")
                continue
            packageVersion=input("Version (default=blank): ")
            list_filters(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion)
        elif choice=="6":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion,action="build")
        elif choice=="7":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion,action="install")
        elif choice=="8":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion,action="delete")
        elif choice=="9":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            packageVersion=input("Version (default=blank): ")
            download_package(auth=auth,host=host,port=port,packageName=packageName,packageVersion=packageVersion)
        elif choice=="10":
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
        elif choice=="11":
            list_packages(auth=remoteAuth,host=remoteHost,port=remotePort)
        elif choice=="12":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("package name required")
                continue
            packageVersion=input("Version (default=blank): ")
            list_filters(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,packageVersion=packageVersion)
        elif choice=="13":
            query=input("Search By Package Name: ")
            list_packages(auth=remoteAuth,host=remoteHost,port=remotePort,query=query)
        elif choice=="14":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("package name required")
                continue
            groupName=input("Group Name (default=my_packages): ")
            if (groupName==""):
                groupName="my_packages"
            packageVersion=input("Version (default=blank): ")
            create_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,groupName=groupName,packageVersion=packageVersion)
        elif choice=="15":
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
        elif choice=="16":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,packageVersion=packageVersion,action="build")

        elif choice=="17":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,packageVersion=packageVersion,action="install")
        elif choice=="18":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            packageVersion=input("Version (default=blank): ")
            handle_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,packageVersion=packageVersion,action="delete")
        elif choice=="19":
            packageName=input("Package Name : ")
            if(packageName==""):
                print("Package Name Required")
                continue
            packageVersion=input("Version (default=blank): ")
            download_package(auth=remoteAuth,host=remoteHost,port=remotePort,packageName=packageName,packageVersion=packageVersion)
        
        else:
            print("Incorrect Choice, Please Try Again!")
            continue
    
    print("[+] Script Exited!")


main()