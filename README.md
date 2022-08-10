<h1><p><u>Contents</u></p></h1>


### Introduction
The **Kafka Streaming Framework** (KSF) is built on Amazon ECS and Docker using libraries like AWS wrangler, Pandas, and BOTO3. The framework's technical stack includes AWS MSK Kafka, Docker, Amazon ECS, and Amazon S3. The docker container is hosted on an Amazon ECS cluster, constantly polling the data from a Kafka topic. Apply some data validation or processing logic to the streamed data before loading it into any AWS Target resource, such as Amazon S3. The Kafka consumer is built using the Confluent-Kafka python library, and it is highly configurable and scalable. The data processing is built using Python frameworks, and AWS Wrangler is used to load the data into an AWS target.

###<p><u> **Release 1**:</u></p>
The KSF is capable of polling Kafka topics synchronously and asynchronously, offset error handling, driven by a JSON configuration file, and writing to AWS S3. JSON and CSV are data formats that are supported. image with Pandas, AWS wrangler, and Confluent Kafka. secure Docker image with all security patches. For now, the AWS ECR sync, setup ECS tasks, and data processing logic will be manual.
####  DockerFile 
<p>The DockerFile builds the image using AWS based image for python3.9. During the build process, it copies requirements.txt, 
KafkaConsumer.py and utils.py.</p>

#### KafkaConsumer.py 
<p>Python code to read the Kafka topic, process the data and write it to the Amazon S3 location.  This piece of code can be updated to add data processing logic.</p>

#### utils.py
<p>Python utility library that contains all the functions to read, process and kafka code. This library will be extended to handle all the sources and targets.<br>
**Note**: For this library, consider Factory and Adapter design patterns for future releases.

### <p><u>VPC, Roles and Execution</p></u>
<p>In this framework, the MSK Kafka and ECS Cluster are hosted on the same VPC for code sample purposes only. The MSK cluster is hosted on a private subnet of the VPC, and a NAT gateway is used to communicate with the public subnet and the internet. The security groups are used to provide least privilege access to the MSK cluster by providing the SG from the ECS container and inbound rules for the corresponding port, like 9000 only. The MSK cluster and ECS can be in different VPCs to handle segmentation and network security. VPC peering or the AWS Transit gateway can be used to enable communication between VPCs. The AmazonECSTaskExecutionRolePolicy is the execution role for EC2 Docker containers under ECS, and for Amazon S3 access, attached actions like Amazon s3: Get*, s3: List*, and s3: PutObject access are available along with the resource name.  </p>


#### <p><u>High level steps to build Amazon ECS task from local Docker image</u></p>


1. Create a docker file with Python 3.9 and the AWS base image.the requirement.txt file with all the required libraries for the data processing logic. Keep in mind that the data processing library is heavy and will increase the image size. The main data processing logic is added to the folder as lambda_code.py. The Dockerfile has the entrypoint and command to execute the script when triggered.
2. Locally create a Docker image and container. Use AWS cloud9 or AWS workspace or local PC for this step
3. Create an Amazon ECR Repository and push the container to repository
4. Create an Amazon ECS task definition and create task
5. Run the ECS task


### Build, test, and deploy containers to the AWS ECR repository.

Building a docker and pushing the image to the Amazon ECR registry.

Browse to the Docker folder with all the required files. Build the Docker image locally by executing the Dockerfile locally.

#Browse to the local folder
```
docker build -t Data-processing-ecs.
```

### Run the docker 

#Authenticate the docker CLI with AWS ECR

```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com</code>
```

### Create the AWS ECR repository using command line

```
aws ecr create-repository --repository-name data-processing-ecs --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
```

#Tag the image and push it to AWS ECR repo


```
docker tag  Data-processing-ecs:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/data-processing-ecs:latest</code> 
```
###  AWS ECR push to repository

```
docker push -accountnumber-.dkr.ecr.us-east-1.amazonaws.com/data-processing-ecs:latest</code>
```


#### Required Permission pushing image in AWS ECR
Before pushing the Docker image to the repository, ensure that the IAM role permission must allow you to list, view, and push or pull images from only one AWS ECR repository in your AWS account. Below is a custom policy.
<em>**Note** : Access is limited to one repository on the AWS ECR. The policy key resource tag has the name of the repository of choice.</em>
e.g.
```{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Sid":"ListImagesInRepository",
         "Effect":"Allow",
         "Action":[
            "ecr:ListImages"
         ],
         "Resource":"arn:aws:ecr:us-east-1:123456789012:repository/my-repo"
      },
      {
         "Sid":"GetAuthorizationToken",
         "Effect":"Allow",
         "Action":[
            "ecr:GetAuthorizationToken"
         ],
         "Resource":"*"
      },
      {
         "Sid":"ManageRepositoryContents",
         "Effect":"Allow",
         "Action":[
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetRepositoryPolicy",
                "ecr:DescribeRepositories",
                "ecr:ListImages",
                "ecr:DescribeImages",
                "ecr:BatchGetImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
         ],
         "Resource":"arn:aws:ecr:us-east-1:123456789012:repository/<repository_name> or data-processing-ecs"
      }
   ]
}
```

### <p><u>Amazon ECS task creation</u></p>
Fill in the task name and the environment variable information.  The Environment variable can be the configuration file location
e.g. configFileLocation

Next select the EC2 instance for the app environment, adjust the hardware configuration , network mode(bridge), task role IAM and enable logging in AWS Cloudwatch. Then click next.
Once the task definition is complete, go to cluster page and task tab under the cluster. Select the ec2 compute option and then select the Application type, Service- long running or continuous task 
Task- transient/batch tasks.

Please select task application type for a batch job.

#### Required Permission for creating Amazon ECS task

To create the ecsInstanceRole, choose Roles and then AWS service Elastic container service. Pick the EC2 role for elastic container service
Attach the permission AmazonEC2ContainerServiceforEC2Role managed policy and add the below trust policy if it not already there.

```
#### Trust policy
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

#### Amazon S3 read only access

The JSON configuration file is stored in Amazon S3 and used as an input. The ECS role requires read-only access to Amazon S3.


### <p><u>Sample Config file</u></p>

The config file drives the ECS task. It is typically stored in an Amazon S3 location and referenced by the Amazon ECS task. When an Amazon ECS task executes, the location of configuration files is passed to the ECS task as an environment variable.
The configuration file below reads the kafka topic and writes the data to the Amazon s3 location in JSON format.
e.g.

```{"Source":{
		"minMSKCommit":"10",
		"MSKpolling":"1.0",
		"MSKTopic":["topicname"],
		"SourceDataFormat":"JSON",
		"asynchronous":false,
		"configuration" :{"bootstrap.servers": "",
							"group.id": "foo",
							"enable.auto.commit": false,
							"auto.offset.reset": "latest",
							"batch.num.messages":"100"}
		},
		
"Target":{
		"TargetS3bucket":"bucketname",
		"TargetFolderName":"curated/",
		"TargetDataFormat": "JSON"
		}
		
}
```

###  <p><u>Amazon ECS task execution</u></p>

In order to execute the Amazon ECS task, the IAM would require the execution role for the ECS task.

#### Required Permission
The task execution role grants the Amazon ECS container and Fargate agents permission to make AWS API calls on your behalf. Under the IAM role, Look for the ecsTaskExecutionRole. If the role does not exist, create a role and attach the following policy called AmazonECSTaskExecutionRolePolicy. Based on your use case, you can have an inline custom policy (if required).

```commandline
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```
Check if the trust policy has the below configuration

```commandline
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```