from confluent_kafka import Consumer
import library.utils as ut
import os


#args=ut.parse_arguments()
#f=ut.readConfig("s3://fitchlab/configuration/config.json")
f=ut.readConfig(os.environ['configFileLocation']) 
print("json : ",f)

#setting the local variables
MIN_COMMIT_COUNT=int(f['Source']['minMSKCommit'])
timeout1=float(f['Source']['MSKpolling'])
BucketName=f['Target']['TargetS3bucket']
FolderName=f['Target']['TargetFolderName']
topics=f['Source']['MSKTopic']
asyncFlg=f['Source']['asynchronous']
    
conf=f['Source']['configuration']
conf['on_commit']=ut.commit_completed   





if __name__ == '__main__':
    """
    Main Lambda handler code
    executed when called by docker container
    or trigger by Lambda trigger.
    """
    
    #reading the Kafka topic based on the configuration
    consumer = Consumer(conf)
    ut.consume_loop(consumer, topics,timeout1,FolderName,MIN_COMMIT_COUNT,asyncFlg,BucketName)
