#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 17:48:19 2020

@author: da
"""
import io
import boto3
import botocore
import json
from kafka import KafkaProducer
import pandas as pd 

def main():
    #communicate with master node of ec2 instance
    producer=KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket="feb2019taq",Key="a.csv")
    df = pd.read_csv(io.BytesIO(response),header=None,low_memory=False)
    #send 200000 events 
    for i in range(200):    
        for j in range(1000):
            b=list(df.loc[i*1000+j])
            b[0]=int(b[0])
            b[2]=int(b[2])
            producer.send(topic='test',value=b)
        producer.flush()
if __name__ == '__main__':
        main()
