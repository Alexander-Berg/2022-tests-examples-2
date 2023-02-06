import boto3
from moto import mock_s3

from s3_json.aws import AWSClient

TEST_FILENAME = "testing-filename.json"
TEST_BYTES = b"test binary string"


@mock_s3
def test_object_save():
    conn = boto3.resource("s3", region_name=AWSClient.REGION_NAME)
    conn.create_bucket(
        Bucket=AWSClient.AWS_BUCKET_NAME,
        CreateBucketConfiguration={
            "LocationConstraint": AWSClient.REGION_NAME,
        },
    )

    client = AWSClient("random-key")
    client.push(TEST_BYTES, TEST_FILENAME)

    c_object = conn.Object(AWSClient.AWS_BUCKET_NAME, TEST_FILENAME).get()
    body = c_object["Body"].read()
    assert TEST_BYTES == body

    body = client.remove(TEST_FILENAME)
    assert TEST_FILENAME == body.get("Deleted").pop().get("Key")
