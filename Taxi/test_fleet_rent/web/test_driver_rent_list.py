import pytest

from fleet_rent.entities import park as park_entities


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.affiliations
    (record_id, state,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz)
    VALUES
    ('affiliation_id', 'new',
     'park_id', 'park_driver_id',
     'driver_park_id', 'driver_id',
     'creator_uid', '2020-01-01+00')
        """,
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     owner_park_id, owner_serial_id,
     asset_type, asset_params,
     driver_id,
     affiliation_id,
     begins_at_tz, ends_at_tz,
     charging_type,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz,
     transfer_order_number)
    VALUES ('record_id1', 'idempotency_token1',
     'park_id', 1,
     'other', '{"subtype": "misc"}',
     'park_driver_id',
     'affiliation_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00',
     'park_id_1'),
     ('record_id2', 'idempotency_token2',
     'park_id', 2,
     'other', '{"subtype": "misc"}',
     'park_driver_id',
     'affiliation_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     NULL,
     'park_id_2'),
     ('record_id3', 'idempotency_token3',
     'park_id', 3,
     'other', '{"subtype": "misc"}',
     'park_driver_id',
     'affiliation_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00',
     'park_id_3'),
     ('record_id4', 'idempotency_token4',
     'park_id', 4,
     'other', '{"subtype": "misc"}',
     'park_driver_id',
     'affiliation_id',
     '2020-01-01+00', '2020-01-10+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00',
     'park_id_4')
        """,
    ],
)
@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'rent_record_list_title.active': {'ru': 'Активные списания'},
        'rent_name': {'ru': 'Списание №{id}'},
        'Park "{park_name}"': {'ru': 'Парк "{park_name}"'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
@pytest.mark.now('2020-01-20T00:00:00')
async def test_selections(web_app_client, driver_auth_headers, patch):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info_b(park_id: str):
        return park_entities.Park(
            id=park_id, name='park name', clid='clid', owner=None, tz_offset=3,
        )

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/list',
        params={'selection': 'active'},
        headers=driver_auth_headers,
        json={'limit': 1},
    )
    assert response.status == 200
    data = await response.json()
    cursor = data.pop('cursor')
    assert data == {
        'title': 'Активные списания',
        'items': [
            {
                'type': 'detail',
                'payload': {
                    'type': 'navigate_rent_details',
                    'rent_id': 'record_id3',
                },
                'horizontal_divider_type': 'bottom_gap',
                'title': 'Списание №3',
                'subtitle': 'Парк "park name"',
                'right_icon': 'navigate',
            },
        ],
    }

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/rent/list',
        params={'selection': 'active'},
        headers=driver_auth_headers,
        json={'limit': 1, 'cursor': cursor},
    )
    assert response.status == 200
    data = await response.json()
    assert data == {
        'title': 'Активные списания',
        'items': [
            {
                'type': 'detail',
                'payload': {
                    'type': 'navigate_rent_details',
                    'rent_id': 'record_id1',
                },
                'horizontal_divider_type': 'bottom_gap',
                'title': 'Списание №1',
                'subtitle': 'Парк "park name"',
                'right_icon': 'navigate',
            },
        ],
    }
