import pytest


YANDEX_UID = 'any_uid'
PHONE_ID = 'any_phone_id'

ADD_FOODTECH_REF_PROMO = (
    'INSERT INTO referral.external_referral_creators'
    '(referral_name, yandex_uid, phone_id, zone_name, promocode)'
    'VALUES'
    '(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\');'
)

ADD_TAXI_REF_PROMO = (
    'INSERT INTO referral.promocodes'
    '(yandex_uid, promocode, country, config_id, phone_id, campaign_id)'
    'VALUES'
    '(\'{}\', \'{}\', \'rus\', {}, \'{}\', {});'
)

MOSCOW_CONFIG_BY_CAMPAIGN = {0: 1, 1: 16}


async def make_request(
        taxi_coupons,
        zone_name,
        phone_id,
        yandex_uid,
        app_version='0.0.0',
        app_name='android',
):
    versions = enumerate(app_version.split('.'), 1)
    params_list = [f'app_ver{num}={version}' for num, version in versions]
    params_list += [f'app_name={app_name}', 'app_brand=yataxi']

    headers = {
        'X-Request-Application': ','.join(params_list),
        'X-Request-Language': 'en',
    }
    headers.update({'X-YaTaxi-PhoneId': phone_id} if phone_id else {})
    headers.update({'X-Yandex-UID': yandex_uid} if yandex_uid else {})

    response = await taxi_coupons.post(
        '/v1/shortcuts', json={'zone_name': zone_name}, headers=headers,
    )
    return response


def make_content(referral_service, full_content, coupon):
    deep_link = '_' + referral_service if referral_service != 'taxi' else ''
    deep_link += f'?promocode={coupon}'
    content_template = {
        'content': {'title': f'Shortcut title {referral_service}'},
        'id': f'referral-{referral_service}-',
        'scenario': 'referral',
        'scenario_params': {
            'referral_params': {
                'deeplink': f'yandextaxi://referral{deep_link}',
            },
        },
    }
    if full_content:
        content_template['content'].update(
            {
                'color': f'{referral_service}_color_code',
                'image_tag': f'{referral_service}_some_image_tag',
                'subtitle': f'Shortcut subtitle {referral_service}',
                'text_color': f'{referral_service}_text_color_code',
            },
        )
    return content_template


def create_expected_response(
        is_taxi_referral_zone,
        grocery_coupon,
        grocery_experiment,
        full_content,
        taxi_coupons_list,
        old_app=False,
):

    response = {'scenario_tops': []}
    if (not is_taxi_referral_zone or not taxi_coupons_list) and (
            not grocery_coupon or not grocery_experiment
    ):
        return response

    response['scenario_tops'].append({'scenario': 'referral', 'shortcuts': []})

    if grocery_coupon and grocery_experiment:
        content = make_content('grocery', full_content, grocery_coupon)
        response['scenario_tops'][0]['shortcuts'].append(content)

    if is_taxi_referral_zone and taxi_coupons_list:
        for coupon in taxi_coupons_list:
            content = make_content('taxi', full_content, coupon)
            response['scenario_tops'][0]['shortcuts'].append(content)

    if old_app:
        response['scenario_tops'][0]['shortcuts'] = [
            response['scenario_tops'][0]['shortcuts'][-1].copy(),
        ]

    return response


def compare_responses(response_json, expected_response_json):
    if expected_response_json['scenario_tops']:
        resp_shortcuts = response_json['scenario_tops'][0]['shortcuts']
        exp_shortcuts = expected_response_json['scenario_tops'][0]['shortcuts']

        for resp, expected in zip(resp_shortcuts, exp_shortcuts):
            assert resp['id'].startswith(expected['id'])
            resp['id'] = expected['id'] = '...'

    assert response_json == expected_response_json


def fill_data(
        user_statistics_services,
        referrals_postgres_db,
        taxi_coupons_list,
        phone_id=PHONE_ID,
        grocery_zone=None,
        grocery_coupon=None,
):
    if grocery_coupon:
        referrals_postgres_db.execute(
            ADD_FOODTECH_REF_PROMO.format(
                'grocery', YANDEX_UID, phone_id, grocery_zone, grocery_coupon,
            ),
        )
    for coupon in taxi_coupons_list:
        campaign_id = int('business' in coupon)
        config_id = MOSCOW_CONFIG_BY_CAMPAIGN[campaign_id]
        referrals_postgres_db.execute(
            ADD_TAXI_REF_PROMO.format(
                YANDEX_UID, coupon, config_id, phone_id, campaign_id,
            ),
        )

    user_statistics_services.set_phone_id(phone_id)


@pytest.mark.experiments3(
    filename='referral_campaign_light_business_experiments3.json',
)
@pytest.mark.experiments3(filename='external_referral_experiments3.json')
@pytest.mark.experiments3(filename='shortcut_experiments3.json')
@pytest.mark.parametrize(
    'grocery_coupon, grocery_zone',
    [
        pytest.param(
            'grocery_ref_promo', 'moscow', id='grocery_coupon_moscow exist',
        ),
        pytest.param(
            'grocery_ref_promo_usa', 'houston', id='grocery_coupon_usa exist',
        ),
        pytest.param(None, None, id='grocery_coupon doesn\'t exist'),
    ],
)
@pytest.mark.parametrize(
    'taxi_coupons_list',
    [
        pytest.param(
            ['taxi_ref_promo', 'taxi_ref_business'], id='several refs exist',
        ),
        pytest.param(['taxi_ref_promo'], id='common_taxi exist'),
        pytest.param(['taxi_ref_business'], id='light_business exist'),
        pytest.param([], id='taxi_coupon doesn\'t exist'),
    ],
)
@pytest.mark.parametrize(
    'zone_name, is_taxi_referral_zone',
    [
        pytest.param('moscow', True, id='taxi_referral_enable'),
        pytest.param('houston', True, id='taxi_referral_enable_usa'),
        pytest.param('samara', False, id='taxi_referral_disable'),
        pytest.param(
            'samara',
            True,
            marks=pytest.mark.experiments3(
                filename='referral_taxi_check_db_first_exp3.json',
            ),
            id='taxi_referral_check_db_first',
        ),
    ],
)
@pytest.mark.parametrize(
    'phone_id, full_content',
    [
        pytest.param('0', False, id='minmal_content'),
        pytest.param('1', True, id='full_content'),
    ],
)
@pytest.mark.parametrize(
    'app_name, app_version, old_app',
    [
        pytest.param(
            'android',
            '1.1.1',
            False,
            marks=pytest.mark.config(
                COUPONS_MULTIPLE_SHORTCUTS_MIN_VERSIONS={},
            ),
            id='empty_config',
        ),
        pytest.param(
            'iphone',
            '1.1.1',
            True,
            marks=pytest.mark.config(
                COUPONS_MULTIPLE_SHORTCUTS_MIN_VERSIONS={'iphone': '1.1.2'},
            ),
            id='old_app',
        ),
        pytest.param(
            'iphone',
            '1.1.1',
            False,
            marks=pytest.mark.config(
                COUPONS_MULTIPLE_SHORTCUTS_MIN_VERSIONS={'iphone': '1.1.0'},
            ),
            id='new_app',
        ),
    ],
)
async def test_shortcuts_main(
        taxi_coupons,
        user_statistics_services,
        phone_id,
        zone_name,
        is_taxi_referral_zone,
        full_content,
        app_name,
        app_version,
        old_app,
        taxi_coupons_list,
        grocery_coupon,
        referrals_postgres_db,
        grocery_zone,
):
    fill_data(
        user_statistics_services,
        referrals_postgres_db,
        taxi_coupons_list,
        phone_id,
        grocery_zone,
        grocery_coupon,
    )

    response = await make_request(
        taxi_coupons, zone_name, phone_id, YANDEX_UID, app_version, app_name,
    )
    assert response.status_code == 200

    response_json = response.json()
    expected_response_json = create_expected_response(
        is_taxi_referral_zone,
        grocery_coupon,
        True,
        full_content,
        taxi_coupons_list,
        old_app,
    )

    compare_responses(response_json, expected_response_json)


@pytest.mark.experiments3(filename='shortcut_experiments3.json')
@pytest.mark.parametrize(
    'taxi_coupons_list',
    [
        pytest.param(['taxi_ref_promo'], id='taxi_coupon exist'),
        pytest.param([], id='taxi_coupon doesn\'t exist'),
    ],
)
@pytest.mark.parametrize(
    'grocery_coupon, grocery_zone',
    [
        pytest.param(
            'grocery_ref_promo', 'astana', id='grocery_coupon_moscow exist',
        ),
        pytest.param(
            'grocery_ref_promo_usa', 'houston', id='grocery_coupon_usa exist',
        ),
        pytest.param(None, None, id='grocery_coupon doesn\'t exist'),
    ],
)
@pytest.mark.parametrize(
    'zone_name, is_taxi_referral_zone',
    [
        pytest.param('moscow', True, id='taxi_referral_enable'),
        pytest.param('houston', True, id='taxi_referral_enable_usa'),
        pytest.param('astana', False, id='taxi_referral_disable'),
    ],
)
@pytest.mark.parametrize(
    'grocery_experiment', [pytest.param(False, id='grocery_experiment_off')],
)
async def test_shortcuts_experiment_off(
        taxi_coupons,
        user_statistics_services,
        zone_name,
        is_taxi_referral_zone,
        grocery_coupon,
        grocery_zone,
        grocery_experiment,
        taxi_coupons_list,
        referrals_postgres_db,
):

    fill_data(
        user_statistics_services,
        referrals_postgres_db,
        taxi_coupons_list,
        PHONE_ID,
        grocery_zone,
        grocery_coupon,
    )

    response = await make_request(
        taxi_coupons, zone_name, PHONE_ID, YANDEX_UID,
    )
    assert response.status_code == 200
    expected_response_json = create_expected_response(
        is_taxi_referral_zone,
        grocery_coupon,
        grocery_experiment,
        True,
        taxi_coupons_list,
    )

    compare_responses(response.json(), expected_response_json)


@pytest.mark.experiments3(filename='external_referral_experiments3.json')
@pytest.mark.experiments3(filename='shortcut_experiments3.json')
@pytest.mark.parametrize('zone_name', ['moscow', None])
@pytest.mark.parametrize('phone_id', [PHONE_ID, None])
@pytest.mark.parametrize('yandex_uid', [YANDEX_UID, None])
async def test_shortcuts_unauthorized_and_empty_required_fields(
        taxi_coupons,
        user_statistics_services,
        referrals_postgres_db,
        zone_name,
        phone_id,
        yandex_uid,
):
    fill_data(
        user_statistics_services,
        referrals_postgres_db,
        taxi_coupons_list=['taxi_ref_promo'],
        phone_id=PHONE_ID,
        grocery_coupon='grocery_ref_promo',
        grocery_zone='moscow',
    )
    response = await make_request(
        taxi_coupons, zone_name, phone_id, yandex_uid,
    )

    assert response.status_code == 200

    expect_empty_resonse = not all([zone_name, phone_id, yandex_uid])
    empty_scenarios = {'scenario_tops': []}
    if expect_empty_resonse:
        assert response.json() == empty_scenarios
    else:
        assert response.json() != empty_scenarios
