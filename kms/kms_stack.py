from aws_cdk import Stack, aws_s3 as s3, aws_s3_notifications as s3_notifications, aws_sqs as sqs
from constructs import Construct


class KmsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, raw_s3_bucket: s3.IBucket, crawler_queue: sqs.Queue, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add Test notification configuration to send events to SQS queue
        raw_s3_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED_PUT, s3_notifications.SqsDestination(crawler_queue)
        )
