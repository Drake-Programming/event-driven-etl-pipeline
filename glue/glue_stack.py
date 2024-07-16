from aws_cdk import (
    Stack,
    aws_glue as glue,
    aws_iam as iam,
    aws_s3 as s3,
    aws_kms as kms,
)
from constructs import Construct


class GlueStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        raw_s3_kms_key: kms.IKey,
        raw_s3_bucket: s3.IBucket,
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

        self.crawler_s3_role = iam.Role(
            self,
            "CrawlerS3Role",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            description="Crawler S3 Role",
            role_name="CrawlerS3Role",
        )

        # Grant the Glue Crawler permissions to use the KMS key
        raw_s3_kms_key.grant_decrypt(self.crawler_s3_role)
        # Grant the Glue Crawler permissions to access the S3 bucket
        raw_s3_bucket.grant_read(self.crawler_s3_role)

        # Glue Crawler
        self.raw_glue_crawler = glue.CfnCrawler(
            self,
            "raw-crawler",
            name="raw-crawler",
            description="Crawl the data in the test raw bucket",
            database_name=self.glue_database.database_input.name,
            role=self.crawler_s3_role.role_name,
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(
                recrawl_behavior="CRAWL_EVENT_MODE"
            ),
            targets={
                "s3Targets": [
                    {"path": f"s3://{raw_s3_bucket.bucket_name}"},
                ]
            },
        )
