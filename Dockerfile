#base image from AWS
FROM public.ecr.aws/lambda/python:3.9 AS base-image



# yum updates and security updates for zlib
RUN yum update -y \
  && yum install -y \
  update zlib \
  && yum clean all


#add the pandas, wrangler dependencies
COPY requirements.txt .
RUN pip3 install --user -r requirements.txt


#multistage build
FROM public.ecr.aws/lambda/python:3.9 AS base-image2
COPY --from=base-image /root/.local /root/.local

#copy all the files from the folder to the container
#COPY KafkaConsumer.py .
COPY . .
#COPY ["KafkaConsumer.py","library","./"] 

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# entry poiny
ENTRYPOINT ["python"]

#Run the command when triggered
CMD [ "KafkaConsumer.py" ]