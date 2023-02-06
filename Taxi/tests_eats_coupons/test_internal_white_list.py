import copy

import pytest

REQUEST = {'series_id': 'first', 'yandex_uids': ['1', '2', '3', '4', '5']}
COUPONS_SERIES_INFO_RESPONSE = {
    'series_id': REQUEST['series_id'],
    'services': ['taxi'],
    'is_unique': True,
    'start': '2016-03-01',
    'finish': '2020-03-01',
    'descr': 'Уникальный, работает',
    'value': 123,
    'created': '2016-03-01T03:00:00+0300',
    'user_limit': 2,
    'currency': 'RUB',
    'country': 'rus',
}


def insert_into_dict(main_dict, **kwargs):
    result = copy.deepcopy(main_dict)
    for key, value in kwargs.items():
        result[key] = value
    return result


def get_uids_in_series_white_list(pgsql, series_id):
    cursor = pgsql['eats_coupons'].cursor()
    cursor.execute(
        f"""SELECT yandex_uid
        FROM eats_coupons.promocodes_white_lists
        WHERE series_id=\'{series_id}\';""",
    )
    result = cursor.fetchall()
    return list(x[0] for x in result)


@pytest.mark.config(
    EATS_COUPONS_ADD_USERS_TO_WHITE_LIST_SETTINGS={
        'batch_size': 50,
        'series_checks': {
            'is_series_exist_enabled': True,
            'is_series_contain_white_list_enabled': True,
        },
    },
)
@pytest.mark.parametrize(
    'coupons_response,coupons_code, expected_code',
    [
        pytest.param(None, 500, 500, id='Series info return 500'),
        pytest.param({'message': 'error'}, 404, 400, id='Series not found'),
        pytest.param(
            COUPONS_SERIES_INFO_RESPONSE, 200, 400, id='Series without meta',
        ),
        pytest.param(
            insert_into_dict(
                COUPONS_SERIES_INFO_RESPONSE,
                external_meta={'some_key': 'some_value'},
            ),
            200,
            400,
            id='Series without white list check flag in meta',
        ),
        pytest.param(
            insert_into_dict(
                COUPONS_SERIES_INFO_RESPONSE,
                external_meta={'some_key': 'some_value'},
            ),
            200,
            400,
            id='Series without white list check flag in meta',
        ),
        pytest.param(
            insert_into_dict(
                COUPONS_SERIES_INFO_RESPONSE,
                external_meta={'check-users-in-whitelist': False},
            ),
            200,
            400,
            id='white list validator is disabled',
        ),
        pytest.param(
            insert_into_dict(
                COUPONS_SERIES_INFO_RESPONSE,
                external_meta={'check-users-in-whitelist': True},
            ),
            200,
            200,
            id='white list validator is enabled success insert',
        ),
    ],
)
async def test_yandex_uids_insert(
        taxi_eats_coupons,
        pgsql,
        mockserver,
        coupons_response,
        coupons_code,
        expected_code,
):
    @mockserver.json_handler('/coupons/internal/series/info')
    def _mock_series_info(request):
        assert request.json == {'series_id': REQUEST['series_id']}
        return mockserver.make_response(
            status=coupons_code, json=coupons_response,
        )

    response = await taxi_eats_coupons.post(
        '/internal/white-list', json=REQUEST,
    )
    assert response.status_code == expected_code

    inserted = get_uids_in_series_white_list(
        pgsql=pgsql, series_id=REQUEST['series_id'],
    )
    if expected_code != 200:
        assert set(inserted) != set(REQUEST['yandex_uids'])
    else:
        assert set(inserted) == set(REQUEST['yandex_uids'])


async def test_double_insert(taxi_eats_coupons, pgsql):
    response = await taxi_eats_coupons.post(
        '/internal/white-list', json=REQUEST,
    )
    assert response.status_code == 200
    inserted = get_uids_in_series_white_list(
        pgsql=pgsql, series_id=REQUEST['series_id'],
    )
    assert set(inserted) == set(REQUEST['yandex_uids'])

    response = await taxi_eats_coupons.post(
        '/internal/white-list', json=REQUEST,
    )
    assert response.status_code == 200
    inserted = get_uids_in_series_white_list(
        pgsql=pgsql, series_id=REQUEST['series_id'],
    )
    assert set(inserted) == set(REQUEST['yandex_uids'])


@pytest.mark.config(
    EATS_COUPONS_ADD_USERS_TO_WHITE_LIST_SETTINGS={
        'batch_size': 1,
        'series_checks': {
            'is_series_exist_enabled': False,
            'is_series_contain_white_list_enabled': False,
        },
    },
)
async def test_success_insert_by_chunks(taxi_eats_coupons, pgsql):
    response = await taxi_eats_coupons.post(
        '/internal/white-list', json=REQUEST,
    )
    assert response.status_code == 200
    inserted = get_uids_in_series_white_list(
        pgsql=pgsql, series_id=REQUEST['series_id'],
    )
    assert set(inserted) == set(REQUEST['yandex_uids'])
