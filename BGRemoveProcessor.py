import sys
sys.path.append("/mnt/efs/lambda-packages")  # Add EFS path

import os
os.environ['NUMBA_CACHE_DIR'] = '/tmp'
os.environ['NUMBA_NUM_THREADS'] = '1'
os.environ['NUMBA_DISABLE_JIT'] = '1'
os.environ['U2NET_HOME'] = '/mnt/efs/models'

from rembg import remove
from PIL import Image
import io
import boto3

def lambda_handler(event, context):
    # Read image from S3
    s3 = boto3.client("s3")
    bucket = event["bucket"]
    image_name = event["key"]
    input_folder_name = "input"
    output_folder_name = "output"
        
    # Construct the S3 object key
    input_key = f"{input_folder_name}/{image_name}"
    output_key = f"{output_folder_name}/{image_name}"
    
    print(f"Downloading image from S3: {input_key}...")
    response = s3.get_object(Bucket=bucket, Key=input_key)
    input_image = Image.open(io.BytesIO(response["Body"].read()))

    # Remove background
    print("Removing background...")
    output_image = remove(input_image)

    # Save processed image to S3
    output_buffer = io.BytesIO()
    output_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)

    print("Uploading processed image to S3")
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=output_buffer,
        ContentType="image/png"
    )

    return {"status": "success", "output_key":output_key}
