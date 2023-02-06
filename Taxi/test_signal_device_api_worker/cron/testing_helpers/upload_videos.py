# This script is used to upload some videos for concatenation in testing
# to check how cron job works
import base64
import collections
import hashlib
import json
import random
import string

import ecdsa
import requests


#  upload parameters
DEVICE_ID = '4f1faadcf0c642de9907a781e6993e0d'
TIMESTAMP = '2020-03-04T16:10:12Z'
TOTAL_FILES_NUMBER = 20
FILE = {'total_size': 6000, 'parts': [b'a' * 1000, b'b' * 2000, b'c' * 3000]}
FILES = [FILE for i in range(TOTAL_FILES_NUMBER)]

PUBLIC_KEY = (
    b'-----BEGIN PUBLIC KEY-----\n'
    b'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEmYB6e5eBFtRajXxCsIDm6AXoL/xN\n'
    b'zLsG2LMul+PWC+fPMA5QnUMpBdk/BsUdqabRzkKkbxO2aXxxwY3xGoC2iw==\n'
    b'-----END PUBLIC KEY-----\n'
)
PRIVATE_KEY = (
    b'-----BEGIN EC PRIVATE KEY-----\n'
    b'MHcCAQEEIKvbS5XZcGltFUyStKMlP3gkNkemQH0jIUq+wjVodY1coAoGCCqGSM49\n'
    b'AwEHoUQDQgAEmYB6e5eBFtRajXxCsIDm6AXoL/xNzLsG2LMul+PWC+fPMA5QnUMp\n'
    b'Bdk/BsUdqabRzkKkbxO2aXxxwY3xGoC2iw==\n'
    b'-----END EC PRIVATE KEY-----\n'
)


BASE_URL = 'http://signal-device-api.taxi.tst.yandex.net'
METADATA_ENDPOINT = 'v1/videos/metadata'
UPLOAD_ENDPOINT = 'v1/videos/upload'

JWT_HEADER = """{
  "alg": "ES256",
  "typ": "JWT"
}"""
JWT_QUERY_HASH_KEY = 'query_hash'
JWT_BODY_HASH_KEY = 'body_hash'
JWT_HEADER_NAME = 'X-JWT-Signature'


def str_to_bytes(str_):
    return bytes(str_, 'utf-8')


def bytes_to_str(bytes_):
    return str(bytes_)[2:-1].replace('\\n', '\n')


def random_string(string_length=12):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(string_length))


def encode_query(query):
    def _tobytes(value):
        if isinstance(value, bytes):
            return value
        return str(value).encode()

    if not query:
        return b''

    return b'?' + b'&'.join(
        b'='.join(
            base64.urlsafe_b64encode(_tobytes(part)).rstrip(b'=')
            for part in pair
        )
        for pair in collections.OrderedDict(sorted(query.items())).items()
    )


def generate_jwt(endpoint, query_params, body, is_body_json=True):
    private_key = ecdsa.SigningKey.from_pem(
        PRIVATE_KEY, hashfunc=hashlib.sha256,
    )
    query_encoded = str_to_bytes(endpoint) + encode_query(query_params)
    if is_body_json:
        body = str_to_bytes(json.dumps(body))
    payload = {
        JWT_QUERY_HASH_KEY: hashlib.sha256(query_encoded).hexdigest(),
        JWT_BODY_HASH_KEY: hashlib.sha256(body).hexdigest(),
    }
    # '=' padding is omitted as per RFC7515 section 2
    data_to_sign = (
        base64.urlsafe_b64encode(str_to_bytes(JWT_HEADER)).rstrip(b'=')
        + b'.'
        + base64.urlsafe_b64encode(str_to_bytes(json.dumps(payload))).rstrip(
            b'=',
        )
    )
    signature = base64.urlsafe_b64encode(
        private_key.sign(data_to_sign),
    ).rstrip(b'=')
    token = data_to_sign + str_to_bytes('.') + signature
    return bytes_to_str(token)


def create_metadata_params(size_bytes, file_id):
    url = BASE_URL + '/' + METADATA_ENDPOINT
    payload = {
        'device_id': DEVICE_ID,
        'timestamp': TIMESTAMP,
        'size_bytes': size_bytes,
        'file_id': file_id,
        'started_at': TIMESTAMP,
        'finished_at': TIMESTAMP,
    }
    jwt = generate_jwt(METADATA_ENDPOINT, {}, payload, True)
    headers = {'Content-Type': 'application/json', 'X-JWT-Signature': f'{jwt}'}
    return {
        'method': 'POST',
        'url': url,
        'headers': headers,
        'payload': json.dumps(payload),
    }


def create_upload_params(size_bytes, file_id, offset_bytes, payload):
    query_params = {
        'device_id': DEVICE_ID,
        'timestamp': TIMESTAMP,
        'size_bytes': str(size_bytes),
        'file_id': file_id,
        'offset_bytes': str(offset_bytes),
    }
    query_str = '?' + '&'.join(
        '='.join(part for part in pair)
        for pair in collections.OrderedDict(
            sorted(query_params.items()),
        ).items()
    )
    url = BASE_URL + '/' + UPLOAD_ENDPOINT + query_str
    jwt = generate_jwt(UPLOAD_ENDPOINT, query_params, payload, False)
    headers = {
        'Content-Type': 'application/octet-stream',
        'X-JWT-Signature': f'{jwt}',
    }
    return {
        'method': 'PUT',
        'url': url,
        'headers': headers,
        'payload': payload,
    }


def post_metadata(file_id, total_size):
    metadata_request = create_metadata_params(total_size, file_id)
    print(
        'REQUEST: '
        + str(metadata_request['method'])
        + ' '
        + str(metadata_request['url'])
        + ' '
        + str(metadata_request['headers'])
        + ' '
        + str(metadata_request['payload']),
    )
    response = requests.request(
        metadata_request['method'],
        metadata_request['url'],
        headers=metadata_request['headers'],
        data=metadata_request['payload'],
    )
    print('RESPONSE: ' + response.text)


def upload_data(file_id, data, offset):
    upload_request = create_upload_params(len(data), file_id, offset, data)
    print(
        'REQUEST: '
        + str(upload_request['method'])
        + ' '
        + str(upload_request['url'])
        + ' '
        + str(upload_request['headers']),
    )
    response = requests.request(
        upload_request['method'],
        upload_request['url'],
        headers=upload_request['headers'],
        data=upload_request['payload'],
    )
    print('RESPONSE: ' + response.text)


def run():
    for file in FILES:
        file_id = random_string()
        post_metadata(file_id, file['total_size'])
        current_offset = 0
        for part in file['parts']:
            upload_data(file_id, part, current_offset)
            current_offset += len(part)
    print('done!')


if __name__ == '__main__':
    run()
