import os
import pandas as pd
import awswrangler as wr
from confluent_kafka import Consumer
import boto3
import json
import argparse,sys

def parse_arguments():
    """
    Function to capture the argument when executing
        topic- Name of the topic
        client- if there an client name
        -c count msgs
    
    """
    parser = argparse.ArgumentParser(description='Generate simulated NetFlow streams')
    parser.add_argument('--config-location', dest='location', action='store',
                        default=None, help='configuration file location', required=True)
    
    return parser.parse_args()

def parseS3Location(s3Location):
    """
    Parse S3 location and return
    folderName and Value
    """
    
    #s3Location = 's3://bucket_name/folder1/folder2/file1.json'
    path=s3Location.replace("s3://","").split("/")
    
    folderName=path[0]
    folder="/".join(path[1:])
    
    return folderName, folder

def readConfig(location):
    """
    Read Configuration file location
    """
    s3 = boto3.client('s3')
    bucket,key=parseS3Location(location)
    obj = s3.get_object(Bucket=bucket, Key=key)

    return json.loads(obj['Body'].read())

def write_to_S3(msgstr,msg,BucketName,FolderName):
    """
    """
    # Method 2: Client.put_object()
    client = boto3.client('s3')
    if msg is not None:
        keyv=str(FolderName)+'_'+str(msg.offset())+'_'+str(msg.partition())+'.txt'
        client.put_object(Body=msgstr, Bucket=BucketName, Key=keyv)


def consume_loop(consumer,topics,timeout,FolderName,MIN_COMMIT_COUNT,asyncFlg,BucketName):
    """
    Kafka Consumer  function
    """
    

    try:
        consumer.subscribe(topics)

        msg_count = 0

        while True:
            print(" Running the while loop")
            msg = consumer.poll(timeout=timeout)
            print("Message :  ",msg)

            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                print("String value of the message    :    ",msg.value().decode('utf-8'))
                print("Metadata of the message  ",(msg.topic(), msg.partition(), msg.offset()))
                msgstr=str(msg.value().decode('utf-8'))+','+str(msg.topic())+','+str(msg.partition())+','+str(msg.offset())
                write_to_S3(msgstr,msg,BucketName,FolderName)
                msg_count += 1
                if msg_count % MIN_COMMIT_COUNT == 0:
                    consumer.commit(asynchronous=asyncFlg)
    finally:
         # Close down consumer to commit final offsets.
         consumer.close()



def commit_completed(err, partitions):
    if err:
        print(str(err))
    else:
        print("Committed partition offsets: " + str(partitions))