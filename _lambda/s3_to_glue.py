import os
import boto3


def handler(event, context):
    glue = boto3.client("glue")
    crawler_name = os.environ["GLUE_CRAWLER_NAME"]

    try:
        response = glue.start_crawler(Name=crawler_name)
        print(f"Started Glue Crawler: {response}")
    except Exception as e:
        print(f"Error starting Glue Crawler: {e}")
