import json
import boto3
import os
from botocore.exceptions import NoCredentialsError

# Initialize S3 client
s3_client = boto3.client('s3')
S3_BUCKET = os.environ['S3_BUCKET']  # Get bucket name from environment variables
output_folder_name = "output"

def lambda_handler(event, context):
    try:
        # Get the file name from the query parameters
        file_name = event['queryStringParameters']['file_name']
        key = f'{output_folder_name}/{file_name}'

        # Generate a pre-signed URL for the file
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': key},
            ExpiresIn=3600  # URL expires in 1 hour
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'file_url': presigned_url
            })
        }
    except NoCredentialsError:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'AWS credentials not available'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }