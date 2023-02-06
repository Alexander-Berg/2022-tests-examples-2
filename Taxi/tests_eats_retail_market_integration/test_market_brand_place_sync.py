import pytest


MARKET_BRAND_PLACE_HANDLER = (
    '/mbi-api/eats-and-lavka/get-or-create/market-credentials'
)

PERIODIC_NAME = 'market-brand-place-sync-periodic'

ERROR_TYPE_WRONG_BUSINESS_ID_IN_DB = 1
ERROR_TYPE_DIFFERENT_BUSINESS_IDS_IN_FOR_ONE_BRAND = 2


@pytest.mark.pgsql('eats_retail_market_integration')
async def test(
        update_taxi_config,
        pg_cursor,
        pg_realdict_cursor,
        mockserver,
        taxi_eats_retail_market_integration,
        taxi_eats_retail_market_integration_monitor,
):
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_PERIODICS',
        {PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 60}},
    )

    old_brand_places = [
        {
            'brand_id': '5',
            'place_id': '51',
            'business_id': 105,
            'feed_id': 1051,
            'partner_id': 10051,
        },
        {
            'brand_id': '5',
            'place_id': '52',
            'business_id': 105,
            'feed_id': 1052,
            'partner_id': 10052,
        },
        {'brand_id': '5', 'place_id': '53'},
        {
            'brand_id': '6',
            'place_id': '61',
            'business_id': 106,
            'feed_id': 1061,
            'partner_id': 100611,
        },
        {'brand_id': '6', 'place_id': '62'},
    ]
    new_brand_places = [
        {
            'brand_id': '6',
            'place_id': '62',
            'business_id': 106,
            'feed_id': 1062,
            'partner_id': 10062,
        },
    ]

    old_brand_places_dict = {
        f'{i["brand_id"]}|{i["place_id"]}': i for i in old_brand_places
    }
    new_brand_places_dict = {
        f'{i["brand_id"]}|{i["place_id"]}': i for i in new_brand_places
    }

    def _has_market_ids(value):
        return all(
            field in value
            for field in ['business_id', 'feed_id', 'partner_id']
        )

    expected_brand_places_dict = {}
    expected_requested_keys = set()
    for key, old_value in old_brand_places_dict.items():
        # Fill expected brand places
        if key in new_brand_places_dict:
            expected_brand_places_dict[key] = new_brand_places_dict[key]
        elif _has_market_ids(old_value):
            expected_brand_places_dict[key] = old_value

        # Fill expected keys in requests
        if not _has_market_ids(old_value):
            expected_requested_keys.add(key)

    requested_keys = set()

    @mockserver.json_handler(MARKET_BRAND_PLACE_HANDLER)
    def _mock_mbi_mapping(request):
        j = request.json

        key = f'{j["service_id"][len("eats_"):]}|{j["eats_and_lavka_id"]}'
        requested_keys.add(key)

        if key not in new_brand_places_dict:
            return mockserver.make_response('Some error', 400)

        value = new_brand_places_dict[key]
        return {
            'business_id': value['business_id'],
            'partner_id': value['partner_id'],
            'market_feed_id': value['feed_id'],
        }

    _sql_set_brands(pg_cursor, list({i['brand_id'] for i in old_brand_places}))
    _sql_set_places(
        pg_cursor,
        list((i['place_id'], i['brand_id']) for i in old_brand_places),
    )
    _sql_set_market_brand_places(
        pg_cursor, [i for i in old_brand_places if _has_market_ids(i)],
    )

    await taxi_eats_retail_market_integration.run_distlock_task(PERIODIC_NAME)
    assert requested_keys == expected_requested_keys

    # Verify brand places

    sql_brand_places = _sql_get_market_brand_places(pg_realdict_cursor)
    sql_brand_places_dict = {
        f'{i["brand_id"]}|{i["place_id"]}': i for i in sql_brand_places
    }

    assert sql_brand_places_dict == expected_brand_places_dict

    metrics = await taxi_eats_retail_market_integration_monitor.get_metrics()
    periodic_metrics = metrics[PERIODIC_NAME]
    assert periodic_metrics['brands_with_wrong_business_id_count'] == 0


@pytest.mark.parametrize(
    'error_type',
    [
        pytest.param(ERROR_TYPE_DIFFERENT_BUSINESS_IDS_IN_FOR_ONE_BRAND),
        pytest.param(ERROR_TYPE_WRONG_BUSINESS_ID_IN_DB),
    ],
)
@pytest.mark.pgsql('eats_retail_market_integration')
async def test_errors(
        update_taxi_config,
        pg_cursor,
        pg_realdict_cursor,
        mockserver,
        taxi_eats_retail_market_integration,
        taxi_eats_retail_market_integration_monitor,
        error_type,
):
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_PERIODICS',
        {PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 60}},
    )

    old_brand_places = [
        {
            'brand_id': '5',
            'place_id': '51',
            'business_id': 105,
            'feed_id': 1051,
            'partner_id': 10051,
        },
        {
            'brand_id': '5',
            'place_id': '52',
            'business_id': 105,
            'feed_id': 1052,
            'partner_id': 10052,
        },
        {'brand_id': '5', 'place_id': '53'},
        {
            'brand_id': '6',
            'place_id': '61',
            'business_id': 106,
            'feed_id': 1061,
            'partner_id': 100611,
        },
        {'brand_id': '6', 'place_id': '62'},
    ]
    new_brand_places = [
        {
            'brand_id': '6',
            'place_id': '62',
            'business_id': 106,
            'feed_id': 1062,
            'partner_id': 10062,
        },
    ]

    if error_type == ERROR_TYPE_WRONG_BUSINESS_ID_IN_DB:
        new_brand_places.append(
            {
                'brand_id': '5',
                'place_id': '53',
                'business_id': 1055,
                'feed_id': 1053,
                'partner_id': 10053,
            },
        )

    if error_type == ERROR_TYPE_DIFFERENT_BUSINESS_IDS_IN_FOR_ONE_BRAND:
        new_brand_places.append(
            {
                'brand_id': '5',
                'place_id': '53',
                'business_id': 105,
                'feed_id': 1053,
                'partner_id': 10053,
            },
        )
        old_brand_places.append({'brand_id': '7', 'place_id': '71'})
        old_brand_places.append({'brand_id': '7', 'place_id': '72'})
        old_brand_places.append({'brand_id': '7', 'place_id': '73'})
        old_brand_places.append({'brand_id': '7', 'place_id': '74'})
        new_brand_places.append(
            {
                'brand_id': '7',
                'place_id': '71',
                'business_id': 107,
                'feed_id': 1071,
                'partner_id': 10071,
            },
        )
        new_brand_places.append(
            {
                'brand_id': '7',
                'place_id': '72',
                'business_id': 107,
                'feed_id': 1072,
                'partner_id': 10072,
            },
        )
        new_brand_places.append(
            {
                'brand_id': '7',
                'place_id': '73',
                'business_id': 1071,
                'feed_id': 1073,
                'partner_id': 10073,
            },
        )
        new_brand_places.append(
            {
                'brand_id': '7',
                'place_id': '74',
                'business_id': 1071,
                'feed_id': 1074,
                'partner_id': 10074,
            },
        )

    old_brand_places_dict = {
        f'{i["brand_id"]}|{i["place_id"]}': i for i in old_brand_places
    }
    new_brand_places_dict = {
        f'{i["brand_id"]}|{i["place_id"]}': i for i in new_brand_places
    }

    def _has_market_ids(value):
        return all(
            field in value
            for field in ['business_id', 'feed_id', 'partner_id']
        )

    expected_brand_places_dict = {}
    expected_requested_keys = set()
    for key, old_value in old_brand_places_dict.items():
        # Fill expected brand places
        if key in new_brand_places_dict:
            expected_brand_places_dict[key] = new_brand_places_dict[key]
        elif _has_market_ids(old_value):
            expected_brand_places_dict[key] = old_value

        # Fill expected keys in requests
        if not _has_market_ids(old_value):
            expected_requested_keys.add(key)

    requested_keys = []

    @mockserver.json_handler(MARKET_BRAND_PLACE_HANDLER)
    def _mock_mbi_mapping(request):
        j = request.json

        key = f'{j["service_id"][len("eats_"):]}|{j["eats_and_lavka_id"]}'
        requested_keys.append(key)

        if key not in new_brand_places_dict:
            return mockserver.make_response('Some error', 400)

        value = new_brand_places_dict[key]
        return {
            'business_id': value['business_id'],
            'partner_id': value['partner_id'],
            'market_feed_id': value['feed_id'],
        }

    _sql_set_brands(pg_cursor, list({i['brand_id'] for i in old_brand_places}))
    _sql_set_places(
        pg_cursor,
        list([i['place_id'], i['brand_id']] for i in old_brand_places),
    )
    _sql_set_market_brand_places(
        pg_cursor, [i for i in old_brand_places if _has_market_ids(i)],
    )

    await taxi_eats_retail_market_integration.run_distlock_task(PERIODIC_NAME)
    assert set(requested_keys) == expected_requested_keys

    # Verify brand places

    sql_brand_places = _sql_get_market_brand_places(pg_realdict_cursor)
    sql_brand_places_dict = {
        f'{i["brand_id"]}|{i["place_id"]}': i for i in sql_brand_places
    }

    if error_type == ERROR_TYPE_WRONG_BUSINESS_ID_IN_DB:
        expected_brand_places_dict.pop('5|53')

    if error_type == ERROR_TYPE_DIFFERENT_BUSINESS_IDS_IN_FOR_ONE_BRAND:
        for key in requested_keys:
            if key in ['7|71', '7|72']:
                expected_brand_places_dict.pop('7|73')
                expected_brand_places_dict.pop('7|74')
                break
            elif key in ['7|73', '7|74']:
                expected_brand_places_dict.pop('7|71')
                expected_brand_places_dict.pop('7|72')
                break

    assert sql_brand_places_dict == expected_brand_places_dict

    metrics = await taxi_eats_retail_market_integration_monitor.get_metrics()
    periodic_metrics = metrics[PERIODIC_NAME]

    if error_type == ERROR_TYPE_WRONG_BUSINESS_ID_IN_DB:
        assert periodic_metrics['brands_with_wrong_business_id_count'] == 1
    if error_type == ERROR_TYPE_DIFFERENT_BUSINESS_IDS_IN_FOR_ONE_BRAND:
        assert periodic_metrics['brands_with_wrong_business_id_count'] == 2


async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(MARKET_BRAND_PLACE_HANDLER)
    def _mock_mbp_mapping(request):
        return {}

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def sorted_by_place_id(places):
    return sorted(places, key=lambda item: item['place_id'])


def _sql_set_brands(pg_cursor, brand_ids):
    for brand_id in brand_ids:
        slug = 'brand' + brand_id
        pg_cursor.execute(
            f"""
            insert into eats_retail_market_integration.brands (id, slug)
            values ('{brand_id}', '{slug}')
            """,
        )


def _sql_set_places(pg_cursor, brand_places):
    for place_id, brand_id in brand_places:
        slug = 'place' + place_id
        pg_cursor.execute(
            f"""
            insert into eats_retail_market_integration.places (
                id, slug, brand_id
            )
            values(
                '{place_id}',
                '{slug}',
                '{brand_id}'
            )
            """,
        )


def _sql_set_market_brand_places(pg_cursor, brand_places):
    for i in brand_places:
        pg_cursor.execute(
            """
            insert into eats_retail_market_integration.market_brand_places (
                brand_id,
                place_id,
                business_id,
                partner_id,
                feed_id
            )
            values(
                %(brand_id)s,
                %(place_id)s,
                %(business_id)s,
                %(partner_id)s,
                %(feed_id)s
            )
            """,
            i,
        )


def _sql_get_market_brand_places(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select
            brand_id,
            place_id,
            business_id,
            partner_id,
            feed_id
        from eats_retail_market_integration.market_brand_places
        """,
    )
    return pg_realdict_cursor.fetchall()
