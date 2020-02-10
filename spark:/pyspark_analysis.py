#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SQLContext,SparkSession
import json
from pyspark.sql.functions import col, when,floor,abs

def combine(criteria,cass_data):
    user_list=criteria.select('user').rdd.flatMap(lambda x: x ).collect()
    filter_data=cass_data.filter(cass_data.user.isin(user_list)==False)
    cass_data=filter_data.union(criteria)
    writeToCassandra(criteria,'users','user_data')

def looping_funct(flow):
    df=flow.toDF(['time_new','ticker','volume','price'])
    df=df.dropDuplicates(['ticker']) 
    criteria=cass_data.join(df,['ticker'],'inner')
    #drop users whose condition don't need to be calculated  
    criteria=criteria.withColumn('volume',
    when((abs(col('previous_price')-col('price'))<col('buy'))&(
        abs(col('previous_price')-col('price'))<col('sell')),
        0).otherwise(col('volume')))
    writepart=criteria.filter(criteria.volume<1)
    writeToCassandra(writepart,'users','graph_data')
    criteria=criteria.filter(criteria.volume != 0)
    calculation(criteria)


def calculation(criteria):
    #Buy-shares
    criteria=criteria.withColumn('numb_share',
    when(col('previous_price')-col('price')>col('buy'),
        (col('numb_share')+floor(col('cash')/col('price')))
    ).otherwise(col('numb_share')))
    #Buy-total value adjustment
    criteria=criteria.withColumn('total_value',
    when(col('previous_price')-col('price')>col('buy'),
        col('total_value')+floor(col('cash')/col('price'))*col('price')
    ).otherwise(col('total_value')))
    #Buy-cash adjustment
    criteria=criteria.withColumn('cash',
    when(col('previous_price')-col('price')>col('buy'),
        col('cash')-floor(col('cash')/col('price'))*col('price')).otherwise(col('cash')))
    #sell-Profit Calculation
    criteria=criteria.withColumn('profit',
    when(col('price')-col('previous_price')>col('sell'),
       col('profit')+(col('numb_share')*col('price'))-col('total_value')).otherwise(col('profit'))) 
    #sell-cash adjustment 
    criteria=criteria.withColumn('cash',
    when(col('price')-col('previous_price')>col('sell'),
        col('cash')+col('total_value')).otherwise(col('cash')))
    #sell-Total Value adjustment
    criteria=criteria.withColumn('total_value',
    when(col('price')-col('previous_price')>col('sell'),
        0).otherwise(col('total_value')))  
    #Sell-shares adjustment 
    criteria=criteria.withColumn('numb_share',
    when(col('price')-col('previous_price')>col('sell'),
        0).otherwise(col('numb_share')))
    #time adjustment 
    criteria=criteria.withColumn('time',
    when((col('previous_price')-col('price')>col('buy'))|((col('price')-col('previous_price')>col('sell')) ),
        col('time_new')).otherwise(col('time')))
    #previous price adjustment 
    criteria=criteria.withColumn('previous_price',
    when((col('previous_price')-col('price')>col('buy'))|((col('price')-col('previous_price')>col('sell')) ),
        col('price')).otherwise(col('previous_price')))
    criteria=criteria.drop('time_new','volume','price')
    combine(criteria,cass_data)

def load_and_get_table(keys_space_name,table_name):
    table_df = sqlContext.read\
        .format("org.apache.spark.sql.cassandra")\
        .options(table=table_name, keyspace=keys_space_name)\
        .load()
    table_df=table_df.toDF('ticker','user','buy','cash','numb_share',\
                           'previous_price','profit','sell','time','total_value')
    return table_df
    
def writeToCassandra(data,key_space_name,table_name):
    data.write\
    .format("org.apache.spark.sql.cassandra")\
    .mode('append').options(
        table=table_name, 
        keyspace=key_space_name).save()
    
if __name__=='__main__':
    conf=SparkConf().setAppName('test').set("spark.executor.memory", "6g")
    sc=SparkContext(conf=conf).getOrCreate()
    sqlContext=SQLContext(sc)
    cass_data=load_and_get_table('users','user_data')
    spark=SparkSession(sc)
    ssc=StreamingContext(sc,8)
    kafka_stream=KafkaUtils.createDirectStream(ssc,['test'],kafkaParams = {"metadata.broker.list": 'ip-10-0-0-4:9092,ip-10-0-0-5:9092,ip-10-0-0-14:9092'})
    flow=kafka_stream.map(lambda v: json.loads(v[1].decode('utf-8')))
    #for java, using following 2 lines 
#    floww=flow.map(lambda v:list( itertools.chain.from_iterable(v.values())))
#    mapped_flow=floww.map(lambda x:(int(x[0]),str(x[1]),int(x[2]),round(float(x[3]),2)))
    mapped_flow=flow.map(lambda x:(int(x[0]),str(x[1]),int(x[2]),round(float(x[3]))))
    mapped_flow.foreachRDD(looping_funct)
   
    ssc.start()
    ssc.awaitTermination()
