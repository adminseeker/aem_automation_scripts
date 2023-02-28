#!/usr/bin/env python3

file1=input("File Path: ")
f1=open(file1,"r")

f1_arr = []

for i in f1.readlines():
    f1_arr.append(i.strip())

f1_set=set()
duplicates=[]

for i in f1_arr:
    if i in f1_set:
        duplicates.append(i)
    else:
        f1_set.add(i)

if(len(duplicates)==0):
    print("No Duplicate!")
else:
    print("Duplicates Found: ")
    for i in duplicates:
        print(i)
