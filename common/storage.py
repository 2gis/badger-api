import boto
import boto.s3.connection

from django.conf import settings


def get_s3_connection():
    if settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY and settings.S3_HOST:
        return boto.connect_s3(
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            host=settings.S3_HOST,
            is_secure=False,
            calling_format=boto.s3.connection.OrdinaryCallingFormat())
    return None
