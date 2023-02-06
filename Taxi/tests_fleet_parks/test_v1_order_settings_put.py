import pytest

from tests_fleet_parks import utils

ENDPOINT = '/fleet/fleet-parks/v1/order-settings'

HEADERS = {
    'X-Ya-Service-Ticket': utils.SERVICE_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Ya-User-Ticket': utils.SERVICE_TICKET,
}


def record_without_changing_fields(rec):
    return {
        k: v
        for k, v in rec.items()
        if k
        not in [
            'updated_ts',
            'modified_date',
            'dispatch_requirement',
            'is_getting_orders_from_app',
            'auto_assign_preorders',
        ]
    }


@pytest.mark.config(
    FLEET_PARKS_DISPATCH_REQUIREMENT_TYPES={
        'default_type': 'only_source_park',
        'types_list': ['only_source_park', 'source_park_and_all'],
        'is_enabled': True,
    },
)
@pytest.mark.parametrize(
    'park_id, order_settings',
    [
        (
            'park_id1',
            {
                'dispatch_requirement': 'source_park_and_all',
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': True,
            },
        ),
        (
            'park_id2',
            {
                'dispatch_requirement': 'source_park_and_all',
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': True,
            },
        ),
        (
            'park_id3',
            {
                'dispatch_requirement': 'only_source_park',
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': False,
            },
        ),
        (
            'park_id4',
            {
                'dispatch_requirement': 'only_source_park',
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': False,
            },
        ),
        (
            'park_id_none_dispatch_requirement1',
            {
                'dispatch_requirement': 'only_source_park',
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': False,
            },
        ),
        (
            'park_id_none_dispatch_requirement2',
            {
                'dispatch_requirement': 'only_source_park',
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': False,
            },
        ),
    ],
)
async def test_ok_dispatch_requirement_enabled(
        taxi_fleet_parks, mongodb, park_id, order_settings,
):
    headers = HEADERS
    headers['X-Park-ID'] = park_id

    park_doc_before = mongodb.dbparks.find_one({'_id': park_id})

    response = await taxi_fleet_parks.put(
        ENDPOINT, json=order_settings, headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == order_settings

    park_doc_after = mongodb.dbparks.find_one({'_id': park_id})

    assert park_doc_after['updated_ts'] > park_doc_before['updated_ts']
    assert park_doc_after['modified_date'] > park_doc_before['modified_date']
    assert (
        park_doc_after['dispatch_requirement']
        == order_settings['dispatch_requirement']
    )
    assert (
        park_doc_after['is_getting_orders_from_app']
        == order_settings['is_getting_orders_from_app']
    )
    assert (
        park_doc_after['auto_assign_preorders']
        == order_settings['auto_assign_preorders']
    )
    assert record_without_changing_fields(
        park_doc_after,
    ) == record_without_changing_fields(park_doc_before)


@pytest.mark.config(
    FLEET_PARKS_DISPATCH_REQUIREMENT_TYPES={
        'default_type': 'only_source_park',
        'types_list': ['only_source_park', 'source_park_and_all'],
        'is_enabled': False,
    },
)
@pytest.mark.parametrize(
    'park_id, order_settings',
    [
        (
            'park_id1',
            {
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': True,
            },
        ),
        (
            'park_id2',
            {
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': True,
            },
        ),
        (
            'park_id_none_dispatch_requirement1',
            {
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': False,
            },
        ),
        (
            'park_id_none_dispatch_requirement2',
            {
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': False,
            },
        ),
    ],
)
async def test_ok_dispatch_requirement_disabled(
        taxi_fleet_parks, mongodb, park_id, order_settings,
):
    headers = HEADERS
    headers['X-Park-ID'] = park_id

    park_doc_before = mongodb.dbparks.find_one({'_id': park_id})

    response = await taxi_fleet_parks.put(
        ENDPOINT, json=order_settings, headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == order_settings

    park_doc_after = mongodb.dbparks.find_one({'_id': park_id})

    assert park_doc_after['updated_ts'] > park_doc_before['updated_ts']
    assert park_doc_after['modified_date'] > park_doc_before['modified_date']
    assert (
        (
            'dispatch_requirement' not in park_doc_after
            and 'dispatch_requirement' not in park_doc_before
        )
        or park_doc_after['dispatch_requirement']
        == park_doc_before['dispatch_requirement']
    )
    assert (
        park_doc_after['is_getting_orders_from_app']
        == order_settings['is_getting_orders_from_app']
    )
    assert (
        park_doc_after['auto_assign_preorders']
        == order_settings['auto_assign_preorders']
    )
    assert record_without_changing_fields(
        park_doc_after,
    ) == record_without_changing_fields(park_doc_before)


@pytest.mark.config(
    FLEET_PARKS_DISPATCH_REQUIREMENT_TYPES={
        'default_type': 'only_source_park',
        'types_list': ['only_source_park', 'source_park_and_all'],
        'is_enabled': False,
    },
)
async def test_failed_dispatch_requirement_disabled(taxi_fleet_parks, mongodb):
    park_id = 'park_id1'
    headers = HEADERS
    headers['X-Park-ID'] = park_id

    park_doc_before = mongodb.dbparks.find_one({'_id': park_id})

    order_settings = {
        'dispatch_requirement': 'source_park_and_all',
        'is_getting_orders_from_app': False,
        'auto_assign_preorders': False,
    }
    response = await taxi_fleet_parks.put(
        ENDPOINT, json=order_settings, headers=headers,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'DISPATCH_REQUIREMENTS_DISABLED',
        'message': 'Dispatch requirements is disabled',
    }

    park_doc_after = mongodb.dbparks.find_one({'_id': park_id})

    assert park_doc_after == park_doc_before


async def test_failed_not_saas_park(taxi_fleet_parks, mongodb):
    park_id = 'park_id_not_saas'
    headers = HEADERS
    headers['X-Park-ID'] = park_id

    park_doc_before = mongodb.dbparks.find_one({'_id': park_id})

    order_settings = {
        'dispatch_requirement': 'source_park_and_all',
        'is_getting_orders_from_app': False,
        'auto_assign_preorders': False,
    }
    response = await taxi_fleet_parks.put(
        ENDPOINT, json=order_settings, headers=headers,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'NOT_SAAS_PARK',
        'message': 'Not a saas park, park_id: park_id_not_saas',
    }

    park_doc_after = mongodb.dbparks.find_one({'_id': park_id})

    assert park_doc_after == park_doc_before


async def test_failed_park_not_found(taxi_fleet_parks, mongodb):
    park_id = 'non_existing_park_id'
    headers = HEADERS
    headers['X-Park-ID'] = park_id

    park_doc_before = mongodb.dbparks.find_one({'_id': park_id})

    order_settings = {
        'dispatch_requirement': 'source_park_and_all',
        'is_getting_orders_from_app': False,
        'auto_assign_preorders': False,
    }
    response = await taxi_fleet_parks.put(
        ENDPOINT, json=order_settings, headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'PARK_NOT_FOUND',
        'message': 'No park found for park_id non_existing_park_id',
    }

    park_doc_after = mongodb.dbparks.find_one({'_id': park_id})

    assert park_doc_after == park_doc_before
