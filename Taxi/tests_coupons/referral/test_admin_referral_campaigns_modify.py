import pytest

from tests_coupons.referral import util


def get_campaign_by_id(db, campaign_id):
    return util.get_pg_records_as_dicts(
        f"""SELECT * FROM referral.campaigns
        WHERE id = {campaign_id}""",
        db,
    )[0]


def get_campaign_by_name(db, campaign_name):
    return util.get_pg_records_as_dicts(
        f"""SELECT * FROM referral.campaigns
        WHERE campaign_name = '{campaign_name}'""",
        db,
    )[0]


def get_campaigns_count(db):
    db.execute('SELECT COUNT(*) FROM referral.campaigns')
    record = list(db)[0]
    return record[0]


YANDEX_UID = {'X-Yandex-Uid': '75170007'}
TICKET = {'X-YaTaxi-Draft-Tickets': 'TAXIRATE-4'}

HEADERS = {'check': YANDEX_UID, 'apply': dict(YANDEX_UID, **TICKET)}

ADD_DATA = {
    'brand_name': 'yauber',
    'campaign_name': 'ba_uber',
    'descr': 'New uber campaign for BA',
    'series_template': 'brand',
    'status': 'by_experiment',
    'extra_check': 'business_account',
    'tanker_prefix': 'uber_new_ba',
}
EDIT_DATA = dict(ADD_DATA, **{'campaign_name': 'common_uber'})


def check_campaign_attrs(db, data):
    campaign = get_campaign_by_name(db, data['campaign_name'])
    campaign['descr'] = campaign.get('description')
    for key in data:
        assert campaign[key] == data[key], campaign


def check_response(response, case, data):
    assert (
        response['change_doc_id'] == f'{case}:campaign:{data["campaign_name"]}'
    )


@pytest.mark.parametrize(
    'data, expected_code',
    [
        pytest.param(
            {'campaign_name': 'common_uber'}, 400, id='campaign exists',
        ),
        pytest.param(
            {'extra_check': 'notexist'}, 400, id='extra_check does not exist',
        ),
        pytest.param({}, 200, id='ok data'),
    ],
)
@pytest.mark.parametrize('mode', ['check', 'apply'])
@pytest.mark.parametrize(
    'service, expected_service',
    [(None, 'taxi'), ('taxi', 'taxi'), ('grocery', 'grocery')],
)
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_campaigns_add(
        taxi_coupons,
        data,
        mode,
        expected_code,
        referrals_postgres_db,
        service,
        expected_service,
):
    count_before = get_campaigns_count(referrals_postgres_db)

    request_data = dict(ADD_DATA, **{**data, 'service': service})
    response = await taxi_coupons.post(
        f'/admin/referral/campaigns/add/{mode}',
        json=request_data,
        headers=HEADERS[mode],
    )
    assert response.status_code == expected_code

    if mode == 'check' and expected_code == 200:
        check_response(response.json(), 'add', request_data)

    count_after = get_campaigns_count(referrals_postgres_db)
    if mode == 'apply' and expected_code == 200:
        assert count_after == count_before + 1
        check_campaign_attrs(
            referrals_postgres_db,
            {**request_data, 'service': expected_service},
        )

    else:
        assert count_after == count_before


@pytest.mark.parametrize(
    'data, expected_code',
    [
        pytest.param(
            {'campaign_name': 'notexist'}, 404, id='campaign does not exist',
        ),
        pytest.param(
            {'extra_check': 'notexist'}, 400, id='extra_check does not exist',
        ),
        pytest.param({}, 200, id='ok data'),
    ],
)
@pytest.mark.parametrize('mode', ['check', 'apply'])
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_campaigns_edit(
        taxi_coupons, data, mode, expected_code, referrals_postgres_db,
):
    count_before = get_campaigns_count(referrals_postgres_db)

    request_data = dict(EDIT_DATA, **data)
    response = await taxi_coupons.post(
        f'/admin/referral/campaigns/edit/{mode}',
        json=request_data,
        headers=HEADERS[mode],
    )
    assert response.status_code == expected_code

    count_after = get_campaigns_count(referrals_postgres_db)
    assert count_after == count_before

    if mode == 'check' and expected_code == 200:
        check_response(response.json(), 'edit', request_data)

    if mode == 'apply' and expected_code == 200:
        check_campaign_attrs(referrals_postgres_db, request_data)


def check_lock_ids(response, ids):
    lock_ids = {
        f'edit:creator_config:{config_id}' for config_id in ids['creator']
    } | {f'edit:consumer_config:{config_id}' for config_id in ids['consumer']}
    assert set(lock_id['id'] for lock_id in response['lock_ids']) == lock_ids


DEL_CHANGED_FIELDS = {'updated_at', 'status', 'is_enabled'}


def check_configs(configs_before, configs_after, expected_ids):

    for config_before, config_after in zip(
            configs_before['creator'], configs_after['creator'],
    ):
        if config_before['id'] in expected_ids['creator']:
            assert config_before['status'] != 'disabled'
            assert config_after['status'] == 'disabled'
            for key in set(config_before) - DEL_CHANGED_FIELDS:
                assert config_before[key] == config_after[key]
        else:
            assert config_before == config_after

    for config_before, config_after in zip(
            configs_before['consumer'], configs_after['consumer'],
    ):
        if config_before['id'] in expected_ids['consumer']:
            assert config_before['is_enabled'] is True
            assert config_after['is_enabled'] is False
            for key in set(config_before) - DEL_CHANGED_FIELDS:
                assert config_before[key] == config_after[key]
        else:
            assert config_before == config_after


@pytest.mark.parametrize(
    'campaign_id, data, expected_code, expected_ids',
    [
        pytest.param(2, {}, 400, None, id='no geo specified'),
        pytest.param(
            2,
            {'country': 'rus', 'cities': ['Хьюстон']},
            400,
            None,
            id='difference in countries',
        ),
        pytest.param(
            5, {'cities': ['Самара']}, 400, None, id='extra config by country',
        ),
        pytest.param(
            3, {'cities': ['Хьюстон']}, 400, None, id='extra zones in config',
        ),
        pytest.param(
            5,
            {'country': 'rus'},
            200,
            {'creator': [18, 19], 'consumer': [8]},
            id='ok delete by country',
        ),
        pytest.param(
            3,
            {'cities': ['Чикаго', 'Хьюстон']},
            200,
            {'creator': [20], 'consumer': [7]},
            id='ok delete by zones',
        ),
    ],
)
@pytest.mark.parametrize('mode', ['check', 'apply'])
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_campaigns_delete(
        taxi_coupons,
        campaign_id,
        data,
        mode,
        expected_code,
        expected_ids,
        referrals_postgres_db,
):
    configs_before = {
        'creator': util.get_creator_configs(referrals_postgres_db),
        'consumer': util.get_consumer_configs(referrals_postgres_db),
    }
    campaign = get_campaign_by_id(referrals_postgres_db, campaign_id)

    request_data = dict({'campaign_name': campaign['campaign_name']}, **data)
    response = await taxi_coupons.post(
        f'/admin/referral/campaigns/delete/{mode}',
        json=request_data,
        headers=HEADERS[mode],
    )
    assert response.status_code == expected_code

    if mode == 'check' and expected_code == 200:
        response_json = response.json()
        check_response(response_json, 'del', request_data)
        check_lock_ids(response_json, expected_ids)

    if mode == 'apply' and expected_code == 200:
        configs_after = {
            'creator': util.get_creator_configs(referrals_postgres_db),
            'consumer': util.get_consumer_configs(referrals_postgres_db),
        }
        check_configs(configs_before, configs_after, expected_ids)
