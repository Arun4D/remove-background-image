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
from datetime import datetime, timezone
from botocore.exceptions import NoCredentialsError, ClientError
import re

def lambda_handler(event, context):
    try:
        # Initialize S3 client
        s3 = boto3.client("s3")
        #bucket = event.get("bucket")
        S3_BUCKET = os.environ.get("S3_BUCKET")
        image_name = event.get("file_name")
        if not image_name:
            return {"statusCode": 400, "body": "Missing 'file_name' in request"}
        
        INPUT_FOLDER_NAME = os.environ.get("INPUT_FOLDER_NAME")
        OUTPUT_FOLDER_NAME = os.environ.get("OUTPUT_FOLDER_NAME")
        
        
        # Extract the base name (e.g., "ad_test203") from the input image name
        base_name = re.sub(r'_input_.*', '', image_name)
        
        # Generate timestamped output filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")  # Use timezone.utc
        output_image_name = f"{base_name}_nobg_{timestamp}.png"
        
        # Construct the S3 object keys
        input_key = f"{INPUT_FOLDER_NAME}/{image_name}"
        output_key = f"{OUTPUT_FOLDER_NAME}/{output_image_name}"
        
        print(f"Downloading image from S3: {input_key}...")
        response = s3.get_object(Bucket=S3_BUCKET, Key=input_key)
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
            Bucket=S3_BUCKET,
            Key=output_key,
            Body=output_buffer,
            ContentType="image/png"
        )

        file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{output_key}"
        return {
            "statusCode": 200,
            "body": {
                "message": "File processed successfully",
                "file_url": file_url,
                "file_name": output_image_name
            }
        }

    except NoCredentialsError:
        return {"statusCode": 500, "body": "AWS credentials not available"}
    except ClientError as e:
        return {"statusCode": 500, "body": f"AWS ClientError: {str(e)}"}
    except Exception as e:
        return {"statusCode": 500, "body": f"Unexpected error: {str(e)}"}