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
        raw_bucket: s3.IBucket,
        raw_kms_key: kms.IKey,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Glue Database
        glue_database = glue.CfnDatabase(
            self,
            "TestGlueDatabase",
            catalog_id=self.account,
            database_name=glue.CfnDatabase.DatabaseInputProperty(
                name="test-raw-database"
            ),
        )

        # creating the permissions for the crawler to enrich our Data Catalog
        glue_crawler_role = iam.Role(
            self,
            "raw-crawler-role",
            role_name="raw-crawler-role",
            assumed_by=iam.ServicePrincipal(service="glue.amazonaws.com"),
            managed_policies=[
                # Remember to apply the Least Privilege Principle and provide only the permissions needed to the crawler
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "AmazonS3FullAccess",
                    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                ),
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    "AWSGlueServiceRole",
                    "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole",
                ),
            ],
        )

        # Grant the Glue Crawler permissions to use the KMS key
        raw_kms_key.grant_decrypt(glue_crawler_role)

        # Grant the Glue Crawler permissions to access the S3 bucket
        raw_bucket.grant_read_write(glue_crawler_role)

        # Glue Crawler
        glue_crawler = glue.CfnCrawler(
            self,
            "raw-crawler",
            name="raw-crawler",
            database_name=glue_database.database_input.name,
            role=glue_crawler_role.role_name,
            targets={
                "s3Targets": [
                    {"path": f"s3://{raw_bucket.bucket_name}"},
                ]
            },
        )
