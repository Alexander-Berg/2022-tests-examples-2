import base64
import datetime
import hashlib
import hmac
import json

import pytest


NOW_DATETIME = datetime.datetime(
    2020, 1, 1, 12, 00, 00, tzinfo=datetime.timezone.utc,
)

# pylint: disable=C0103
pytestmark = [pytest.mark.now(NOW_DATETIME.isoformat())]


def hole(revision, seconds_ago):
    timestamp = int(NOW_DATETIME.timestamp()) - seconds_ago
    return {'id': revision, 'timestamp': timestamp}


async def make_request(taxi_virtual_tariffs, last_revision, holes):
    cursor_payload = _build_cursor_dict(last_revision, holes)
    cursor = _to_jwt_token(cursor_payload, b'secret')
    response = await taxi_virtual_tariffs.get(
        f'/v1/special-requirements/updates?cursor={cursor.decode()}',
    )
    assert response.status_code == 200
    resp = response.json()
    resp['cursor'] = _get_jwt_payload(resp['cursor'])
    return resp


def _get_jwt_payload(jwt_token):
    payload_part = jwt_token.split('.')[1].encode()
    payload_part += b'=' * (-len(payload_part) % 4)
    return json.loads(base64.b64decode(payload_part))


def _base64_encode(data):
    binary = json.dumps(data, separators=(',', ':')).encode()
    return base64.urlsafe_b64encode(binary).rstrip(b'=')


def _load_cursor(cursor):
    payload_part = cursor.split('.')[1].encode()
    payload_part += b'=' * (-len(payload_part) % 4)
    return json.loads(base64.b64decode(payload_part))


def _build_cursor(last_revision, holes):
    payload = _build_cursor_dict(last_revision, holes)
    return _to_jwt_token(payload, b'secret').decode()


def _build_cursor_dict(last_revision, holes):
    return {'version': 1, 'last_revision_id': last_revision, 'holes': holes}


def _to_jwt_token(payload, key):
    header = {'alg': 'HS512', 'typ': 'JWT'}
    signing_input = b'.'.join(
        [_base64_encode(header), _base64_encode(payload)],
    )
    signature = hmac.new(key, signing_input, hashlib.sha512).digest()
    return b'.'.join(
        [signing_input, base64.urlsafe_b64encode(signature).rstrip(b'=')],
    )


async def test_without_cursor(taxi_virtual_tariffs):
    response = await taxi_virtual_tariffs.get(
        '/v1/special-requirements/updates',
    )
    assert response.status_code == 200
    response = response.json()
    response['cursor'] = _load_cursor(response['cursor'])
    assert response == {
        'special_requirements': [
            # revision: 1
            {'id': 'empty', 'requirements': []},
            # revision: 20
            {
                'id': 'food_delivery',
                'requirements': [
                    {
                        'field': 'tags',
                        'operation': 'contains',
                        'arguments': [{'value': 'food_box'}],
                    },
                    {
                        'field': 'rating',
                        'operation': 'over',
                        'arguments': [{'value': '4.95'}],
                    },
                ],
            },
            # revision: 22
            {'id': 'good_driver', 'requirements': []},
        ],
        'cursor': _build_cursor_dict(
            last_revision=22, holes=[hole(revision=21, seconds_ago=10)],
        ),
        'has_more_records': False,
    }


async def test_found_missing_hole(taxi_virtual_tariffs):
    response = await make_request(
        taxi_virtual_tariffs,
        last_revision=30,
        holes=[hole(revision=1, seconds_ago=10)],
    )
    assert response['special_requirements'][0]['id'] == 'empty'
    assert response['cursor'] == _build_cursor_dict(last_revision=30, holes=[])


async def test_remove_old_holes(taxi_virtual_tariffs):
    # Must remove hole with revision=5 because seconds_ago=100 > 60
    response = await make_request(
        taxi_virtual_tariffs,
        last_revision=30,
        holes=[
            hole(revision=5, seconds_ago=100),
            hole(revision=6, seconds_ago=10),
        ],
    )
    assert not response['special_requirements']
    assert response['cursor'] == _build_cursor_dict(
        last_revision=30, holes=[hole(revision=6, seconds_ago=10)],
    )
