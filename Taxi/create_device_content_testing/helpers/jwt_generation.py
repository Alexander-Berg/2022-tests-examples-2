# pylint: skip-file
# flake8: noqa
import base64
import collections
import hashlib
import json

import ecdsa

from helpers.config import read_private_key

JWT_HEADER = {'alg': 'ES256', 'typ': 'JWT'}


def _encode_query_binary(query):
    def _to_bytes(value):
        if isinstance(value, bytes):
            return value
        return str(value).encode()

    if not query:
        return b''

    return b'?' + b'&'.join(
        b'='.join(
            base64.urlsafe_b64encode(_to_bytes(part)).rstrip(b'=')
            for part in pair
        )
        for pair in collections.OrderedDict(sorted(query.items())).items()
    )


def _jwt_payload(query_hash, body_hash):
    return {'query_hash': query_hash, 'body_hash': body_hash}


def _url64_encode_stripped(bin_string):
    # "=" padding is omitted as per RFC7515 section 2
    return base64.urlsafe_b64encode(bin_string).rstrip(b'=')


def generate_jwt(endpoint, query_params, body, is_body_json=True):
    endpoint = endpoint.lstrip('/')
    private_key = ecdsa.SigningKey.from_pem(
        read_private_key(), hashfunc=hashlib.sha256,
    )
    query_encoded = endpoint.encode('utf-8') + _encode_query_binary(
        query_params,
    )
    if is_body_json:
        body = json.dumps(body).encode('utf-8')
    header = json.dumps(JWT_HEADER)
    query_hash = hashlib.sha256(query_encoded).hexdigest()
    body_hash = hashlib.sha256(body).hexdigest()
    payload = json.dumps(_jwt_payload(query_hash, body_hash))
    data_to_sign = (
        _url64_encode_stripped(header.encode('utf-8'))
        + b'.'
        + _url64_encode_stripped(payload.encode('utf-8'))
    )
    signature = _url64_encode_stripped(private_key.sign(data_to_sign))
    token = data_to_sign + b'.' + signature
    return token.decode('utf-8')
