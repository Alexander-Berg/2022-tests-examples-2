# pylint: disable=redefined-outer-name
import bson
import pytest

ORDER_ID = '71e78aa6276c38c08f12def2af04799e'


@pytest.mark.parametrize(
    'order, fields, expected_order',
    [
        (
            {
                '_id': 'ANONYMIZED_ORDER_1',
                'order': {'user_id': 'fake_id', 'field1': '1'},
                'foo': 'bar',
            },
            [
                {
                    'json_path': 'order.user_id',
                    'original_value': 'original_user_id',
                },
            ],
            {
                '_id': 'ANONYMIZED_ORDER_1',
                'order': {'user_id': 'original_user_id', 'field1': '1'},
                'foo': 'bar',
            },
        ),
        (
            {
                '_id': 'ANONYMIZED_ORDER_2',
                'order': {'user_id': 'fake_id', 'field1': '1'},
                'candidates': [
                    {'name': 'FIO1', 'key': 'value1'},
                    {'name': 'fake2', 'key': 'value2'},
                    {'name': 'fake3', 'key': 'value3'},
                    {'name': 'FIO4', 'key': 'value4'},
                ],
                'foo': 'bar',
            },
            [
                {'json_path': 'candidates.1.name', 'original_value': 'FIO2'},
                {'json_path': 'candidates.2.name', 'original_value': 'FIO3'},
            ],
            {
                '_id': 'ANONYMIZED_ORDER_2',
                'order': {'user_id': 'fake_id', 'field1': '1'},
                'candidates': [
                    {'name': 'FIO1', 'key': 'value1'},
                    {'name': 'FIO2', 'key': 'value2'},
                    {'name': 'FIO3', 'key': 'value3'},
                    {'name': 'FIO4', 'key': 'value4'},
                ],
                'foo': 'bar',
            },
        ),
        (
            {
                '_id': 'ANONYMIZED_ORDER_3',
                'order': {'user_id': 'fake_id', 'field1': '1'},
                'candidates': [
                    {'name': 'FIO1', 'key': 'value1'},
                    {'name': 'fake2', 'key': 'value2'},
                    {'name': 'fake3', 'key': 'value3'},
                    {'name': 'FIO4', 'key': 'value4'},
                ],
                'foo': 'bar',
            },
            [
                {
                    'json_path': 'order.user_id',
                    'original_value': 'original_user_id',
                },
                {
                    'json_path': 'order.field1',
                    'original_value': 'field1_original',
                },
                {'json_path': 'foo', 'original_value': 'bar_original'},
                {'json_path': 'candidates.1.name', 'original_value': 'FIO2'},
                {'json_path': 'candidates.2.name', 'original_value': 'FIO3'},
            ],
            {
                '_id': 'ANONYMIZED_ORDER_3',
                'order': {
                    'user_id': 'original_user_id',
                    'field1': 'field1_original',
                },
                'candidates': [
                    {'name': 'FIO1', 'key': 'value1'},
                    {'name': 'FIO2', 'key': 'value2'},
                    {'name': 'FIO3', 'key': 'value3'},
                    {'name': 'FIO4', 'key': 'value4'},
                ],
                'foo': 'bar_original',
            },
        ),
        (
            {
                '_id': 'ANONYMIZED_ORDER_4',
                'order': {
                    'users': [
                        {'foo': [{'bar': {'value': 1}}, {'bar2': {}}]},
                        {'foo': [{'bar': {'value': 2}}]},
                    ],
                },
                'foo': 'bar',
            },
            [
                {
                    'json_path': 'order.users.0.foo.0.bar.value',
                    'original_value': 11,
                },
                {
                    'json_path': 'order.users.1.foo.0.bar.value',
                    'original_value': 22,
                },
                {
                    'json_path': 'order.users.0.foo.1.bar2',
                    'original_value': {'abc': [1, 2, 3]},
                },
            ],
            {
                '_id': 'ANONYMIZED_ORDER_4',
                'order': {
                    'users': [
                        {
                            'foo': [
                                {'bar': {'value': 11}},
                                {'bar2': {'abc': [1, 2, 3]}},
                            ],
                        },
                        {'foo': [{'bar': {'value': 22}}]},
                    ],
                },
                'foo': 'bar',
            },
        ),
    ],
)
async def test_get_order_deanonymize(
        taxi_order_core,
        mongodb,
        order_archive_mock,
        order_takeout_mock,
        order,
        fields,
        expected_order,
):
    order_id = order['_id']
    order_archive_mock.set_order_proc(order)
    order_takeout_mock.register_fields(order_id, fields)
    request_params = {
        'order_id': order_id,
        'require_latest': True,
        'deanonymize': True,
    }
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-order', json=request_params,
    )
    assert response.status_code == 200
    doc = bson.BSON(response.content).decode()
    assert doc['doc'] == expected_order


async def test_get_order_from_mongo(taxi_order_core, mongodb):
    order_id = ORDER_ID
    request_params = {'order_id': order_id, 'require_latest': True}
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-order', json=request_params,
    )
    assert response.status_code == 200
    doc = bson.BSON(response.content).decode()
    assert doc['doc']['_id'] == order_id


async def test_get_order_404(taxi_order_core, mongodb, order_archive_mock):
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-order',
        json={'order_id': 'not_found'},
    )
    assert response.status_code == 404


async def test_get_order_from_archive(
        taxi_order_core, mongodb, order_archive_mock,
):
    order_archive_mock.set_order_proc({'_id': 'from_archive'})
    response = await taxi_order_core.post(
        '/internal/processing/v1/order-proc/get-order',
        json={'order_id': 'from_archive'},
    )
    assert response.status_code == 200
    doc = bson.BSON(response.content).decode()
    assert doc['doc']['_id'] == 'from_archive'


@pytest.fixture
async def order_takeout_mock(mockserver):
    cache = {}

    @mockserver.json_handler('/order-takeout/v1/get-fields')
    def _get_fields(request):
        order_id = request.json['order_id']
        data = bson.BSON.encode({'fields': cache[order_id]})
        return mockserver.make_response(
            status=200, content_type='application/bson', response=data,
        )

    class Mock:
        @classmethod
        def register_fields(cls, order_id, fields):
            cache[order_id] = fields

    return Mock()
