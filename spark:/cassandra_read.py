
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pyspark import SparkContext
from pyspark.sql import SQLContext 

def write_to_cassandra(data,key_space_name,table_name):
    data.write.format("org.apache.spark.sql.cassandra")\
    .mode('append').options(
        table=table_name, 
        keyspace=key_space_name,).save()
    
def load_and_get_table(keys_space_name,table_name):
    table_df = sqlContext.read\
        .format("org.apache.spark.sql.cassandra")\
        .options(table=table_name, keyspace=keys_space_name)\
        .load()
    return table_df

if __name__=='__main__':
    sc=SparkContext('local')
    sqlContext=SQLContext(sc)
    data=load_and_get_table('users','user_data')
    data.show()

