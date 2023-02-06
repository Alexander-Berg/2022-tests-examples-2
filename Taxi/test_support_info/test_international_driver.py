# pylint: disable=invalid-name
import uuid

import pytest

from support_info import settings


@pytest.mark.parametrize(
    'data',
    (
        {
            'subject': 'subject',
            'description': 'description',
            'driver_license': 'driver_license',
            'order_id': 'order_id',
            'requester': 'requester',
            'brand': 'yango',
            'status': 'new',
        },
        {
            'subject': 'subject',
            'description': 'description',
            'driver_license': 'driver_license',
            'requester': 'requester',
            'city': 'Москва',
            'brand': 'yango',
            'status': 'new',
        },
        {
            'subject': 'subject',
            'description': 'description',
            'driver_license': 'driver_license',
            'order_id': 'order_id_2',
            'requester': 'requester',
            'brand': 'uber',
            'status': 'new',
        },
    ),
)
async def test_international_driver(support_info_client, patch, data):
    uuid_hex = '8fcb4acfee754679b72b66efb36c2a1d'

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        assert queue == (
            settings.STQ_SUPPORT_INFO_INTERNATIONAL_DRIVER_TICKET_QUEUE
        )
        data_with_task_id = {**data, 'task_id': uuid_hex}
        assert kwargs['args'] == (data_with_task_id,)
        assert 'log_extra' in kwargs['kwargs']

    @patch('uuid.uuid4')
    def _uuid4(*args, **kwargs):
        return uuid.UUID(hex=uuid_hex)

    response = await support_info_client.post(
        '/v1/international_driver/create',
        json=data,
        headers={'YaTaxi-Api-Key': 'idriver-api-key'},
    )
    assert response.status == 200
    assert len(_put.calls) == 1


@pytest.mark.parametrize(
    'data',
    (
        {'order_id': 'order_id', 'requester': 'requester', 'status': 'new'},
        {
            'subject': '',
            'description': 'description',
            'driver_license': 'driver_license',
            'order_id': 'order_id',
            'requester': 'requester',
            'brand': 'yango',
            'status': 'new',
        },
        {
            'subject': 'subject',
            'description': '',
            'driver_license': 'driver_license',
            'order_id': 'order_id',
            'requester': 'requester',
            'brand': 'yango',
            'status': 'new',
        },
        {
            'subject': 'subject',
            'description': 'description',
            'driver_license': 'driver_license ',
            'order_id': 'order_id',
            'requester': 'requester',
            'brand': 'yango',
            'status': 'new',
        },
    ),
)
async def test_international_driver_errors(support_info_client, data):

    response = await support_info_client.post(
        '/v1/international_driver/create',
        json=data,
        headers={'YaTaxi-Api-Key': 'idriver-api-key'},
    )
    assert response.status == 400
