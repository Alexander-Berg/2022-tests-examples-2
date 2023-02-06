import hashlib
import random
import string


async def clean_agent_request(
        mock_mark_handler, exec_time=True, take_id=False,
):
    mark_request = await mock_mark_handler.wait_call()
    mark_request_data = mark_request['request'].json

    assert mark_request_data.pop('node_id') is not None
    if exec_time:
        assert mark_request_data.pop('exec_time') is not None
    if take_id:
        assert mark_request_data.pop('take_id') is not None

    return mark_request_data


def random_name():
    return ''.join(random.choice(string.ascii_letters) for _ in range(8))


def our_hash(split_id):
    hash_str = hashlib.sha1(split_id.encode('utf-8')).hexdigest()
    return int(hash_str[0:4], 16) % 100


def send_to_cluster_from_config(percent, split_id):
    val = our_hash(split_id)
    return val < percent
