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
from datetime import datetime
from botocore.exceptions import NoCredentialsError, ClientError

def lambda_handler(event, context):
    try:
        # Initialize S3 client
        s3 = boto3.client("s3")
        bucket = event.get("bucket")
        image_name = event.get("key")
        if not bucket or not image_name:
            return {"statusCode": 400, "body": "Missing 'bucket' or 'key' in request"}
        
        input_folder_name = "input"
        output_folder_name = "output"
        
        # Generate timestamped output filename
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        output_image_name = f"{os.path.splitext(image_name)[0]}_nobg_{timestamp}.png"
        
        # Construct the S3 object keys
        input_key = f"{input_folder_name}/{image_name}"
        output_key = f"{output_folder_name}/{output_image_name}"
        
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

        return {
            "statusCode": 200,
            "body": {
                "message": "File processed successfully",
                "output_key": output_key,
                "file_name": output_image_name
            }
        }

    except NoCredentialsError:
        return {"statusCode": 500, "body": "AWS credentials not available"}
    except ClientError as e:
        return {"statusCode": 500, "body": f"AWS ClientError: {str(e)}"}
    except Exception as e:
        return {"statusCode": 500, "body": f"Unexpected error: {str(e)}"}
