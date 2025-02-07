#BGRemover

## Step1: Install the Required Libraries
````bash
mkdir -p python
cd python
pip install rembg -t .
````

## Step2: Zip the Contents:

````bash
zip -r rembg_layer.zip .
````

## Step 3: Upload the Zip File to AWS:
Use S3 for Larger Layers

If your zipped layer is larger than 50 MB, you must upload it to an S3 bucket and reference it in AWS Lambda.
AWS will then extract it when attaching it to your function.
 
````bash

aws lambda publish-layer-version --layer-name rembg_layer \
--content S3Bucket=mioot-bgremover-dev-us-west-1-sagemaker-data,S3Key=lambda/rembg_layer.zip \
--compatible-runtimes python3.13

````

## Step 4: Create EC2 :

Create ec2 and create EFS with below details

**create EFS**
````
name: BRRemover-lambda-efs-rembg 
mount path : /mnt/efs
````
**create Access point**
````
Name: BGRemove-lambda-efs-rembg-access-point
Root directory path: /

POSIX user
    User ID
    1001
    Group ID
    1001

Root directory creation permissions
    Owner user ID
    1001
    Owner group ID
    1001
    Permissions
    0755

````

## Step 4: Login to VM:
login to vm 

````bash
sudo yum install -y amazon-efs-utils
sudo mkdir /mnt/efs/lambda-packages
sudo mkdir /mnt/efs/models

sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
````
Create a Dockerfile:

Dockerfile
````bash
FROM python:3.13-slim
RUN pip install rembg
````
## Step 4: Build and Run the Container:

````bash
sudo docker build -t rembg-install .
sudo docker run --rm -v /mnt/efs/lambda-packages:/output rembg-install sh -c "cp -r /usr/local/lib/python3.13/site-packages/* /output"
cd lambda-packages
zip -r rembg_package.zip .
cd ..
cd models
sudo wget --retry-connrefused --waitretry=3 --timeout=30 --tries=5 -O u2net.onnx \
     https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx

````