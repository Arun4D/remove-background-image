import json
import boto3
import os
import logging
import base64
from io import BytesIO
from botocore.exceptions import NoCredentialsError, ClientError
from datetime import datetime, timezone  # Import timezone explicitly

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3_client = boto3.client("s3")
S3_BUCKET = os.environ.get("S3_BUCKET")  # Get bucket name from environment variables
INPUT_FOLDER_NAME = "input"

def lambda_handler(event, context):
    try:
        # Validate request structure
        if "body" not in event or "headers" not in event or "isBase64Encoded" not in event:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid request format"})}

        # Extract headers and validate filename
        headers = event["headers"]
        if "file-name" not in headers:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing 'file-name' header"})}

        original_file_name = headers["file-name"]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")  # Use timezone.utc
        new_file_name = f"{os.path.splitext(original_file_name)[0]}_input_{timestamp}{os.path.splitext(original_file_name)[1]}"
        file_key = f"{INPUT_FOLDER_NAME}/{new_file_name}"

        # Check if the file content is Base64 encoded
        if event["isBase64Encoded"]:
            file_content = BytesIO(base64.b64decode(event["body"]))  # Convert to binary
        else:
            try:
                file_content = BytesIO(event["body"].encode("utf-8"))  # Handle plain file upload
            except Exception as e:
                logger.error(f"Failed to handle file content: {str(e)}")
                return {"statusCode": 400, "body": json.dumps({"error": "Failed to process file content"})}

        # Upload the file to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=file_key,
            Body=file_content.getvalue()
        )

        # Verify upload
        try:
            s3_client.head_object(Bucket=S3_BUCKET, Key=file_key)
            logger.info(f"File {file_key} uploaded successfully to S3")
        except ClientError as e:
            logger.error(f"Failed to verify upload in S3: {str(e)}")
            return {"statusCode": 500, "body": json.dumps({"error": "Upload verification failed"})}

        # Generate S3 file URL
        file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file_key}"

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File uploaded successfully",
                "file_url": file_url,
                "file_name": new_file_name
            })
        }

    except NoCredentialsError:
        logger.error("AWS credentials not available")
        return {"statusCode": 500, "body": json.dumps({"error": "AWS credentials not available"})}

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}