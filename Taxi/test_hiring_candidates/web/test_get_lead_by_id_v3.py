import pytest


@pytest.mark.now('2022-06-01T12:00:00+0000')
async def test_v3_lead_get_non_existent_lead(taxi_hiring_candidates_web):
    # arrange
    # act
    response = await taxi_hiring_candidates_web.get(
        '/v3/leads/details',
        params={'id': 'non_existent_lead', 'locale': 'en'},
    )

    # assert
    assert response.status == 400
    assert await response.json() == {
        'code': 'LEAD_NOT_EXIST',
        'message': 'Lead non_existent_lead not found in database',
        'details': {'occurred_at': '2022-06-01T15:00:00+03:00', 'errors': []},
    }


@pytest.mark.config(
    TVM_RULES=[{'src': 'hiring-candidates', 'dst': 'personal'}],
)
@pytest.mark.now('2022-06-01T12:00:00+0000')
async def test_v3_lead_with_minimal_lead(
        taxi_hiring_candidates_web,
        load_json,
        taxi_config,
        mock_personal_phone_retrieve,
):
    # arrange
    personal_phone_retrieve_mock = mock_personal_phone_retrieve(
        response={'value': '+79999999999', 'id': 'phone_pd_id'},
    )

    # act
    response = await taxi_hiring_candidates_web.get(
        '/v3/leads/details',
        params={'id': 'DEF-EXTERNAL-ID-MIN-456', 'locale': 'ru'},
    )

    # assert
    assert response.status == 200
    assert await response.json() == load_json('responses/minimal.json')

    assert personal_phone_retrieve_mock.times_called == 1
    call = personal_phone_retrieve_mock.next_call()['request'].json
    assert call == {'id': 'JKL-PERSONAL-PHONE-789'}


@pytest.mark.config(
    TVM_RULES=[{'src': 'hiring-candidates', 'dst': 'personal'}],
)
@pytest.mark.translations(
    hiring_suggests={
        'employment_type.self_employed': {
            'ru': 'Самозанятый',
            'en': 'Self Employed (business-slave)',
        },
        'status.Active_100': {'ru': 'Совершил 100 поездок'},
        'tariff.comfort_plus': {'ru': 'Комфорт Плюс', 'en': 'Comfort +'},
        'car_colors.red': {'ru': 'Красный', 'en': ''},
    },
)
@pytest.mark.now('2022-06-01T12:00:00+0000')
async def test_v3_lead_with_maximal_lead(
        taxi_hiring_candidates_web,
        load_json,
        taxi_config,
        mock_personal_phone_retrieve,
        mock_personal_login_retrieve,
        mock_personal_license_retrieve,
        mock_gambling_territories_bulk_post,
        mock_gambling_conditions_bulk_post,
):
    # arrange
    personal_phone_retrieve_mock = mock_personal_phone_retrieve(
        response={'value': '+79999999999', 'id': 'phone_pd_id'},
    )
    personal_login_retrieve_mock = mock_personal_login_retrieve(
        response={'value': 'concrete_login', 'id': 'yandex_login_pd_id'},
    )
    personal_license_retrieve_mock = mock_personal_license_retrieve(
        response={'value': 'LIC4Q04B86E6N', 'id': 'driver_license_pd_id'},
    )
    gambling_territories_mock = mock_gambling_territories_bulk_post(
        response=load_json('gambling_territories_response.json'),
    )
    gambling_conditions_mock = mock_gambling_conditions_bulk_post(
        response=load_json('gambling_conditions_response.json'),
    )

    # act
    response = await taxi_hiring_candidates_web.get(
        '/v3/leads/details',
        params={'id': 'WXY-EXTERNAL-ID_MAX-222324', 'locale': 'ru'},
    )

    # assert
    assert response.status == 200
    assert await response.json() == load_json('responses/maximal.json')

    assert personal_phone_retrieve_mock.times_called == 1
    call = personal_phone_retrieve_mock.next_call()['request'].json
    assert call == {'id': 'ZAB-PERSONAL-PHONE-242526'}

    assert personal_login_retrieve_mock.times_called == 1
    call = personal_login_retrieve_mock.next_call()['request'].json
    assert call == {'id': 'TUV-CREATOR-LOGIN-ID-MAX-192021'}

    assert personal_license_retrieve_mock.times_called == 1
    call = personal_license_retrieve_mock.next_call()['request'].json
    assert call == {'id': 'PRS-LICENSE-ID-MAX-161718'}

    assert gambling_territories_mock.times_called == 1
    call = gambling_territories_mock.next_call()['request'].json
    assert call == {'region_ids': ['213']}

    assert gambling_conditions_mock.times_called == 1
    call = gambling_conditions_mock.next_call()['request'].json
    assert call == {'sf_ids': ['SoMe_PaRk_CoNdItIoN_iD']}
