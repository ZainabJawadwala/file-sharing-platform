import os
from typing import Any, Dict
try:
    import boto3  # type: ignore
    from botocore.exceptions import ClientError  # type: ignore
    _HAVE_BOTO3 = True
except Exception:
    boto3: Any = None
    ClientError: Any = Exception
    _HAVE_BOTO3 = False


def get_s3_client() -> Any:
    if not _HAVE_BOTO3:
        raise RuntimeError("boto3 is required for S3 operations. Run: pip install -r requirements.txt")
    session = boto3.session.Session()
    return session.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )


def create_presigned_post(bucket_name: str, object_name: str, expires_in: int = 3600, acl: str = "private") -> Dict[str, Any]:
    s3_client = get_s3_client()
    try:
        response = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=object_name,
            ExpiresIn=expires_in,
            Fields={"acl": acl},
        )
    except ClientError:
        raise
    return response


def create_presigned_put_url(bucket_name: str, object_name: str, expires_in: int = 3600) -> str:
    s3_client = get_s3_client()
    try:
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expires_in,
        )
    except ClientError:
        raise
    return url
