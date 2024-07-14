#!/usr/bin/env python3
import os

import aws_cdk as cdk

from compute_stack.compute_stack import ComputeStack
from storage_stack.storage_stack import StorageStack
from integration_stack.integration_stack import IntegrationStack


app = cdk.App()

ComputeStack(app, "ComputeStack")
StorageStack(app, "StorageStack")
IntegrationStack(app, "IntegrationStack")

app.synth()
