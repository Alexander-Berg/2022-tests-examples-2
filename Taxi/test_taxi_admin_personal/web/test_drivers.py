import pytest

from test_taxi_admin_personal import utils

DRIVERS_PD = {
    '100500_3625641848644387a263e78b2c3a7a5c': {
        'phone': '+79000000000',
        'driver_license': '000',
    },
    '5192573621_f977c37e2653e61186a6001e671f718d': {
        'phone': '+79000000005',
        'driver_license': '0000000000',
    },
}


async def test_search_by_pd_no_parameters(taxi_admin_personal):
    response = await utils.make_post_request(
        taxi_admin_personal, '/driver/search/', data={},
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'EMPTY_BODY'


@pytest.mark.config(
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
)
async def test_search_by_phone(web_app_client, mock_countries, mock_pd_phones):
    response = await utils.post_ok_json_response(
        '/driver/search/', {'phone': '+79000000000'}, web_app_client,
    )

    assert set(response['driver_ids']) == {
        '100500_3625641848644387a263e78b2c3a7a5c',
        '100500_794513c94b864ad7ad1088063ec468e1',
    }
    assert list(response.keys()) == ['driver_ids']

    assert len(mock_countries.calls) == 1
    assert mock_pd_phones.bulk_find_count == 1


async def test_search_by_driver_license(taxi_admin_personal):
    response = await utils.post_ok_json_response(
        '/driver/search/',
        {'driver_license': '00000000000'},
        taxi_admin_personal,
    )

    assert set(response['driver_ids']) == {
        '100112_ca3a2377daf2440097e2b9ec9749ca28',
        '100500_794513c94b864ad7ad1088063ec468e1',
        '100900_3580371a802b4c5b911ff3e0c0196244',
        '643753730335_b268d6727a7840ed9ca6dee4f5919c12',
    }
    assert list(response.keys()) == ['driver_ids']


@pytest.mark.config(
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
)
async def test_search_by_all_pd(
        web_app_client, mock_countries, mock_pd_phones,
):
    response = await utils.post_ok_json_response(
        '/driver/search/',
        {'driver_license': '00000000000', 'phone': '+79000000000'},
        web_app_client,
    )

    assert list(response.keys()) == ['driver_ids']
    assert set(response['driver_ids']) == {
        '100500_794513c94b864ad7ad1088063ec468e1',
    }

    assert len(mock_countries.calls) == 1
    assert mock_pd_phones.bulk_find_count == 1


async def test_get_pd_no_id(taxi_admin_personal):
    response = await utils.make_post_request(
        taxi_admin_personal, '/driver/retrieve/',
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'permissions,expected_fields',
    [
        (['view_driver_phones'], ['phone']),
        (['view_driver_licenses'], ['driver_license']),
        (
            ['view_driver_phones', 'view_driver_licenses'],
            ['phone', 'driver_license'],
        ),
        (['view_user_phones', 'view_user_emails'], []),
    ],
)
@pytest.mark.parametrize('driver_id,driver_pd', DRIVERS_PD.items())
@pytest.mark.config(
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
)
async def test_get_pd(
        permissions,
        expected_fields,
        driver_id,
        driver_pd,
        web_app_client,
        mock_countries,
        mock_pd_phones,
):
    expected = {
        field: value
        for field, value in driver_pd.items()
        if field in expected_fields
    }

    with utils.has_permissions(permissions):
        response = await utils.post_ok_json_response(
            f'/driver/{driver_id}/retrieve/', {}, web_app_client,
        )

    assert response == expected
    assert mock_pd_phones.bulk_retrieve_count == (
        1 if 'phone' in expected_fields else 0
    )


@pytest.mark.parametrize(
    'permissions,expected_fields',
    [
        (['view_driver_phones'], ['phone']),
        (
            ['view_driver_licenses', 'view_deptrans_driver_profile'],
            ['driver_license', 'deptrans_id'],
        ),
        (
            [
                'view_driver_phones',
                'view_driver_licenses',
                'view_deptrans_driver_profile',
            ],
            ['phone', 'driver_license', 'deptrans_id'],
        ),
        (['view_user_phones', 'view_user_emails'], []),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'taxi-admin-personal', 'dst': 'personal'}],
)
async def test_get_deptrans_pd(
        permissions,
        expected_fields,
        web_app_client,
        mock_countries,
        mock_pd_phones,
        mock_deptrans_ids,
):
    driver_id = '5192573621_f977c37e2653e61186a6001e671f718e'
    driver_pd = {
        'phone': '+79000000006',
        'driver_license': '0000000001',
        'deptrans_id': '123',
    }

    expected = {
        field: value
        for field, value in driver_pd.items()
        if field in expected_fields
    }

    with utils.has_permissions(permissions):
        response = await utils.post_ok_json_response(
            f'/driver/{driver_id}/retrieve/', {}, web_app_client,
        )

    assert response == expected
    assert mock_pd_phones.bulk_retrieve_count == (
        1 if 'phone' in expected_fields else 0
    )
    assert mock_deptrans_ids.bulk_retrieve.times_called == (
        1 if 'deptrans_id' in expected_fields else 0
    )
    assert mock_deptrans_ids.personal_deptrans_ids.times_called == (
        1 if 'deptrans_id' in expected_fields else 0
    )
