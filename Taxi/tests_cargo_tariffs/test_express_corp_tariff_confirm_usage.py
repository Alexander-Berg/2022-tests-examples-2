import pytest


TARIFF_ID = 'tariff_id'
CATEGORY_NAME = 'category_name'
CARGO_TARIFF_ID = 'cargo-tariffs/v1/' + TARIFF_ID + '-' + CATEGORY_NAME


def _get_tariff_categories():
    return [
        {
            'add_minimal_to_paid_cancel': True,
            'category_name': 'econom',
            'category_name_key': 'name.econom',
            'category_type': 'application',
            'currency': 'RUB',
            'day_type': 2,
            'disable_surge': False,
            'id': '05156a5d865a429a960ddb4dde20e736',
            'included_one_of': [],
            'meters': [
                {'prepaid': 0, 'trigger': 3},
                {'prepaid': 0, 'trigger': 3},
                {'prepaid': 0, 'trigger': 3},
            ],
            'minimal': 89,
            'name_key': 'interval.always',
            'paid_cancel_fix': 0,
            'special_taximeters': [
                {
                    'price': {
                        'distance_price_intervals': [{'begin': 3, 'price': 8}],
                        'distance_price_intervals_meter_id': 6,
                        'time_price_intervals': [{'begin': 5, 'price': 13}],
                        'time_price_intervals_meter_id': 5,
                    },
                    'zone_name': 'suburb',
                },
                {
                    'price': {
                        'distance_price_intervals': [{'begin': 3, 'price': 7}],
                        'distance_price_intervals_meter_id': 6,
                        'time_price_intervals': [{'begin': 5, 'price': 12}],
                        'time_price_intervals_meter_id': 5,
                    },
                    'zone_name': 'spb',
                },
            ],
            'summable_requirements': [{'max_price': 0, 'type': 'nosmoking'}],
            'time_from': '00:00',
            'time_to': '23:59',
            'waiting_included': 3,
            'waiting_price': 9,
            'waiting_price_type': 'per_minute',
            'zonal_prices': [
                {
                    'destination': 'dme',
                    'price': {
                        'distance_price_intervals': [
                            {'begin': 10, 'price': 6},
                        ],
                        'distance_price_intervals_meter_id': 6,
                        'once': 449,
                        'time_price_intervals': [{'begin': 15, 'price': 6}],
                        'time_price_intervals_meter_id': 5,
                        'waiting_included': 5,
                        'waiting_price': 7,
                    },
                    'route_without_jams': False,
                    'source': 'spb',
                },
            ],
        },
    ]


def _get_tariff_response():
    return {
        'tariff': {
            'id': '5caeed9d1bc8d21af5a07a24',
            'home_zone': 'moscow',
            'categories': _get_tariff_categories(),
        },
        'disable_paid_supply_price': False,
        'disable_fixed_price': False,
    }


@pytest.fixture(name='mock_corp_tariffs_v1_tariff')
def _mock_corp_tariffs_v1_tariff(mockserver):
    class Context:
        request = {}
        mock = None
        response = _get_tariff_response()

    ctx = Context()

    @mockserver.json_handler('/corp-tariffs/v1/tariff')
    def _mock(request):
        ctx.request = request.query
        return mockserver.make_response(json=ctx.response, status=200)

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='call_tariff_confirm_usage')
def _call_tariff_confirm_usage(taxi_cargo_tariffs):
    async def call():
        response = await taxi_cargo_tariffs.post(
            '/cargo-tariffs/express/v1/corp-tariff-confirm-usage',
            json={'id': TARIFF_ID, 'category': CATEGORY_NAME},
        )
        return response

    return call


@pytest.fixture(name='get_tariffs_from_db')
def _get_tariffs_from_db(pgsql):
    def get():
        cursor = pgsql['cargo_tariffs'].conn.cursor()
        cursor.execute(
            f"""
            SELECT id, pricing_schedule, composer_process, service
            FROM cargo_tariffs.tariff_compositions
            WHERE id='{CARGO_TARIFF_ID}'
            """,
        )
        return list(cursor)

    return get


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_express_corp_tariff_confirm_usage(
        mock_corp_tariffs_v1_tariff,
        call_tariff_confirm_usage,
        get_tariffs_from_db,
):
    response = await call_tariff_confirm_usage()
    assert response.status_code == 200

    db_tariffs = get_tariffs_from_db()
    assert len(db_tariffs) == 1
    db_tariff_id, tariff, composer_process, service = db_tariffs[0]
    assert db_tariff_id == CARGO_TARIFF_ID
    assert tariff == _get_tariff_response()
    assert composer_process == {
        'tariff_nodes': [TARIFF_ID + '-' + CATEGORY_NAME],
    }
    assert service == 'express'


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_express_corp_tariff_confirm_usage_existing_tariff(
        mock_corp_tariffs_v1_tariff,
        call_tariff_confirm_usage,
        get_tariffs_from_db,
):
    response1 = await call_tariff_confirm_usage()
    assert response1.status_code == 200

    mock_corp_tariffs_v1_tariff.response['tariff']['home_zone'] = 'spb'
    response2 = await call_tariff_confirm_usage()
    assert response2.status_code == 200

    db_tariffs = get_tariffs_from_db()
    assert len(db_tariffs) == 1
    db_tariff_id, tariff, _, _ = db_tariffs[0]
    assert db_tariff_id == CARGO_TARIFF_ID
    assert tariff == _get_tariff_response()


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_express_corp_tariff_confirm_usage_v1_tariff_response(
        mock_corp_tariffs_v1_tariff, call_tariff_confirm_usage,
):
    response1 = await call_tariff_confirm_usage()
    assert response1.status_code == 200

    assert mock_corp_tariffs_v1_tariff.mock.times_called == 1
    assert mock_corp_tariffs_v1_tariff.request == {
        'id': TARIFF_ID,
        'categories': CATEGORY_NAME,
    }
