import bson
import pytest


@pytest.mark.parametrize(
    'namespace,request_additional_data,error_message',
    [
        (
            'ns1',
            {'additional_field': 'value'},
            'namespace not allowed for additional_data',
        ),
        (
            'ns2',
            {'wrong_additional_field': 'value'},
            'field not allowed for additional_data',
        ),
    ],
)
@pytest.mark.config(
    METADATA_STORAGE_ALLOWED_ADDITIONAL_DATA={
        'ns2': {'additional_field': {'ticket': 'ticket'}},
    },
)
async def test_forbidden_field(
        taxi_metadata_storage,
        namespace,
        request_additional_data,
        error_message,
):
    request_body = {'value': {'additional_data': request_additional_data}}
    response = await taxi_metadata_storage.put(
        'v1/metadata/store',
        params={'ns': namespace, 'id': 'some_id'},
        json=request_body,
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': error_message}


@pytest.mark.parametrize(
    'retrieve_handler_path', ['v1/metadata/retrieve', 'v2/metadata/retrieve'],
)
@pytest.mark.parametrize(
    'request_additional_data',
    [
        'string_value',
        123,
        123.4,
        8589934591,  # 33 bit integer
        -8589934591,
        True,
        False,
        [],
        ['array_val1', 'array_val2'],
        {'field': 'value'},
        [{'class': 'string', 'special_requirements': [{'id': 'string'}]}],
    ],
)
@pytest.mark.config(
    METADATA_STORAGE_ALLOWED_ADDITIONAL_DATA={
        'ns2': {'tariffs': {'ticket': 'ticket'}},
    },
)
@pytest.mark.now('2018-1-01T00:00:00Z')
async def test_correct_field(
        taxi_metadata_storage, request_additional_data, retrieve_handler_path,
):
    request_body = {
        'value': {'additional_data': {'tariffs': request_additional_data}},
    }
    response = await taxi_metadata_storage.put(
        'v1/metadata/store',
        params={'ns': 'ns2', 'id': 'some_id'},
        json=request_body,
    )
    assert response.status_code == 200
    assert response.content == b'{}'

    response = await taxi_metadata_storage.post(
        retrieve_handler_path, params={'ns': 'ns2', 'id': 'some_id'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'value': {'additional_data': {'tariffs': request_additional_data}},
        'updated': '2018-01-01T00:00:00+00:00',
    }


@pytest.mark.parametrize(
    'retrieve_handler_path', ['v1/metadata/retrieve', 'v2/metadata/retrieve'],
)
@pytest.mark.parametrize(
    'archive_response,expected',
    [
        (
            {
                'items': [
                    {
                        'additional_data': {'test': 'test'},
                        'experiments': [],
                        'tags': [],
                        'updated': 1572949800.00,
                    },
                ],
            },
            {
                'updated': '2019-11-05T10:30:00+00:00',
                'value': {
                    'additional_data': {'test': 'test'},
                    'experiments': [],
                    'tags': [],
                },
            },
        ),
        (
            {
                'items': [
                    {
                        'additional_data': None,
                        'experiments': [],
                        'tags': [],
                        'updated': 1572949800.00,
                    },
                ],
            },
            {
                'updated': '2019-11-05T10:30:00+00:00',
                'value': {'experiments': [], 'tags': []},
            },
        ),
        (
            {
                'items': [
                    {'experiments': [], 'tags': [], 'updated': 1572949800.00},
                ],
            },
            {
                'updated': '2019-11-05T10:30:00+00:00',
                'value': {'experiments': [], 'tags': []},
            },
        ),
    ],
)
async def test_get_value_from_yt(
        taxi_metadata_storage,
        mockserver,
        retrieve_handler_path,
        archive_response,
        expected,
):
    @mockserver.json_handler('/archive-api/v1/yt/lookup_rows')
    def handle_archive(request):
        return mockserver.make_response(
            bson.BSON.encode(archive_response),
            status=200,
            content_type='application/bson',
            charset='utf-8',
        )

    response = await taxi_metadata_storage.post(
        retrieve_handler_path,
        params={'ns': 'ns2', 'id': 'some_id', 'try_archive': True},
    )

    assert response.status_code == 200
    assert response.json() == expected
    assert handle_archive.times_called == 1
