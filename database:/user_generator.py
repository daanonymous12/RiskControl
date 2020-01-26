#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 23:36:32 2020

@author: da
"""
import string
import random 
import pandas as pd 
#This scipt will create a list of user with
#username, stock,Current holding value,# stock, buy,sell amount 
def name_generator():
    length=7
    res = ''.join(random.choices(string.ascii_uppercase +string.digits, k = length))
    return res
def stock_generator(data):
    #open a day trading data,randomly select an interger from 1 to 15796358(len(file))
    #pull the ticker of random interger on csv file 
    ticker=data[1]
    return ticker[random.randint(1,15796358)]
def main():
    #generate 3000 users data
    temp=[]
    data=pd.read_csv('full.csv',header=None)
    for i in range(4000):
        temp.append([name_generator(),stock_generator(data),0,0,random.randint(10,40)/100,random.randint(5,40)/100])
    temp=pd.DataFrame(temp)
    temp.to_csv('user_gen.csv',header=False,index=False)
    
if __name__ == '__main__':
        main()
