#!/usr/bin/env python3

file1=input("File1 Path: ")
f1=open(file1,"r")

file2=input("File2 Path: ")
f2=open(file2,"r")

f1_arr = []
f2_arr = []

for i in f1.readlines():
    f1_arr.append(i.strip())

for i in f2.readlines():
    f2_arr.append(i.strip())


f1.close()
f2.close()

only_in_f1=[]
only_in_f2=[]

for i in f1_arr:
    if i not in f2_arr:
        only_in_f1.append(i.strip())

for i  in f2_arr:
    if i not in f1_arr:
        only_in_f2.append(i.strip())



if (len(only_in_f1)==0 and len(only_in_f2)==0):
    print("both are identical!")

else:
    if (len(only_in_f1)!=0):
        print("lines only in file1: ")
        for i in only_in_f1:
            print(i.strip())
    if (len(only_in_f2)!=0):
        print("lines only in file2: ")
        for i in only_in_f2:
            print(i.strip())
    
    print("Common Lines: ")
    for i in set(f1_arr).intersection(set(f2_arr)):
        print(i.strip())



