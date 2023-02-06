import pytest

from tests_eats_coupons import conftest
from . import experiments
from . import utils

# fixture for pagination test


@pytest.fixture(name='mock_eats_eaters')
def _mock_eats_eaters(mockserver):
    class Context:
        mock_eater_cnt = 0
        limit = 5
        mock_eaters_client = None
        glue_uids = []

    context = Context()

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eaters(request):
        request_uids = request.json['passport_uids']
        assert set(request_uids) == set(context.glue_uids)
        if context.mock_eater_cnt:
            assert request.json['pagination'] == {
                'after': str(context.mock_eater_cnt * context.limit) + '0',
            }
        sorted_uids = sorted(request_uids, key=int)
        left = context.limit * context.mock_eater_cnt
        right = min(left + context.limit, len(context.glue_uids))
        has_more = right < len(context.glue_uids)
        response_uids = sorted_uids[left:right]
        response_eaters = [
            {
                'id': uid + '0',
                'uuid': 'uuid' + uid,
                'created_at': '2019-12-31T10:59:59+03:00',
                'updated_at': '2019-12-31T10:59:59+03:00',
            }
            for uid in response_uids
        ]
        context.mock_eater_cnt += 1
        return mockserver.make_response(
            json={
                'eaters': response_eaters,
                'pagination': {'limit': 5, 'has_more': has_more},
            },
        )

    context.mock_eaters_client = _mock_eaters
    return context


@experiments.eats_coupons_validators(['eats-order-cnt-validator'])
@pytest.mark.now('2019-03-06T11:30:00+0300')
@experiments.use_glue_uids()
async def test_eats_eaters_pagination(
        taxi_eats_coupons, mock_order_stats, mock_eats_eaters,
):

    glue_uids = [str(uid) for uid in range(1, 17)]
    glue_uids.append(conftest.YANDEX_UID)
    validation_request = {
        'coupon_id': 'ID1',
        'series_id': 'series_id_1',
        'series_meta': {'eats_order_cnt_from': 4, 'eats_order_cnt_to': 5},
        'glue': glue_uids,
        'source_handler': 'check',
    }

    mock_eats_eaters.glue_uids = glue_uids
    mock_order_stats.exp_identities_cnt = (
        len(glue_uids) + 2
    )  # 2 - device and phone

    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json=validation_request,
        headers=conftest.HEADERS,
    )

    assert mock_eats_eaters.mock_eaters_client.times_called == 4
    assert mock_order_stats.order_stats_client.times_called == 1
    assert response.status_code == 200


@experiments.eats_coupons_validators(['eats-order-cnt-validator'])
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    'use_glue_uids',
    [
        pytest.param(False, id='not_use_glue'),
        pytest.param(True, marks=experiments.use_glue_uids(), id='use_glues'),
    ],
)
@pytest.mark.parametrize(
    'card_id',
    [
        pytest.param(False, id='no_card_id'),
        pytest.param(True, id='with_card_id'),
    ],
)
@pytest.mark.parametrize(
    'glue_uids',
    [
        pytest.param(['glue_uid1', 'glue_uid2'], id='glue_in_request'),
        pytest.param([], id='no_glue_in_request'),
    ],
)
async def test_eats_order_cnt_basic_flow(
        taxi_eats_coupons,
        mockserver,
        use_glue_uids,
        glue_uids,
        card_id,
        mock_order_stats,
):

    eater_cnt_stat = 4
    card_cnt_stat = 5
    validation_request = {
        'coupon_id': 'ID1',
        'series_id': 'series_id_1',
        'series_meta': {'eats_order_cnt_from': 4, 'eats_order_cnt_to': 5},
        'source_handler': 'check',
    }

    if card_id:
        validation_request.update({'payload': {'card_id': 'some_card'}})

    if glue_uids:
        validation_request.update({'glue': glue_uids})

    fetch_eaters = (len(glue_uids) > 0) and use_glue_uids
    glue = set(glue_uids) if fetch_eaters else set()
    glue.add(conftest.YANDEX_UID)

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def mock_eaters(request):
        body = request.json
        assert set(body['passport_uids']) == glue
        response_eaters = [
            {
                'id': 'eater' + uid,
                'uuid': 'uuid' + uid,
                'created_at': '2019-12-31T10:59:59+03:00',
                'updated_at': '2019-12-31T10:59:59+03:00',
            }
            for uid in glue
        ]
        return mockserver.make_response(
            json={
                'eaters': response_eaters,
                'pagination': {'limit': 1000, 'has_more': False},
            },
        )

    mock_order_stats.orders_cnt = [
        utils.StatsCounter(eater_cnt_stat),
        utils.StatsCounter(100500, business='grocery'),  # will be ignored
    ]
    mock_order_stats.exp_identities_cnt = (
        len(glue) + int(card_id) + 2
    )  # 2 - device and phone
    if card_id:
        mock_order_stats.orders_cnt.append(utils.StatsCounter(card_cnt_stat))

    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json=validation_request,
        headers=conftest.HEADERS,
    )

    assert mock_eaters.has_calls == fetch_eaters
    assert mock_order_stats.order_stats_client.times_called == 1
    assert response.status_code == 200

    response = response.json()
    if card_id:
        assert response == utils.create_response(
            False,
            True,
            'ORDER_SEQUENCE_FAILURE',
            'Количество заказов не соответсует услввию',
        )
    else:
        assert response == utils.create_response(True, True)


@experiments.eats_coupons_validators(['eats-order-cnt-validator'])
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    'eats_order_cnt_from,eats_order_cnt_to, success',
    [
        pytest.param(None, 5, False, id='more_orders'),
        pytest.param(0, 2, False, id='more_orders_2'),
        pytest.param(6, None, False, id='less_orders'),
        pytest.param(7, 9, False, id='less_orders_2'),
        pytest.param(4, None, True, id='exactly_orders'),
        pytest.param(None, 7, True, id='exactly_orders_2'),
        pytest.param(5, 6, True, id='exactly_orders_3'),
    ],
)
async def test_eats_order_cnt_check_intervals(
        taxi_eats_coupons,
        eats_order_cnt_from,
        eats_order_cnt_to,
        success,
        mock_order_stats,
):
    mock_order_stats.orders_cnt = [utils.StatsCounter(5, None, None)]

    series_meta = {}
    if eats_order_cnt_from is not None:
        series_meta.update({'eats_order_cnt_from': eats_order_cnt_from})
    if eats_order_cnt_to is not None:
        series_meta.update({'eats_order_cnt_to': eats_order_cnt_to})
    validation_request = {
        'coupon_id': 'ID1',
        'series_id': 'series_id_1',
        'series_meta': series_meta,
        'source_handler': 'check',
    }

    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json=validation_request,
        headers=conftest.HEADERS,
    )

    assert mock_order_stats.order_stats_client.times_called == 1
    assert response.status_code == 200

    response = response.json()
    if success:
        assert response == utils.create_response(True, True)
    else:
        assert response == utils.create_response(
            False,
            True,
            'ORDER_SEQUENCE_FAILURE',
            'Количество заказов не соответсует услввию',
        )


@experiments.eats_coupons_validators(['eats-order-cnt-validator'])
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    'eats_order_cnt_from,eats_order_cnt_to',
    [pytest.param(None, 1, id='empty_from'), pytest.param(0, 1, id='0_from')],
)
@pytest.mark.parametrize(
    'stat_cnt,success',
    [
        pytest.param(0, True, id='first_order'),
        pytest.param(5, False, id='not_first_order'),
    ],
)
async def test_eats_order_cnt_first_order(
        taxi_eats_coupons,
        eats_order_cnt_from,
        eats_order_cnt_to,
        success,
        stat_cnt,
        mock_order_stats,
):
    mock_order_stats.orders_cnt = [utils.StatsCounter(stat_cnt)]

    series_meta = {}
    if eats_order_cnt_from is not None:
        series_meta.update({'eats_order_cnt_from': eats_order_cnt_from})
    if eats_order_cnt_to is not None:
        series_meta.update({'eats_order_cnt_to': eats_order_cnt_to})
    validation_request = {
        'coupon_id': 'ID1',
        'series_id': 'series_id_1',
        'series_meta': series_meta,
        'source_handler': 'check',
    }

    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json=validation_request,
        headers=conftest.HEADERS,
    )

    assert mock_order_stats.order_stats_client.times_called == 1
    assert response.status_code == 200

    response = response.json()
    if success:
        assert response == utils.create_response(True, True)
    else:
        assert response == utils.create_response(
            False, True, 'FIRST_ORDER_FAILURE', 'У вас не первый заказ',
        )


@experiments.eats_coupons_validators(['eats-order-cnt-validator'])
@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_eats_order_cnt_skipped(taxi_eats_coupons):
    validation_request = {
        'coupon_id': 'ID1',
        'series_id': 'series_id_1',
        'series_meta': {},
        'source_handler': 'check',
    }

    response = await taxi_eats_coupons.post(
        '/internal/v1/coupons/validate',
        json=validation_request,
        headers=conftest.HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == utils.create_response(
        True, True, 'SKIPPED_VALIDATION',
    )
