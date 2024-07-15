#!/usr/bin/env python3
import os

import aws_cdk as cdk

from compute_stack.compute_stack import ComputeStack
from storage_stack.storage_stack import StorageStack
from integration_stack.integration_stack import IntegrationStack
from glue_stack.glue_stack import GlueStack


app = cdk.App()

#  init storage stack
storage_stack = StorageStack(app, "StorageStack")

#  init compute stack
compute_stack = ComputeStack(
    app,
    "ComputeStack",
    raw_s3_bucket=storage_stack.raw_bucket,
    raw_s3_kms_key=storage_stack.raw_bucket_kms_key,
)

glue_stack = GlueStack(
    app,
    "IntegrationStack",
    raw_s3_bucket=storage_stack.raw_bucket,
    raw_s3_kms_key=storage_stack.raw_bucket_kms_key,
)

#  init integration stack
integration_stack = IntegrationStack(
    app,
    "IntegrationStack",
)

app.synth()
