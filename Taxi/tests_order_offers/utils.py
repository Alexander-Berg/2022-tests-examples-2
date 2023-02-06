import gzip
import io
import uuid

import bson

# Map 0x24 to zero
SHARD_ID_FLIP = 0x24


def gzip_data(source):
    data = io.BytesIO()

    with gzip.GzipFile(mode='wb', fileobj=data) as gzip_file:
        gzip_file.write(bytes(source))

    return data.getvalue()


async def make_request(service, path, data, compress=False):
    request_data = bson.BSON.encode(data) if isinstance(data, dict) else data

    headers = {'content-type': 'application/bson'}

    if compress:
        request_data = gzip_data(request_data)
        headers['content-encoding'] = 'gzip'

    return await service.post(path, headers=headers, data=request_data)


async def make_save_request(service, *args, **kwargs):
    return await make_request(service, '/v1/save-offer', *args, **kwargs)


async def make_match_request(service, *args, **kwargs):
    return await make_request(service, '/v1/match-offer', *args, **kwargs)


def get_shard_id(obj_id, log_extra=None):
    try:
        obj_uuid = uuid.UUID(obj_id)
    except (ValueError, AttributeError):
        return 0
    return (
        ((obj_uuid.int >> 76) & 0xF) | ((obj_uuid.int >> 58) & 0x30)
    ) ^ SHARD_ID_FLIP
