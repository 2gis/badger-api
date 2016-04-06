import boto
import boto.s3.connection

from django.conf import settings

import logging
log = logging.getLogger(__name__)


def get_s3_connection():

    if settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY and settings.S3_HOST:
        log.debug('Connecting to {}, with secure connection is {}'.
                  format(settings.S3_HOST, settings.S3_SECURE_CONNECTION))
        return boto.connect_s3(
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            host=settings.S3_HOST,
            is_secure=settings.S3_SECURE_CONNECTION,
            calling_format=boto.s3.connection.OrdinaryCallingFormat())
    return None


def get_or_create_bucket(s3_connection):
    bucket = s3_connection.get_bucket(settings.S3_BUCKET_NAME)
    if bucket is None:
        bucket = s3_connection.create_bucket(settings.S3_BUCKET_NAME)
    return bucket
