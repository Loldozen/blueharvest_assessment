import os
import json
import asyncio
import base64
import boto3
from botocore.exceptions import ClientError
from utils.get_marvel_characters import main

SECRET_NAME = os.environ.get('SECRET_NAME')
REGION_NAME = os.environ.get('REGION_NAME')


def lambda_handler(event, context):

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=REGION_NAME
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=SECRET_NAME
        )
    except ClientError as e:
        raise e
    if 'SecretString' in get_secret_value_response:
        secret = json.loads( get_secret_value_response['SecretString'])
    else:
        secret = base64.b64decode(get_secret_value_response['SecretBinary'])
    public = secret['MARVEL_PUBLIC_KEY']
    private = secret['MARVEL_PRIVATE_KEY']


    asyncio.run(main(public, private, session))

    response = {
        "status": "success",
        "message": "File uploaded to s3 successfully!!!",
    }

    return response
