import asyncio
import aiohttp
import time, logging
import json,csv
from hashlib import md5
import os
import boto3
import pandas as pd
import awswrangler as wr
import traceback

BUCKET_NAME = os.environ.get("BUCKET_NAME")
BUCKET_PREFIX = os.environ.get("BUCKET_PREFIX")

save_directory = os.path.join('/tmp', "marvel_characters.csv")

def logger_config():
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s ::%(levelname)s::%(name)s --> %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    return logger

logger = logger_config()


def upload_to_s3(df, boto_session):
    """Upload dataframe to S3"""

    if df.empty:
        logger.info("############ No new character was discovered  !!! ###########")
    else:  
        wr.s3.to_csv(
            df=df,
            path=f"s3://{BUCKET_NAME}/{BUCKET_PREFIX}",
            index=True,
            boto3_session=boto_session,
            dataset=True,
            mode="append",
        )
    logger.info("############ CSV upload successfull !!! ###########")

async def fetch_characters(async_session, public_key, private_key, timestamp, offset=0):
    """Make a request to the marvel endpoint and fetch the characters in 100s"""

    hash_str = md5(f"{timestamp}{private_key}{public_key}".encode("utf8")).hexdigest()
    url = 'http://gateway.marvel.com/v1/public/characters'
    params = {
        "apikey": public_key,
        "ts": timestamp,
        "hash": hash_str,
        "orderBy": "name",
        "limit": 100,
        "offset": offset
    }
    logger.info(f"First {offset} characters queried successfully !!!")
    async with async_session.get(url, params=params, ssl=False) as response:
        return await response.json()

async def get_all_characters(public_key, private_key):
    """Asynchronously call the fetch_characters() function to gather all the characters """

    async with aiohttp.ClientSession(trust_env=True) as async_session:
        timestamp = str(time.time())

        # Fetch the first 100 characters to know the total amount available
        response = await fetch_characters(async_session, public_key, private_key, timestamp)
        total = response['data']['total']
        characters = response['data']['results']

        # Fetch remaining characters asynchronously
        tasks = []
        for offset in range(100, total, 100):

            tasks.append(fetch_characters(async_session, public_key, private_key, timestamp, offset))

        additional_characters = await asyncio.gather(*tasks)
        for data in additional_characters:
           
            characters.extend(data['data']['results'])

        return characters

async def main(public_key, private_key, boto_session):  
    """Specifies the exact data required from the endpoint response and
    deduplicates the characters being uploaded to S3"""

    logger.info("############ Program started successfully !!! ###########")
    characters = await get_all_characters(public_key, private_key)

    logger.info("############ Writing characters to CSV  !!! ###########")
    columns = ["ID", 'NAME', 'COMIC_COUNT']
    data = [(item['id'], item['name'], item['comics']['available']) for item in characters]
    new_df = pd.DataFrame(data, columns=columns)
    try:
        existing_df = wr.s3.read_csv(
            path=f"s3://{BUCKET_NAME}/{BUCKET_PREFIX}",
            dataset=True,
            boto3_session=boto_session,
        )
        merged_df = pd.merge(new_df, existing_df, on=columns, how='left', indicator=True)
        filtered_df = merged_df[merged_df['_merge'] == 'left_only'][columns]
        upload_to_s3(filtered_df, boto_session)
        logger.info("############ Characters writen to CSV successfully  !!! ###########")
    except Exception as e:
        # print(traceback.format_exc())
        logger.info("############ No file existing in S3 !!! ###########")

        upload_to_s3(new_df, boto_session)
        logger.info("############ Characters writen to CSV successfully  !!! ###########")

    


# if __name__ == "__main__":
    # asyncio.run(main())
