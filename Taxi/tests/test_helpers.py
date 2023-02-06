import datetime
import hmac
import json
import hashlib
import base64

import pytest
import freezegun

from taxi.robowarehouse.lib.misc import helpers
from taxi.robowarehouse.lib.misc import datetime_utils


def test_generate_id():
    result = helpers.generate_id()

    assert isinstance(result, str)
    assert len(result) == 36


def test_generate_string():
    result = helpers.generate_string(10)

    assert isinstance(result, str)
    assert len(result) == 10


@pytest.mark.parametrize('newer_than, start, expected_n_t, expected_o_t', [
    (None, 0, 2, None),
    (2, 3, 5, 3),
    (5, 6, None, 6),
])
def test_get_cursors_with_results_forward(newer_than, start, expected_n_t, expected_o_t):
    class TestObj:
        def __init__(self, pk):
            self.pk = pk

    items = [TestObj(pk) for pk in range(0, 7)]
    limit = 3

    newer_than, older_than, new_items = helpers.get_cursors_with_results(items[start:start + limit + 1],
                                                                         key='pk',
                                                                         limit=limit,
                                                                         newer_than=newer_than,
                                                                         older_than=None)

    expected_n_t = expected_n_t and helpers.base64_encode(expected_n_t)
    expected_o_t = expected_o_t and helpers.base64_encode(expected_o_t)

    assert expected_n_t == newer_than
    assert expected_o_t == older_than
    assert new_items == items[start:start + limit]


@pytest.mark.parametrize('older_than, start, end, expected_n_t, expected_o_t', [
    (5, 1, 5, 4, 2),
    (2, 0, 2, 1, None),
])
def test_get_cursors_with_results_backward(older_than, start, end, expected_n_t, expected_o_t):
    class TestObj:
        def __init__(self, pk):
            self.pk = pk

    items = [TestObj(pk) for pk in range(0, 6)]
    limit = 3

    newer_than, older_than, new_items = helpers.get_cursors_with_results(items[start:end],
                                                                         key='pk',
                                                                         limit=limit,
                                                                         newer_than=None,
                                                                         older_than=older_than)

    expected_n_t = expected_n_t and helpers.base64_encode(expected_n_t)
    expected_o_t = expected_o_t and helpers.base64_encode(expected_o_t)

    assert expected_n_t == newer_than
    assert expected_o_t == older_than
    assert new_items == items[start + 1:start + limit + 1] if end - start > limit else items[start:end]


def test_get_cursors_with_results_items_lt_limit():
    class TestObj:
        def __init__(self, pk):
            self.pk = pk

    items = [TestObj(0)]
    limit = 6

    newer_than, older_than, new_items = helpers.get_cursors_with_results(items,
                                                                         key='pk',
                                                                         limit=limit,
                                                                         newer_than=None,
                                                                         older_than=None)

    assert newer_than is None
    assert older_than is None
    assert new_items == items


def test_get_cursors_with_results_without_items():
    items = []
    limit = 5

    newer_than, older_than, new_items = helpers.get_cursors_with_results(items,
                                                                         key='pk',
                                                                         limit=limit,
                                                                         newer_than=None,
                                                                         older_than=None)

    assert newer_than is None
    assert older_than is None
    assert new_items == []


def test_sign_payload():
    registar_id = helpers.generate_id()
    exp = datetime_utils.get_now_timestamp()
    header = {'alg': 'HS256', 'typ': 'JWT'}
    payload = {'registrar_id': registar_id, 'exp': exp}
    key = 'test'

    segments = []

    for segment in (header, payload):
        segment = json.dumps(segment, separators=(",", ":"))
        segments.append(base64.urlsafe_b64encode(segment.encode()).decode())

    sign = hmac.new(key.encode(), '.'.join(segments).encode(), hashlib.sha256).digest()
    segments.append(base64.urlsafe_b64encode(sign).decode().replace('=', ''))

    expected = '.'.join(segments)
    result = helpers.sign_payload(payload, key)
    resulted_segment = result.split('.')

    assert resulted_segment[0] == segments[0]
    assert resulted_segment[1] == segments[1]
    assert resulted_segment[2] == segments[2]
    assert result == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=0)
def test_decode_jwt():
    registar_id = helpers.generate_id()
    exp = datetime_utils.get_now_timestamp() + datetime.timedelta(minutes=30).total_seconds()
    header = {'alg': 'HS256', 'typ': 'JWT'}
    payload = {'registrar_id': registar_id, 'exp': exp}
    key = 'test'

    segments = []
    for segment in (header, payload):
        segment = json.dumps(segment, separators=(",", ":"))
        segments.append(base64.urlsafe_b64encode(segment.encode()).decode())

    sign = hmac.new(key.encode(), '.'.join(segments).encode(), hashlib.sha256).digest()
    segments.append(base64.urlsafe_b64encode(sign).decode().replace('=', ''))

    token = '.'.join(segments)

    result = helpers.decode_jwt(token, key)

    assert result == payload
