import pytest

HEADERS = {
    'User-Agent': 'Taximeter 8.80 (562)',
    'X-Driver-Session': 'session1',
}


@pytest.mark.parametrize(
    'db_id,courier_type,expected_response',
    [
        (
            'db_id1',
            'not_walking_courier',
            'Пропуск*1*1*pass*port11*А123УУ48*123456789012*ООО Таксопарк',
        ),
        (
            'db_id2',
            'not_walking_courier',
            'Пропуск*1*1*pass*port11*А123УУ48*123456789013*ИП',
        ),
        (
            'db_id3',
            'not_walking_courier',
            'Пропуск*1*1*pass*port11*А123УУ48*123456789014*СМЗ',
        ),
        (
            'db_id1',
            'walking_courier',
            'Пропуск*1*1*pass*port11**123456789012*ООО Таксопарк',
        ),
    ],
    ids=['park', 'ip', 'selfemployed', 'courier'],
)
@pytest.mark.config(COVID_PERMITS_BY_SMS_HTML='Пропуск*1*{}*{}*{}*{}*{}*{}')
async def test_get_permits(
        taxi_driver_profile_view,
        driver_authorizer,
        parks_commute,
        mockserver,
        courier_type,
        expected_response,
        db_id,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        return {
            'driver_profiles': [
                {
                    'car': {'id': 'car_id', 'normalized_number': 'А123YY48'},
                    'driver_profile': {'courier_type': courier_type},
                },
            ],
            'limit': 1,
            'offset': 0,
            'parks': [{'id': db_id}],
            'total': 1,
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/identity-docs/retrieve_by_park_driver_profile_id',
    )
    def _mock_driver_profiles(request):
        return {
            'docs_by_park_driver_profile_id': [
                {
                    'park_driver_profile_id': 'db1_uuid1',
                    'docs': [
                        {
                            'data': {
                                'number_pd_id': 'test_passport_pd_id',
                                'type': 'passport_rus',
                            },
                            'id': 'doc_id',
                        },
                    ],
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _mock_personal(request):
        assert request.json == {
            'id': 'test_passport_pd_id',
            'primary_replica': False,
        }
        return {'id': 'phone_pd_id', 'value': 'passport11'}

    parks_commute.set_clid_mapping(
        {'db_id1': 'clid1', 'db_id2': 'clid2', 'db_id3': 'clid3'},
    )

    driver_authorizer.set_session(db_id, 'session1', 'uuid1')
    response = await taxi_driver_profile_view.get(
        'driver/profile-view/v1/permits-by-sms',
        params={'park_id': db_id},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.text == expected_response
