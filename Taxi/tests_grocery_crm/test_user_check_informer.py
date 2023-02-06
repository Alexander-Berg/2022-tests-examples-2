# pylint: disable=cell-var-from-loop

import pytest

from tests_grocery_crm import common
from tests_grocery_crm import configs
from tests_grocery_crm import headers
from tests_grocery_crm import models

DEFAULT_CHARITY_SUB_INFO = {'status': 'was_subscribed', 'donated': True}

DEFAULT_COUPONS_REFERRAL = {
    'promocode': 'TYV4FLR',
    'value': 33,
    'currency': 'RUB',
    'rides_count': 1,
    'rides_left': 1,
    'descr': 'Temp',
    'message': 'Msg',
    'referral_service': 'lavka',
    'consumer_properties': {
        'percent': '20.0',
        'limit': '100.0',
        'value': '33.3',
        'currency': 'RUB',
    },
    'creator_properties': {'value': '33.3', 'currency': 'RUB'},
}

DEFAULT_INAPP_REQUEST = {
    'optional_kwargs': {
        'country_iso3': 'RUS',
        'persey_subscription_status': 'was_subscribed',
        'persey_user_has_donations': True,
    },
    'tanker_args': {
        'referral_code': 'TYV4FLR',
        'referral_value': '20%',
        'referral_limit': '100 ₽',
        'referral_min_cart_cost': '0 ₽',
        'reward_value': '33,3 ₽',
        'reward_min_cart_cost': '0 ₽',
    },
}


DEFAULT_COUPONS_REQUEST = {
    'application': {
        'name': headers.APP_NAME,
        'version': [0, 0, 0],
        'platform_version': [0, 0, 0],
    },
    'country': 'rus',
    'currency': 'RUB',
    'format_currency': True,
    'locale': headers.LOCALE,
    'payment_options': ['card'],
    'phone_id': headers.PHONE_ID,
    'yandex_uid': headers.YANDEX_UID,
    'zone_name': 'moscow',
    'services': ['grocery'],
}


def _make_informer(informer_id, source, priority, index, max_shown_count):
    return {
        'id': informer_id,
        'options': {
            'name': '{}-name'.format(informer_id),
            'source': source,
            'priority': priority,
            'same_priority_order': index,
            'max_shown_count': max_shown_count,
        },
        'payload': {},
    }


def _get_selected_informer_id(informers, total_shown_count, shown_count_by_id):
    # Function assumes tracking informers are correctly formed
    # and there exists an answer
    assert informers is not None
    assert total_shown_count is not None

    informers = list(
        filter(
            lambda informer: informer['options']['source'] == 'tracking',
            informers,
        ),
    )

    def get_priority(informer):
        return informer['options']['priority']

    sorted_priorities = sorted(
        list({get_priority(informer) for informer in informers}), reverse=True,
    )

    for priority in sorted_priorities:
        informers_with_same_priority = list(
            filter(
                lambda informer: get_priority(informer) == priority, informers,
            ),
        )

        informers_with_same_priority = sorted(
            informers_with_same_priority,
            key=lambda informer: informer['options']['same_priority_order'],
        )

        for informer in informers_with_same_priority:
            assert 'same_priority_order' in informer['options']

        informers_wsp_count = len(informers_with_same_priority)
        chosen_informer_idx = total_shown_count % informers_wsp_count
        for idx in range(
                chosen_informer_idx, informers_wsp_count + chosen_informer_idx,
        ):
            in_bounds_idx = idx % informers_wsp_count
            informer = informers_with_same_priority[in_bounds_idx]

            assert informer['options']['same_priority_order'] == in_bounds_idx

            if (
                    informer['options']['max_shown_count'] is None
                    or shown_count_by_id[informer['id']]
                    < informer['options']['max_shown_count']
            ):
                return informer['id']


def _create_informer_models(
        pgsql,
        informer_id,
        shown_count,
        idempotency_key,
        yandex_uid=headers.YANDEX_UID,
        source=None,
):
    informer = models.Informer(
        pgsql=pgsql,
        informer_id=informer_id,
        text=None,
        picture=None,
        text_color=None,
        background_color=None,
        modal=None,
        extra_data=None,
        source=source,
        save_in_db=shown_count != 0,
    )
    user_informer = models.UserInformer(
        pgsql=pgsql,
        informer_id=informer_id,
        yandex_uid=yandex_uid,
        shown_count=shown_count,
        idempotency_key=idempotency_key,
        save_in_db=shown_count != 0,
    )
    return informer, user_informer


@configs.BASIC_TRANSLATIONS
@configs.GROCERY_HELP_IS_NEAR
@configs.GROCERY_COUPONS_ZONE_NAME
@configs.GROCERY_REFERRAL_PAYMENT_OPTIONS
@pytest.mark.parametrize('shown_count', [0, 5])
async def test_basic(
        taxi_grocery_crm,
        pgsql,
        grocery_depots,
        inapp_communications,
        coupons,
        persey_core,
        shown_count,
):
    common.add_default_depot(grocery_depots)

    informers_data = [
        # source, priority, same_priority_order, max_shown_count
        ('tracking', 10, 0, 10),
        ('catalog', 15, None, None),
        ('tracking', 15, 1, 5),  # selected informer
        ('tracking', 15, 0, None),
        ('catalog', 50, None, 5),
        ('tracking', 15, 2, None),  # second selected informer
        ('catalog', 10, None, 10),
    ]
    # tracking_informers_with_top_priority_count = 3
    # Choose value so that
    # total_shown_count % tracking_informers_with_top_priority_count == 1
    total_shown_count = 10
    informers = [
        _make_informer(str(i), source, priority, index, max_shown_count)
        for i, (source, priority, index, max_shown_count) in enumerate(
            informers_data,
        )
    ]
    selected_informer_id = _get_selected_informer_id(
        informers,
        total_shown_count,
        {'0': total_shown_count - shown_count - 2, '2': shown_count, '5': 2},
    )

    coupons.set_referrals([DEFAULT_COUPONS_REFERRAL])
    coupons.set_request_check(DEFAULT_COUPONS_REQUEST)

    persey_core.set_charity_subscription_info(DEFAULT_CHARITY_SUB_INFO)

    inapp_communications.set_informers(informers)
    inapp_communications.set_request_check(DEFAULT_INAPP_REQUEST)

    informers_models = [
        _create_informer_models(
            pgsql=pgsql,
            informer_id='0',
            shown_count=total_shown_count - shown_count - 2,
            idempotency_key='0',
        ),
        _create_informer_models(
            pgsql=pgsql,
            informer_id='2',
            shown_count=shown_count,
            idempotency_key='2',
        ),
        _create_informer_models(
            pgsql=pgsql, informer_id='5', shown_count=2, idempotency_key='5',
        ),
    ]

    response = await taxi_grocery_crm.post(
        '/internal/user/v1/check-informer',
        json={
            'idempotency_key': 'idempotency_key',
            'depot_id': common.DEPOT_ID,
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['informer_id'] == selected_informer_id
    assert inapp_communications.grocery_comm_times_called() == 1
    assert coupons.referral_times_called() == 1
    assert persey_core.subs_status_times_called() == 1

    for informer, user_informer in informers_models:
        if informer.informer_id == selected_informer_id:
            user_informer.shown_count = user_informer.shown_count + 1
            user_informer.idempotency_key = 'idempotency_key'
        informer.compare_with_db()
        user_informer.compare_with_db()


@pytest.mark.parametrize('shown_count', [2, 5])
async def test_top_priority_informers_already_shown(
        taxi_grocery_crm, pgsql, inapp_communications, shown_count,
):
    informers_data = [
        # source, priority, same_priority_order, max_shown_count, shown_count
        ('tracking', 10, 0, 10, 5),
        ('tracking', 15, 1, 5, shown_count),
        ('tracking', 15, 0, 5, 5),
        ('tracking', 15, 2, 5, 5),
    ]
    informers = [
        _make_informer(str(i), source, priority, index, max_shown_count)
        for i, (source, priority, index, max_shown_count, _) in enumerate(
            informers_data,
        )
    ]
    selected_informer_id = '1' if shown_count != 5 else '0'

    inapp_communications.set_informers(informers)

    informers_models = []
    for i, informer in enumerate(informers_data):
        informers_models.append(
            _create_informer_models(
                pgsql=pgsql,
                informer_id=str(i),
                shown_count=informer[4],
                idempotency_key=str(i),
            ),
        )

    response = await taxi_grocery_crm.post(
        '/internal/user/v1/check-informer',
        json={'idempotency_key': 'idempotency_key'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['informer_id'] == selected_informer_id
    assert inapp_communications.grocery_comm_times_called() == 1

    for informer, user_informer in informers_models:
        if informer.informer_id == selected_informer_id:
            user_informer.shown_count = user_informer.shown_count + 1
            user_informer.idempotency_key = 'idempotency_key'
        informer.compare_with_db()
        user_informer.compare_with_db()


async def test_catalog_informers(
        taxi_grocery_crm, pgsql, inapp_communications,
):
    informers_data = [
        # source, priority, same_priority_order, max_shown_count, shown_count
        ('catalog', 10, 0, 10, 1),
        ('tracking', 15, 0, 5, 1),
        ('catalog', 15, 0, 5, 1),
    ]
    informers = [
        _make_informer(str(i), source, priority, index, max_shown_count)
        for i, (source, priority, index, max_shown_count, _) in enumerate(
            informers_data,
        )
    ]

    inapp_communications.set_informers(informers)

    informers_models = []
    for i, informer in enumerate(informers_data):
        informers_models.append(
            _create_informer_models(
                pgsql=pgsql,
                informer_id=str(i),
                shown_count=informer[4],
                idempotency_key=str(i),
                source=informer[0],
            ),
        )

    response = await taxi_grocery_crm.post(
        '/internal/user/v1/check-informer',
        json={
            'idempotency_key': 'idempotency_key',
            'request_source': 'catalog',
        },
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert inapp_communications.grocery_comm_times_called() == 1

    for informer, user_informer in informers_models:
        if informer.source == 'catalog':
            user_informer.shown_count = user_informer.shown_count + 1
            user_informer.idempotency_key = 'idempotency_key'
        informer.compare_with_db()
        user_informer.compare_with_db()


async def test_no_informers(taxi_grocery_crm, inapp_communications):
    response = await taxi_grocery_crm.post(
        '/internal/user/v1/check-informer',
        json={'idempotency_key': 'idempotency_key'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert 'informer_id' not in response.json()
    assert inapp_communications.grocery_comm_times_called() == 1


async def test_single_informer_default_same_priority_order(
        taxi_grocery_crm, pgsql, inapp_communications,
):
    informer_id = 'test_id'
    informers = [
        _make_informer(
            informer_id=informer_id,
            source='tracking',
            priority=1,
            index=None,
            max_shown_count=None,
        ),
    ]
    inapp_communications.set_informers(informers)

    informer, user_informer = _create_informer_models(
        pgsql=pgsql,
        informer_id=informer_id,
        shown_count=0,
        idempotency_key=None,
    )

    response = await taxi_grocery_crm.post(
        '/internal/user/v1/check-informer',
        json={'idempotency_key': 'idempotency_key'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['informer_id'] == informer_id
    assert inapp_communications.grocery_comm_times_called() == 1

    user_informer.shown_count = user_informer.shown_count + 1
    user_informer.idempotency_key = 'idempotency_key'
    informer.compare_with_db()
    user_informer.compare_with_db()


async def test_informers_with_no_same_priority_order(
        taxi_grocery_crm, inapp_communications,
):
    informers_data = [
        ('tracking', 10, 0),
        ('catalog', 15, None),
        (
            'tracking',
            15,
            4,
        ),  # top_priority_informer with indexes 4 and 5, needed 0
        ('tracking', 15, 5),
        ('catalog', 10, None),
    ]
    informers = [
        _make_informer(str(i), source, priority, index, max_shown_count=None)
        for i, (source, priority, index) in enumerate(informers_data)
    ]
    inapp_communications.set_informers(informers)

    response = await taxi_grocery_crm.post(
        '/internal/user/v1/check-informer',
        json={'idempotency_key': 'idempotency_key'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 500
    assert inapp_communications.grocery_comm_times_called() == 1


async def test_inconsistent_same_priority_order_numeration(
        taxi_grocery_crm, pgsql, inapp_communications,
):
    informers_data = [
        # source, priority, same_priority_order, max_shown_count, shown_count
        ('tracking', 15, 0, 5, 5),
        ('tracking', 15, 99, 5, 1),
        ('tracking', 15, 1, 5, 5),
        ('tracking', 15, 2, 5, 5),
    ]
    informers = [
        _make_informer(str(i), source, priority, index, max_shown_count)
        for i, (source, priority, index, max_shown_count, _) in enumerate(
            informers_data,
        )
    ]

    inapp_communications.set_informers(informers)

    informers_models = []
    for i, informer in enumerate(informers_data):
        informers_models.append(
            _create_informer_models(
                pgsql=pgsql,
                informer_id=str(i),
                shown_count=informer[4],
                idempotency_key=str(i),
            ),
        )

    response = await taxi_grocery_crm.post(
        '/internal/user/v1/check-informer',
        json={'idempotency_key': 'idempotency_key'},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 500
    assert inapp_communications.grocery_comm_times_called() == 1


async def test_idempotency(taxi_grocery_crm, pgsql, inapp_communications):
    informer_id = 'test'
    idempotency_key = 'idempotency_key'

    user_informer = models.UserInformer(
        pgsql=pgsql,
        informer_id=informer_id,
        idempotency_key=idempotency_key,
        yandex_uid=headers.YANDEX_UID,
    )

    response = await taxi_grocery_crm.post(
        '/internal/user/v1/check-informer',
        json={'idempotency_key': idempotency_key},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert inapp_communications.grocery_comm_times_called() == 0
    user_informer.compare_with_db()
