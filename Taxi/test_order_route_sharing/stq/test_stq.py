# pylint: disable=redefined-outer-name,unused-argument
import bson
import pytest

from order_route_sharing.stq import finished_order
from order_route_sharing.stq import insert_order
from .. import helpers


@pytest.fixture
def mock_user_api_search(mockserver, load_json):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_users_search(request):
        assert request.json['phone_ids']
        assert request.json['applications'] == ['android', 'iphone']
        assert request.json['fields'] == [
            '_id',
            'application_version',
            'application',
        ]

        return load_json('user_api_response.json')[
            request.json['phone_ids'][0]
        ]

    return _mock_users_search


@pytest.mark.parametrize(
    'phone_ids, user_exists',
    [
        pytest.param(
            [
                bson.ObjectId('00aaaaaaaaaaaaaaaaaaaa01'),
                bson.ObjectId('00aaaaaaaaaaaaaaaaaaaa66'),
            ],
            [True, False],
            id='with phone_id',
        ),
        pytest.param(
            [None, bson.ObjectId('00aaaaaaaaaaaaaaaaaaaa01')],
            [True],
            id='with phone_id',
        ),
        pytest.param(None, None, id='without phone_id'),
        pytest.param([], None, id='without phone_id'),
    ],
)
async def test_stq_insert_order(
        stq3_context, pgsql, mock_user_api_search, phone_ids, user_exists,
):
    assert not helpers.select_by_order_id(pgsql, 'order_new')

    await insert_order.task(
        stq3_context,
        order_id='order_new',
        sharing_key='key_new',
        phone_ids=phone_ids,
        corp_client_id=None,
        application=None,
        tariff_class=None,
    )

    item = helpers.select_by_order_id(pgsql, 'order_new')

    expected_phone_ids = None
    if phone_ids:
        expected_phone_ids = [str(_id) for _id in phone_ids if _id]

    assert item.sharing_key == 'key_new'
    assert not item.finished_at
    assert item.phone_ids == expected_phone_ids
    assert item.user_exists == user_exists
    if expected_phone_ids:
        assert mock_user_api_search.times_called == len(expected_phone_ids)
    else:
        assert not mock_user_api_search.times_called


async def test_stq_insert_exist_order(
        stq3_context, mock_user_api_search, pgsql,
):
    order_id = 'order_new'
    phone_ids = [bson.ObjectId('00aaaaaaaaaaaaaaaaaaaa01'), 'any']

    assert not helpers.select_by_order_id(pgsql, order_id)

    for _ in range(5):
        await insert_order.task(
            stq3_context,
            order_id=order_id,
            sharing_key='key_new',
            phone_ids=phone_ids,
            corp_client_id=None,
            application=None,
            tariff_class=None,
        )

    item = helpers.select_by_order_id(pgsql, order_id)

    if phone_ids:
        assert item.phone_ids == list(map(str, phone_ids))
    else:
        assert not item.phone_ids


@pytest.mark.parametrize(
    'order_id, sharing_key, phone_ids',
    [
        pytest.param(
            'order_1', 'key_1', ['00aaaaaaaaaaaaaaaaaaaa01'], id='order exist',
        ),
        pytest.param('order_404', 'key_404', [], id='order not exist'),
        pytest.param(
            'order_2',
            'key_2',
            ['00aaaaaaaaaaaaaaaaaaaa01'],
            id='order with finished_at',
        ),
    ],
)
async def test_stq_finished_order(
        stq3_context, pgsql, order_id, sharing_key, phone_ids,
):
    await finished_order.task(
        stq3_context,
        order_id=order_id,
        sharing_key=sharing_key,
        phone_ids=phone_ids,
    )

    item = helpers.select_by_order_id(pgsql, order_id)

    assert item.finished_at
    if order_id == 'order_2':
        assert str(item.finished_at) == '2018-01-01 10:00:00+03:00'


async def test_stq_insert_after_finished(stq3_context, pgsql):
    await finished_order.task(
        stq3_context,
        order_id='order_666',
        sharing_key='key_666',
        phone_ids=[],
    )

    await insert_order.task(
        stq3_context,
        order_id='order_666',
        sharing_key='key_new',
        phone_ids=[],
        corp_client_id=None,
        application=None,
        tariff_class=None,
    )

    item = helpers.select_by_order_id(pgsql, 'order_666')
    assert item.order_id == 'order_666'
    assert item.sharing_key == 'key_666'
    assert item.finished_at
