import copy
import json
import typing

import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from metadata_storage_plugins.generated_tests import *  # noqa


VAL1: typing.Dict[str, typing.Any] = {}
VAL2 = {
    'experiments': [
        {
            'name': 'exp1',
            'position': 1,
            'version': 1,
            'json': '{}',
            'is_signal': False,
        },
        {
            'name': 'exp2',
            'position': 3,
            'version': 2,
            'json': '{"name1":"val1"}',
            'is_signal': False,
        },
    ],
}
VAL3 = {'tags': [{'name': 'tag1'}, {'name': 'tag2'}]}
VAL4 = {
    'experiments': [
        {
            'name': 'exp1',
            'position': 1,
            'version': 1,
            'json': '{}',
            'is_signal': False,
        },
        {
            'name': 'exp2',
            'position': 3,
            'version': 2,
            'json': '{"name1":"val1"}',
            'is_signal': False,
        },
    ],
    'tags': [{'name': 'tag1'}, {'name': 'tag2'}],
}
RESPONSE_BODY_404 = {'code': '404', 'message': 'item not found'}


def experiments_to_v2(exp_array, remove_deprecated=False):
    result = []
    for item in exp_array:
        item_v2 = copy.deepcopy(item)
        item_v2['value'] = json.loads(item_v2['json'])
        if remove_deprecated:
            del item_v2['json']
        result.append(item_v2)
    return result


def metadata_to_v2(metadata, remove_deprecated=False):
    result = copy.deepcopy(metadata)
    if 'experiments' in metadata:
        result['experiments'] = experiments_to_v2(
            metadata['experiments'], remove_deprecated=remove_deprecated,
        )
    return result


assert metadata_to_v2(VAL4) == {
    'experiments': [
        {
            'name': 'exp1',
            'position': 1,
            'version': 1,
            'value': {},
            'json': '{}',
            'is_signal': False,
        },
        {
            'name': 'exp2',
            'position': 3,
            'version': 2,
            'value': {'name1': 'val1'},
            'json': '{"name1":"val1"}',
            'is_signal': False,
        },
    ],
    'tags': [{'name': 'tag1'}, {'name': 'tag2'}],
}

assert metadata_to_v2(VAL4, True) == {
    'experiments': [
        {
            'name': 'exp1',
            'position': 1,
            'version': 1,
            'value': {},
            'is_signal': False,
        },
        {
            'name': 'exp2',
            'position': 3,
            'version': 2,
            'value': {'name1': 'val1'},
            'is_signal': False,
        },
    ],
    'tags': [{'name': 'tag1'}, {'name': 'tag2'}],
}


@pytest.mark.parametrize(
    'retrieve_handler_path,retrieve_expected_value_filter',
    [
        ('v1/metadata/retrieve', lambda x: x),
        ('v2/metadata/retrieve', metadata_to_v2),
    ],
)
@pytest.mark.now('2018-1-01T00:00:00Z')
async def test_store(
        taxi_metadata_storage,
        retrieve_handler_path,
        retrieve_expected_value_filter,
):
    response = await taxi_metadata_storage.put(
        'v1/metadata/store',
        params={'ns': 'ns3', 'id': 'id1'},
        json={'value': VAL1},
    )
    assert response.status_code == 200
    assert response.content == b'{}'

    response = await taxi_metadata_storage.put(
        'v1/metadata/store',
        params={'ns': 'ns3', 'id': 'id1'},
        json={'value': VAL2},
    )

    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': 'key already in storage',
    }

    response = await taxi_metadata_storage.post(
        retrieve_handler_path, params={'ns': 'ns3', 'id': 'id1'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': retrieve_expected_value_filter(VAL1),
        'updated': '2018-01-01T00:00:00+00:00',
    }

    response = await taxi_metadata_storage.post(
        retrieve_handler_path, params={'ns': 'ns5', 'id': 'id1'},
    )

    assert response.status_code == 404
    assert response.json() == RESPONSE_BODY_404


@pytest.mark.parametrize(
    'retrieve_handler_path,retrieve_expected_value_filter',
    [
        ('v1/metadata/retrieve', lambda x: x),
        ('v2/metadata/retrieve', metadata_to_v2),
    ],
)
@pytest.mark.parametrize(
    'namespace, id_, value',
    [('ns6', 'id1', VAL1), ('ns6', 'id2', VAL2), ('ns7', 'id2', VAL3)],
)
@pytest.mark.now('2018-1-01T00:00:00Z')
async def test_store_different_ns(
        taxi_metadata_storage,
        namespace,
        id_,
        value,
        retrieve_handler_path,
        retrieve_expected_value_filter,
):
    response = await taxi_metadata_storage.put(
        'v1/metadata/store',
        params={'ns': namespace, 'id': id_},
        json={'value': value},
    )
    assert response.status_code == 200
    assert response.content == b'{}'

    response = await taxi_metadata_storage.post(
        retrieve_handler_path, params={'ns': namespace, 'id': id_},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': retrieve_expected_value_filter(value),
        'updated': '2018-01-01T00:00:00+00:00',
    }


@pytest.mark.parametrize(
    'retrieve_handler_path,expected_value',
    [
        ('v1/metadata/retrieve', VAL4),
        ('v2/metadata/retrieve', metadata_to_v2(VAL4)),
    ],
)
async def test_retrieve_yt(
        mock_archive_api,
        taxi_metadata_storage,
        retrieve_handler_path,
        expected_value,
):
    response = await taxi_metadata_storage.post(
        retrieve_handler_path,
        params={'ns': 'test_ns', 'id': 'test_id', 'try_archive': True},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': expected_value,
        'updated': '2017-05-31T17:43:50.763+00:00',
    }

    response = await taxi_metadata_storage.post(
        retrieve_handler_path,
        params={'ns': 'test_ns', 'id': 'test_id2', 'try_archive': True},
    )
    assert response.status_code == 404
    assert response.json() == RESPONSE_BODY_404


@pytest.mark.config(METADATA_STORAGE_V2_DEPRECATED_FIELD=False)
async def test_retrieve_no_deprecated(taxi_metadata_storage, mock_archive_api):
    response = await taxi_metadata_storage.post(
        'v2/metadata/retrieve',
        params={'ns': 'test_ns', 'id': 'test_id', 'try_archive': True},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': metadata_to_v2(VAL4, True),
        'updated': '2017-05-31T17:43:50.763+00:00',
    }

    response = await taxi_metadata_storage.post(
        'v2/metadata/retrieve', params={'ns': 'ns1', 'id': 'id2'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': {
            'experiments': [
                {
                    'value': {},
                    'name': 'exp1',
                    'position': 1,
                    'version': 1,
                    'is_signal': False,
                },
                {
                    'value': {'name1': 'val1'},
                    'name': 'exp2',
                    'position': 3,
                    'version': 2,
                    'is_signal': False,
                },
            ],
        },
        'updated': '1970-01-15T06:56:08+00:00',
    }


@pytest.mark.parametrize(
    'retrieve_handler_path', ['v1/metadata/retrieve', 'v2/metadata/retrieve'],
)
async def test_404_from_archive(
        taxi_metadata_storage, mockserver, retrieve_handler_path,
):
    @mockserver.handler('/archive-api/v1/yt/lookup_rows')
    def _mock_archive_api(request):
        return mockserver.make_response(status=404)

    response = await taxi_metadata_storage.post(
        retrieve_handler_path,
        params={'ns': 'unknown_ns', 'id': 'unknown_id', 'try_archive': 'True'},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'ITEM_NOT_FOUND_IN_YT',
        'message': 'item not found in Yt',
    }
