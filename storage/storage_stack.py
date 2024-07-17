from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    Duration,
    aws_kms as kms,
    Fn,
    aws_sqs as sqs,
    aws_glue as glue,
    aws_iam as iam, RemovalPolicy,
)
from constructs import Construct


class StorageStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #  Make KMS key for raw S3 bucket
        self.raw_bucket_kms_key = kms.Key(
            self,
            "RawBucketKey",
            enable_key_rotation=True,
            rotation_period=Duration.days(90),
        )
        self.raw_bucket_kms_key.add_alias("alias/test-s3-raw-encryption")

        #  Make KMS key for SQS Glue Crawler Queue
        self.sqs_crawler_kms_key = kms.Key(
            self,
            "SQSCrawlerKey",
            enable_key_rotation=True,
            rotation_period=Duration.days(90),
        )
        self.sqs_crawler_kms_key.add_alias("alias/test-sqs-crawler-encryption")

        #  Make suffix for S3 buckets
        suffix = self.__initialize_suffix()

        # S3 Raw Bucket
        self.raw_bucket = s3.Bucket(
            self,
            "RawBucket",
            bucket_name=f"test-raw-{suffix}",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            encryption_key=self.raw_bucket_kms_key,
            removal_policy=RemovalPolicy.DESTROY,
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30),
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER_INSTANT_RETRIEVAL,
                            transition_after=Duration.days(90),
                        ),
                    ]
                )
            ],
        )

        self.crawler_dlq = sqs.Queue(
            self,
            "CrawlerDLQ",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=self.sqs_crawler_kms_key,
            enforce_ssl=True,
            queue_name="CrawlerDLQ",
            retention_period=Duration.days(14),
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.crawler_queue = sqs.Queue(
            self,
            "CrawlerQueue",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=self.sqs_crawler_kms_key,
            enforce_ssl=True,
            queue_name="CrawlerQueue",
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=5,
                queue=self.crawler_dlq,
            ),
            retention_period=Duration.days(14),
            removal_policy=RemovalPolicy.DESTROY
        )

        self.raw_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED_PUT, s3_notifications.SqsDestination(self.crawler_queue)
        )

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
        self.raw_bucket.grant_read(self.raw_crawler_role)

        #  Grant Glue Crawler permission to consume messages from SQS queue
        self.crawler_queue.grant_consume_messages(self.raw_crawler_role)
        self.crawler_queue.grant_purge(self.raw_crawler_role)
        self.raw_crawler_role.add_to_policy(
            iam.PolicyStatement(
                actions=["sqs:SetQueueAttributes"],
                resources=[self.crawler_queue.queue_arn],
                effect=iam.Effect.ALLOW
            )
        )

        self.sqs_crawler_kms_key.grant_decrypt(self.raw_crawler_role)

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
                        event_queue_arn=self.crawler_queue.queue_arn,
                        path=f"s3://{self.raw_bucket.bucket_name}",
                    )
                ]
            },
        )

    def __initialize_suffix(self):
        short_stack_id = Fn.select(2, Fn.split("/", self.stack_id))
        suffix = Fn.select(4, Fn.split("-", short_stack_id))
        return suffix
