from aws_cdk import (
    Stack,
    aws_glue as glue,
    aws_iam as iam,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_kms as kms,
)
from constructs import Construct


class GlueStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        raw_s3_bucket: s3.IBucket,
        crawler_queue: sqs.Queue,
        queue_key: kms.IKey,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Glue Database
        self.glue_database = glue.CfnDatabase(
            self,
            "TestGlueDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name="test-raw-database"
            ),
        )
        # Crawler Role
        self.raw_crawler_role = iam.Role(
            self,
            "RawCrawlerRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            description="Raw Bucket Crawler Role",
            role_name="RawCrawlerRole",
        )

        # Grant the Glue Crawler permissions to access the S3 bucket
        raw_s3_bucket.grant_read(self.raw_crawler_role)

        #  Grant Glue Crawler permission to consume messages from SQS queue
        crawler_queue.grant_consume_messages(self.raw_crawler_role)

        queue_key.grant_decrypt(self.raw_crawler_role)

        # Glue Crawler
        self.raw_glue_crawler = glue.CfnCrawler(
            self,
            "RawBucketCrawler",
            name="RawBucketCrawler",
            description="Crawl the data in the test raw bucket",
            database_name=self.glue_database.database_input.name,
            role=self.raw_crawler_role.role_name,
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(
                recrawl_behavior="CRAWL_EVENT_MODE"
            ),
            targets={
                "s3Targets": [
                    glue.CfnCrawler.S3TargetProperty(
                        event_queue_arn=crawler_queue.queue_arn,
                        path=f"s3://{raw_s3_bucket.bucket_name}",
                    )
                ]
            },
        )
