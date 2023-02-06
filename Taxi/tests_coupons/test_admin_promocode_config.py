import enum

import pytest


def check_unique_promocode(promocode_json, mongodb):
    promocode = list(
        mongodb.promocodes.find({'code': promocode_json['code']}),
    )[0]
    assert promocode.get('expire_at') and promocode_json.get('expire_at')
    if promocode.get('revoked'):
        assert promocode_json.get('revoked')
        assert (
            promocode['revoked']['created']
            and promocode_json['revoked']['created']
        )
        assert (
            promocode['revoked']['operator_login']
            == promocode_json['revoked']['operator_login']
        )
        assert (
            promocode['revoked']['otrs_ticket']
            == promocode_json['revoked']['otrs_ticket']
        )
    assert promocode['series_id'] == promocode_json['series_id']
    assert promocode['value'] == promocode_json['value']
    return True


def check_multi_user_promocode(promocode_json, mongodb):
    series = mongodb.promocode_series.find_one(promocode_json['series_id'])
    assert series['_id'] == promocode_json['code']
    assert series['value'] == promocode_json['value']
    assert series['finish'] and promocode_json['expire_at']
    return True


def compare_responses(response, expected):
    assert response['cost_usage'] == expected['cost_usage']
    assert response['orders_count'] == expected['orders_count']
    assert response['phone'] == expected['phone']
    assert sorted(
        response['failed_validation_reasons'], key=lambda x: x['code'],
    ) == sorted(expected['failed_validation_reasons'], key=lambda x: x['code'])
    assert sorted(response['usages'], key=lambda x: x['reserve']) == sorted(
        expected['usages'], key=lambda x: x['reserve'],
    )
    return True


class PromocodeType(enum.Enum):
    Single = 0
    Multi = 1


@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    'promocode, status_code, promocode_type',
    [
        ('eatspromocode2promocode', 200, PromocodeType.Single),
        ('validpromocode', 200, PromocodeType.Multi),
    ],
)
async def test_config_ok(
        taxi_coupons, mongodb, promocode, status_code, promocode_type,
):
    response = await taxi_coupons.get(
        f'/admin/promocodes/config/?promocode={promocode}',
    )
    assert response.status_code == status_code

    json = response.json()

    if promocode_type == PromocodeType.Single:
        assert check_unique_promocode(json, mongodb)
    if promocode_type == PromocodeType.Multi:
        assert check_multi_user_promocode(json, mongodb)


PHONE_VALUE = '+79044245004'
PHONE_ID = '5bbb5faf15870bd76635d5e2'


@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    'promocode, status_code, promocode_type, yandex_uid, expected_response',
    [
        (
            'eatspromocode2promocode',
            200,
            PromocodeType.Single,
            'yandex_uid-1',
            'usages_response_1.json',
        ),
        (
            'validpromocode',
            200,
            PromocodeType.Multi,
            'yandex_uid-2',
            'usages_response_2.json',
        ),
    ],
)
async def test_usages(
        mockserver,
        taxi_coupons,
        mongodb,
        promocode,
        status_code,
        promocode_type,
        yandex_uid,
        load_json,
        expected_response,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal(request):
        assert 'id' in request.json
        return {'id': request.json['id'], 'value': PHONE_VALUE}

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eaters(request):
        assert 'passport_uid' in request.json
        return {
            'eater': {
                'personal_phone_id': PHONE_ID,
                'id': 'eater-id-1',
                'uuid': 'eater-uuid-1',
                'created_at': '2021-06-01T00:00:00+00:00',
                'updated_at': '2021-06-01T00:00:00+00:00',
            },
        }

    @mockserver.json_handler('/user-api/users/search')
    def _mock_user_api(request):
        assert 'yandex_uid' in request.json
        assert request.json['fields'] == ['phone_id']
        return {'items': [{'id': 'taxi-user-id-1', 'phone_id': PHONE_ID}]}

    response = await taxi_coupons.get(
        f'/admin/promocodes/config/usages?'
        f'promocode={promocode}&yandex_uid={yandex_uid}',
    )
    assert response.status_code == status_code
    json = response.json()
    assert compare_responses(json, load_json(expected_response))


@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    'promocode, status_code, promocode_type, yandex_uid, expected_response',
    [
        (
            'eatspromocode2promocode',
            200,
            PromocodeType.Single,
            'yandex_uid-1',
            'usages_response_1.json',
        ),
        (
            'validpromocode',
            200,
            PromocodeType.Multi,
            'yandex_uid-2',
            'usages_response_2.json',
        ),
    ],
)
async def test_usages_bad_responses_404(
        mockserver,
        taxi_coupons,
        mongodb,
        promocode,
        status_code,
        promocode_type,
        yandex_uid,
        load_json,
        expected_response,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'person_not_found', 'message': 'person not found'},
        )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eaters(request):
        assert 'passport_uid' in request.json
        return mockserver.make_response(
            status=404,
            json={'code': 'eater_not_found', 'message': 'eater not found'},
            headers={'X-YaTaxi-Error-Code': 'eater_not_found'},
        )

    @mockserver.json_handler('/user-api/users/search')
    def _mock_user_api(request):
        assert 'yandex_uid' in request.json
        assert request.json['fields'] == ['phone_id']
        return {'items': []}

    response = await taxi_coupons.get(
        f'/admin/promocodes/config/usages?'
        f'promocode={promocode}&yandex_uid={yandex_uid}',
    )
    assert response.status_code == 404
