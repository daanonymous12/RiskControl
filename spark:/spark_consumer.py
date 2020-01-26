#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:37:30 2020

@author: da
"""
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SQLContext
import json
def calculation(rdd):
    rdd.pprint()

if __name__=='__main__':
    sc=SparkContext(appName='test').getOrCreate()
    ssc=StreamingContext(sc,60)
    kafka_stream=KafkaUtils.createDirectStream(ssc,['test'],kafkaParams = {"metadata.broker.list": 'ip-10-0-0-4:9092,ip-10-0-0-5:9092,ip-10-0-0-14:9092'})
    print(1)
    flow=kafka_stream.map(lambda v: json.loads(v.decode('utf-8')))
    flow.foreachRDD(calculation)
    ssc.start()
    ssc.awaitTermination()