from aws_cdk import Stack, aws_s3 as s3, aws_iam as iam, Duration, aws_kms as kms
from constructs import Construct


class StorageStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #  Make suffix for S3 buckets
        suffix = self.__initialize_suffix()

        #  Make KMS key for raw S3 bucket
        self.raw_bucket_kms_key = kms.Key(
            self,
            "RawBucketKey",
            enable_key_rotation=True,
            rotation_period=Duration.days(90),
        )
        self.raw_bucket_kms_key.add_alias("alias/test-s3-raw-encryption")

        # S3 Raw Bucket
        self.raw_bucket = s3.Bucket(
            self,
            "RawBucket",
            bucket_name=f"test-raw-{suffix}",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            encryption_key=self.raw_bucket_kms_key,
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
