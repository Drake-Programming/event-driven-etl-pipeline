from aws_cdk import Stack, aws_s3 as s3, Duration, aws_kms as kms, Fn
from constructs import Construct


class StorageStack(Stack):

    def __init__(
        self, scope: Construct, construct_id: str, raw_s3_kms_key: kms.IKey, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
            encryption_key=raw_s3_kms_key,
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

    def __initialize_suffix(self):
        short_stack_id = Fn.select(2, Fn.split("/", self.stack_id))
        suffix = Fn.select(4, Fn.split("-", short_stack_id))
        return suffix
