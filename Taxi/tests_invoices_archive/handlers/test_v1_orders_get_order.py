# pylint: disable=redefined-outer-name
import bson
import pytest


@pytest.mark.parametrize(
    'order, fields, expected_order',
    [
        pytest.param(
            {
                '_id': 'order_1',
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
                '_id': 'order_1',
                'order': {
                    'user_id': 'original_user',
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
            id='order_1 deanonymize',
        ),
        pytest.param(
            {
                '_id': 'order_2',
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
                '_id': 'order_2',
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
            id='order_2 deanonymize',
        ),
    ],
)
@pytest.mark.ydb(files=['fill_fields.sql'])
async def test_get_order_deanonymize(
        taxi_invoices_archive,
        mongodb,
        ydb,
        mock_archive_api,
        order,
        fields,
        expected_order,
):
    order_id = order['_id']
    mock_archive_api.set_order(order)
    request_params = {
        'order_id': order_id,
        'require_latest': True,
        'deanonymize': True,
    }
    response = await taxi_invoices_archive.post(
        '/v1/orders/get-order', json=request_params,
    )
    assert response.status_code == 200
    doc = bson.BSON(response.content).decode()
    assert doc['doc'] == expected_order


async def test_get_order_from_mongo(taxi_invoices_archive, mongodb):
    order_id = '71e78aa6276c38c08f12def2af04799e'
    request_params = {'order_id': order_id, 'require_latest': True}
    response = await taxi_invoices_archive.post(
        '/v1/orders/get-order', json=request_params,
    )
    assert response.status_code == 200
    doc = bson.BSON(response.content).decode()
    assert doc['doc']['_id'] == order_id


async def test_get_order_404(taxi_invoices_archive, mongodb, mock_archive_api):
    response = await taxi_invoices_archive.post(
        '/v1/orders/get-order', json={'order_id': 'not_found'},
    )
    assert response.status_code == 404


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'source-service', 'dst': 'invoices-archive'}],
    TVM_SERVICES={'source-service': 111, 'invoices-archive': 2345},
)
@pytest.mark.tvm2_ticket({111: 'wrong'})
async def test_get_order_401(taxi_invoices_archive, mongodb, mock_archive_api):
    headers = {'X-Ya-Service-Ticket': 'wrong'}
    response = await taxi_invoices_archive.post(
        '/v1/orders/get-order',
        json={'order_id': 'not_found', 'deanonymize': True},
        headers=headers,
    )
    assert response.status_code == 401


async def test_get_order_restore(
        taxi_invoices_archive, mongodb, mock_archive_api,
):
    mock_archive_api.set_order({'_id': 'restore'})
    response = await taxi_invoices_archive.post(
        '/v1/orders/get-order',
        json={'order_id': 'restore', 'autorestore': True},
    )
    assert response.status_code == 200
    assert mock_archive_api.mock_restore.times_called == 1


async def test_get_order_from_archive(
        taxi_invoices_archive, mongodb, mock_archive_api,
):
    mock_archive_api.set_order({'_id': 'from_archive'})
    response = await taxi_invoices_archive.post(
        '/v1/orders/get-order', json={'order_id': 'from_archive'},
    )
    assert response.status_code == 200
    doc = bson.BSON(response.content).decode()
    assert doc['doc']['_id'] == 'from_archive'


@pytest.fixture(name='mock_archive_api')
def _mock_archive_api(mockserver):
    cache = {}

    @mockserver.json_handler('/archive-api/archive/order')
    def _get(request):
        order_id = request.json['id']
        if order_id in cache:
            response = {'doc': cache[order_id]}
            return mockserver.make_response(
                bson.BSON.encode(response), status=200,
            )
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/archive-api/archive/orders/restore')
    async def _restore(request):
        order_id = request.json['id']
        if order_id in cache:
            return [{'id': order_id, 'status': 'restored'}]
        return [{'id': order_id, 'status': 'not_found'}]

    class Mock:
        @classmethod
        def set_order(cls, order):
            cache[order['_id']] = order

        mock_restore = _restore
        mock_get = _get

    return Mock()
