#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import boto3
import json
from kafka import KafkaProducer
import pandas as pd


def main():
    """
    Opens historical trade data from amazon S3 and sends them into Kafka.
    """
    flush_amount = 10000
    # communicate with master node of ec2 instance
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket="feb2019taq", Key="0204.csv")
    df = pd.read_csv(response['Body'], header=None, low_memory=False)
    # drop last 2 rows since it contains Nan for some fields
    df.drop(df.tail(2).index, inplace=True)
    df[0] = df[0].astype(dtype=int)
    df[2] = df[2].astype(dtype=int)
    df[3] = df[3].astype(dtype=float)
    for i in range(len(df.index)/flush_amount):
        for j in range(flush_amount):
            b = list(df.iloc[i*flush_amount+j])
            producer.send(topic='test', value=b)
        # flushing every 10 thousand rows
        producer.flush()


if __name__ == '__main__':
    main()
