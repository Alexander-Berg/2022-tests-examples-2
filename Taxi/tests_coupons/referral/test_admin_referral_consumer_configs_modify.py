import pytest

from tests_coupons.referral import util


def get_consumer_configs_count(db):
    db.execute('SELECT COUNT(*) FROM referral.consumer_configs')
    record = list(db)[0]
    return record[0]


YANDEX_UID = {'X-Yandex-Uid': '75170007'}
TICKET = {'X-YaTaxi-Draft-Tickets': 'TAXIRATE-4'}

HEADERS = {'check': YANDEX_UID, 'apply': dict(YANDEX_UID, **TICKET)}

ADD_DATA = {
    'campaign_name': 'common_taxi',
    'country': 'rus',
    'cities': ['Самара'],
    'status': 'enabled',
    'duration_days': 30,
    'series': {'series_template': 'custom', 'series_id': 'referral'},
}


BRAND_SERIES = {
    'series_template': 'brand',
    'value': 123,
    'user_limit': 3,
    'percent': 25,
    'creditcard_only': True,
}


def check_response(response, case, data):
    change_doc_id = response['change_doc_id']

    if case == 'edit':
        assert change_doc_id == f'edit:consumer_config:{data["config_id"]}'
        assert response['lock_ids'] == [{'id': change_doc_id, 'custom': True}]
    else:
        assert change_doc_id.startswith('add:consumer_config:')


def perform_consumer_apply_checks(
        postgres_db, mongodb, count_before, request_data, force_change=None,
):
    count_after = get_consumer_configs_count(postgres_db)
    assert count_after == count_before + (0 if force_change else 1)

    configs_after_list = util.get_consumer_configs(postgres_db)
    config = configs_after_list[
        request_data['config_id'] - 1 if force_change else -1
    ]
    if request_data['series']['series_template'] == 'brand':
        doc = mongodb.promocode_series.find_one({'_id': config['series_id']})

        assert doc.get('cities', []) == request_data.get('cities', [])

        for key in ('value', 'percent', 'user_limit', 'creditcard_only'):
            assert doc.get(key) == request_data['series'].get(key)

    if force_change is False:  # for edit case only
        old_config = configs_after_list[request_data['config_id'] - 1]
        assert not old_config['is_enabled']


@pytest.mark.parametrize(
    'data, expected_code',
    [
        pytest.param(
            {'campaign_name': 'notexist'}, 404, id='campaign does not exist',
        ),
        pytest.param(
            {'series': {'series_template': 'custom', 'series_id': 'notexist'}},
            404,
            id='series does not exist',
        ),
        pytest.param(
            {
                'series': {
                    'series_template': 'custom',
                    'series_id': 'secondpromocode',
                },
            },
            400,
            id='series is not unique',
        ),
        pytest.param(
            {'cities': None, 'country': None}, 400, id='no geo specified',
        ),
        pytest.param(
            {'cities': ['Хьюстон']}, 400, id='difference in countries',
        ),
        pytest.param({'cities': ['Москва']}, 400, id='geo intersection'),
        pytest.param({}, 200, id='ok data'),
    ],
)
@pytest.mark.parametrize('mode', ['check', 'apply'])
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_consumer_configs_add_check(
        taxi_coupons, data, mode, expected_code,
):
    request_data = dict(ADD_DATA, **data)
    response = await taxi_coupons.post(
        f'/admin/referral/consumer_configs/add/{mode}',
        json=request_data,
        headers=HEADERS[mode],
    )
    assert response.status_code == expected_code

    if mode == 'check' and expected_code == 200:
        check_response(response.json(), 'add', request_data)


@pytest.mark.parametrize(
    'data, expected_campaign_id',
    [
        pytest.param({}, 0, id='custom series'),
        pytest.param(
            {'campaign_name': 'common_uber', 'series': BRAND_SERIES},
            4,
            id='brand series',
        ),
    ],
)
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_consumer_configs_add_apply(
        taxi_coupons,
        data,
        expected_campaign_id,
        referrals_postgres_db,
        mongodb,
        tariffs,
):
    count_before = get_consumer_configs_count(referrals_postgres_db)

    request_data = dict(ADD_DATA, **data)
    response = await taxi_coupons.post(
        '/admin/referral/consumer_configs/add/apply',
        json=request_data,
        headers=HEADERS['apply'],
    )
    assert response.status_code == 200

    perform_consumer_apply_checks(
        referrals_postgres_db, mongodb, count_before, request_data,
    )


EDIT_DATA = dict(ADD_DATA, **{'cities': ['Москва']})


@pytest.mark.parametrize(
    'data, expected_code',
    [
        pytest.param({'config_id': 0}, 404, id='config does not exist'),
        pytest.param(
            {'config_id': 1, 'campaign_name': 'common_yango'},
            400,
            id='wrong config campaign',
        ),
        pytest.param({'config_id': 2}, 400, id='geo intersection'),
        pytest.param({'config_id': 1}, 200, id='ok data'),
    ],
)
@pytest.mark.parametrize('force_change', [True, False])
@pytest.mark.parametrize('mode', ['check', 'apply'])
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_consumer_configs_edit_check(
        taxi_coupons, data, force_change, mode, expected_code,
):
    request_data = dict(EDIT_DATA, **data, **{'force_change': force_change})
    response = await taxi_coupons.post(
        f'/admin/referral/consumer_configs/edit/{mode}',
        json=request_data,
        headers=HEADERS[mode],
    )
    assert response.status_code == expected_code

    if mode == 'check' and expected_code == 200:
        check_response(response.json(), 'edit', request_data)


@pytest.mark.parametrize(
    'data',
    [
        pytest.param({'config_id': 1}, id='duration changes'),
        pytest.param(
            {
                'config_id': 1,
                'series': {
                    'series_template': 'custom',
                    'series_id': 'seriespptreferral',
                },
            },
            id='custom series changes',
        ),
        pytest.param(
            {
                'config_id': 5,
                'campaign_name': 'common_uber',
                'series': BRAND_SERIES,
            },
            id='brand series changes',
        ),
    ],
)
@pytest.mark.parametrize('force_change', [True, False])
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_consumer_configs_edit_apply(
        taxi_coupons,
        data,
        force_change,
        referrals_postgres_db,
        mongodb,
        tariffs,
):
    count_before = get_consumer_configs_count(referrals_postgres_db)

    request_data = dict(EDIT_DATA, **data, **{'force_change': force_change})
    response = await taxi_coupons.post(
        '/admin/referral/consumer_configs/edit/apply',
        json=request_data,
        headers=HEADERS['apply'],
    )
    assert response.status_code == 200

    perform_consumer_apply_checks(
        referrals_postgres_db,
        mongodb,
        count_before,
        request_data,
        force_change,
    )
