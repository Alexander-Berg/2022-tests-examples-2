import os


def test_list_buckets(s3_client):
    buckets = s3_client.list_buckets()
    assert buckets['Buckets'][0]['Name'] == 'test-bucket'

    global AWS_DATA_PATH
    AWS_DATA_PATH = os.environ.get('AWS_DATA_PATH')
    assert AWS_DATA_PATH is not None


def test_tmp_clean():
    global AWS_DATA_PATH
    assert not os.path.exists(AWS_DATA_PATH)
