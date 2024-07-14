#!/usr/bin/env python3
import os

import aws_cdk as cdk

from event_driven_etl_pipeline.event_driven_etl_pipeline_stack import EventDrivenEtlPipelineStack


app = cdk.App()
EventDrivenEtlPipelineStack(app, "EventDrivenEtlPipelineStack")

app.synth()
