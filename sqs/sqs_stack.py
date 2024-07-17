from aws_cdk import Stack, aws_kms as kms, aws_sqs as sqs, Duration
from constructs import Construct


class SqsStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #  Make KMS key for SQS Glue Crawler Queue
        self.sqs_crawler_kms_key = kms.Key(
            self,
            "SQSCrawlerKey",
            enable_key_rotation=True,
            rotation_period=Duration.days(90),
        )
        self.sqs_crawler_kms_key.add_alias("alias/test-sqs-crawler-encryption")

        self.crawler_dlq = sqs.Queue(
            self,
            "CrawlerDLQ",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=self.sqs_crawler_kms_key,
            enforce_ssl=True,
            fifo=True,
            queue_name="CrawlerDLQ.fifo",
            retention_period=Duration.days(14),
        )

        self.crawler_queue = sqs.Queue(
            self,
            "CrawlerQueue",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=self.sqs_crawler_kms_key,
            enforce_ssl=True,
            fifo=True,
            queue_name="CrawlerQueue.fifo",
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=5,
                queue=self.crawler_dlq,
            ),
            retention_period=Duration.days(14),
        )
