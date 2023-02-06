import datetime

import pytest

from taxi.util import dates as dates_utils

from corp_clients.utils import json_util
from test_corp_clients.web import test_utils

NOW = datetime.datetime.utcnow().replace(microsecond=0)

pytestmark = pytest.mark.config(  # pylint: disable=invalid-name
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'root_geo_node': 'br_russia', 'default_language': 'ru'},
    },
)


def iso_localize(data: datetime.datetime) -> str:
    return dates_utils.localize(data).isoformat()


def timedelta_dec(**kwargs) -> datetime.datetime:
    return NOW - datetime.timedelta(**kwargs)


def timedelta_inc(**kwargs) -> datetime.datetime:
    return NOW + datetime.timedelta(**kwargs)


async def test_service_taxi_get_404(web_app_client):
    response = await web_app_client.get(
        '/v1/services/taxi', params={'client_id': 'unknown'},
    )
    response_json = await response.json()

    assert response.status == 404, response_json
    assert response_json == {
        'code': 'NOT_FOUND',
        'details': {'reason': 'Service taxi for client unknown not found'},
        'message': 'Not found',
    }


@pytest.mark.now(NOW.isoformat())
async def test_service_taxi_get(web_app_client):
    response = await web_app_client.get(
        '/v1/services/taxi', params={'client_id': 'client_id_1'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {
        'categories': [{'name': 'econom'}, {'name': 'vip'}],
        'comment': 'Держи дверь, стой у входа!',
        'default_category': 'econom',
        'is_active': True,
        'is_visible': True,
    }


@pytest.mark.now(NOW.isoformat())
async def test_service_taxi_update(web_app_client, db):
    data_base = {
        'is_active': False,
        'is_visible': False,
        'is_test': True,
        'deactivate_threshold_ride': 1,
        'deactivate_threshold_date': timedelta_inc(days=1),
    }

    data = dict(
        data_base,
        **{
            'comment': 'Корп поездка',
            'default_category': 'vip',
            'categories': [{'name': 'vip'}],
        },
    )

    old_client = await db.secondary.corp_clients.find_one(
        {'_id': 'client_id_1'},
    )

    expected_client = old_client
    expected_client['services']['taxi'] = data_base
    expected_client['services']['taxi']['comment'] = data['comment']

    response = await web_app_client.patch(
        '/v1/services/taxi',
        params={'client_id': 'client_id_1'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_1'})

    for key in ['created', 'updated', 'updated_at']:
        expected_client.pop(key, None)
        client.pop(key, None)

    assert client == expected_client

    # validate client_categories
    client_categories = await db.secondary.corp_client_categories.find_one(
        {'client_id': 'client_id_1'},
    )

    updated = client_categories.pop('updated', None)
    assert isinstance(updated, datetime.datetime)

    assert client_categories == {
        '_id': 'client_categories_id_1',
        'client_id': 'client_id_1',
        'service': 'taxi',
        'categories': data['categories'],
        'default_category': data['default_category'],
    }


@pytest.mark.now(NOW.isoformat())
async def test_service_taxi_update_categories_406(web_app_client):
    data = {'categories': [{'name': 'unknown'}]}

    response = await web_app_client.patch(
        '/v1/services/taxi',
        params={'client_id': 'client_id_1'},
        json=json_util.serialize(data),
    )
    response_json = await response.json()

    assert response.status == 406, response_json
    assert response_json['details']['reason'] == 'unknown is not allowed'


@pytest.mark.config(
    CORP_DEFAULT_CATEGORIES={'rus': ['econom', 'cargo', 'courier']},
    CORP_WITHOUT_VAT_DEFAULT_CATEGORIES={'rus': ['comfort_plus', 'econom']},
)
async def test_wo_vat_invalid_default_category(
        web_app_client, patch, db, personal_mock, corp_billing_mock,
):
    await db.corp_clients.find_one_and_update(
        {'_id': 'client_id_1'}, {'$set': {'without_vat_contract': True}},
    )
    data = {'default_category': 'cargo'}
    response = await web_app_client.patch(
        '/v1/services/taxi',
        params={'client_id': 'client_id_1'},
        json=json_util.serialize(data),
    )
    assert response.status == 406


@pytest.mark.now(NOW.isoformat())
async def test_service_taxi_update_default_category_406(web_app_client):
    data = {'default_category': 'unknown'}

    response = await web_app_client.patch(
        '/v1/services/taxi',
        params={'client_id': 'client_id_1'},
        json=json_util.serialize(data),
    )
    response_json = await response.json()

    assert response.status == 406, response_json
    assert response_json['details']['reason'] == 'unknown is not allowed'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ('without_vat_contract', 'expected_tariff_plans'),
    [
        pytest.param(
            False,
            [
                {
                    'tariff_plan_series_id': 'tariff_plan_default',
                    'date_from': NOW,
                    'date_to': None,
                },
            ],
        ),
        pytest.param(
            False,
            [
                {
                    'tariff_plan_series_id': 'tariff_plan_promo',
                    'date_from': NOW,
                    'date_to': NOW + datetime.timedelta(hours=10),
                },
                {
                    'tariff_plan_series_id': 'tariff_plan_default',
                    'date_from': NOW + datetime.timedelta(hours=10),
                    'date_to': None,
                },
            ],
            marks=pytest.mark.config(
                CORP_PROMO_TARIFF_PLANS={
                    'rus': {
                        'tariff_plan_series_id': 'tariff_plan_promo',
                        'date_to': (
                            NOW + datetime.timedelta(hours=10)
                        ).isoformat(),
                    },
                },
            ),
        ),
        pytest.param(
            True,
            [
                {
                    'tariff_plan_series_id': 'tariff_plan_without_vat',
                    'date_from': NOW,
                    'date_to': None,
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    CORP_DEFAULT_TARIFF_PLANS={
        'rus': {'tariff_plan_series_id': 'tariff_plan_default'},
    },
    CORP_WITHOUT_VAT_TARIFF_PLANS={
        'rus': {
            'is_active': True,
            'tariff_plan_series_id': 'tariff_plan_without_vat',
        },
    },
)
@pytest.mark.translations(**test_utils.TRANSLATIONS)
async def test_service_taxi_update_assign_tariff_plans(
        db, web_app_client, without_vat_contract, expected_tariff_plans,
):
    await db.corp_clients.find_one_and_update(
        {'_id': 'client_id_2'},
        {'$set': {'without_vat_contract': without_vat_contract}},
    )
    data = {'is_active': True}

    response = await web_app_client.patch(
        '/v1/services/taxi',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )
    response_json = await response.json()
    assert response.status == 200, response_json

    client_tariff_plans = (
        await db.secondary.corp_client_tariff_plans.find(
            {'client_id': 'client_id_2'},
        )
        .sort('date_from')
        .to_list(None)
    )

    for client_tariff_plan in client_tariff_plans:
        assert client_tariff_plan.pop('_id')
        assert client_tariff_plan.pop('created')
        assert client_tariff_plan.pop('updated')
        assert client_tariff_plan.pop('client_id') == 'client_id_2'
        assert client_tariff_plan.pop('service') == 'taxi'

    assert client_tariff_plans == expected_tariff_plans


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_INITIAL_DEFAULT_CATEGORIES={
        '__default__': {'default_category': 'business'},
    },
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'root_geo_node': 'br_russia', 'default_language': 'ru'},
    },
)
@pytest.mark.translations(**test_utils.TRANSLATIONS)
async def test_service_taxi_update_assign_default_category(db, web_app_client):
    data = {'is_active': True}

    response = await web_app_client.patch(
        '/v1/services/taxi',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )
    response_json = await response.json()
    assert response.status == 200, response_json

    client_categories = await db.secondary.corp_client_categories.find(
        {'client_id': 'client_id_2'},
    ).to_list(None)

    updated = client_categories[0].pop('updated', None)
    assert isinstance(updated, datetime.datetime)

    for client_category in client_categories:
        assert client_category.pop('_id')
        assert client_category.pop('client_id') == 'client_id_2'
        assert client_category.pop('service') == 'taxi'

    assert client_categories == [
        {'categories': None, 'default_category': 'business'},
    ]


@pytest.mark.translations(**test_utils.TRANSLATIONS)
@pytest.mark.parametrize(
    ('without_vat_contract',), [pytest.param(True), pytest.param(False)],
)
@pytest.mark.config(
    CORP_DEFAULT_CATEGORIES={'rus': ['econom', 'comfort', 'cargo']},
    CORP_WITHOUT_VAT_DEFAULT_CATEGORIES={'rus': ['econom', 'comfort']},
)
async def test_service_taxi_default_limit(
        web_app_client, db, drive_mock, web_context, without_vat_contract,
):
    await db.corp_clients.find_one_and_update(
        {'_id': 'client_id_2'},
        {'$set': {'without_vat_contract': without_vat_contract}},
    )
    data: dict = {'is_active': True, 'is_visible': True}

    response = await web_app_client.patch(
        '/v1/services/taxi',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )

    assert response.status == 200

    taxi_limit = await db.corp_limits.find_one(
        {'client_id': 'client_id_2', 'service': 'taxi'},
        projection={'_id': False, 'created': False, 'updated': False},
    )
    assert taxi_limit == {
        'client_id': 'client_id_2',
        'title': 'Регулярные поездки',
        'name': 'Регулярные поездки',
        'department_id': None,
        'service': 'taxi',
        'is_default': True,
        'limits': {'orders_cost': None, 'orders_amount': None},
        'categories': (
            web_context.config.CORP_WITHOUT_VAT_DEFAULT_CATEGORIES['rus']
            if without_vat_contract
            else web_context.config.CORP_DEFAULT_CATEGORIES['rus']
        ),
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_DEFAULT_TARIFF_PLANS={
        'rus': {'tariff_plan_series_id': 'tariff_plan_default'},
    },
)
@pytest.mark.translations(**test_utils.TRANSLATIONS)
async def test_service_taxi_update_assign_home_zones(db, web_app_client):
    data = {'is_active': True}

    response = await web_app_client.patch(
        '/v1/services/taxi',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )
    response_json = await response.json()
    assert response.status == 200, response_json

    client_home_zones = await db.secondary.corp_client_roaming_zones.find_one(
        {'client_id': 'client_id_2'},
    )

    assert client_home_zones['zones'] == [{'name': 'br_tsentralnyj_fo'}]


@pytest.mark.now(NOW.isoformat())
async def test_service_without_vat_update(web_app_client, db):
    await db.corp_clients.find_one_and_update(
        {'_id': 'client_id_2'}, {'$set': {'without_vat_contract': True}},
    )
    data = {'is_active': True, 'is_visible': True, 'is_test': True}

    response = await web_app_client.patch(
        '/v1/services/taxi',
        params={'client_id': 'client_id_2'},
        json=json_util.serialize(data),
    )

    assert response.status == 400
    response_json = await response.json()
    assert response_json['details'] == {
        'reason': 'Forbid to make test without_vat client',
    }
