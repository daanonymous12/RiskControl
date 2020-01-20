#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 13:20:16 2020

@author: da
"""

import pandas as pd 
import gzip
import os 
tem_list=[]
for filename in os.listdir('Feb2019TAQ'):
    f=gzip.open('/home/ubuntu/Feb2019TAQ/'+filename,'r')
    for i in f:
        s=f.readline().decode().split('|')
        if len(s)<4:
            continue
        else:
            tem_list.append([s[0],s[2],s[4],s[5]])
tem_list=pd.DataFrame(tem_list)
tem_list.to_csv('data.csv',header=False,index=False)
