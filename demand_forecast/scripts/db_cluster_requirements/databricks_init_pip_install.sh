#!/bin/bash

REQUIREMENTS_S3_PATH="s3://gygdata/data-products/sdp/rubtsovenko/demand_forecast/requirements/db_cluster_requirements.txt"
REQUIREMENTS_LOCAL_PATH="/tmp/requirements.txt"

aws s3 cp "$REQUIREMENTS_S3_PATH" "$REQUIREMENTS_LOCAL_PATH"

pip install -r "$REQUIREMENTS_LOCAL_PATH"
