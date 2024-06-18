#!/bin/bash

# AUDIENCE = os.getenv('AUDIENCE')
# SECRET_KEY = os.getenv('SECRET_KEY')
# DATA_LAYER_URL = os.getenv('PREFERENCES_DATA_LAYER_URL')
# PROJECT_ID = os.getenv('PROJECT_ID')
# CONTEXT_ROOT = os.getenv('CONTEXT_ROOT')
# REGION = os.getenv('REGION')
# K_SERVICE = os.getenv('K_SERVICE')
# DOMAIN = os.getenv('DOMAIN')

docker build -t data-svc:latest .
docker run --rm -p 8080:8080 -e PORT=8080 \
    -e PROJECT_ID=configuration-20231112 \
    -e DATASET_NAME=configuration_dataset \
    -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/google.key \
    -e CONTEXT_ROOT=user-profile-ol-svc \
    -v /Users/admin/secrets:/secrets \
      data-svc:latest
