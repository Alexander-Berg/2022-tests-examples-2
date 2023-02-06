import pytest


# Generated via `tvmknife unittest service -s 444 -d 111`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIvAMQbw:WPKzP90'
    '8f_Y5-7PxLhkZEx1cC5i4kdTYbv4eO1h_0tDX1d1u'
    'P8Og7N_Nl1RWyGsl_Dwk3ceh581YfoyCy0iJfW-Iv'
    'zRFi8cm4R8B8bQRq-Cuu15W1z0IGwp0Gg58UNeJ8f'
    'Go-kdaqCB2RpPcthDoqA-a9Sk-Qy_Cih0jW02ueII'
)

HEADERS = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}


@pytest.mark.parametrize(
    'request_body,expected_response',
    [
        (
            {'park_ids': ['db_id1']},
            {
                'certifications': [
                    {
                        'park_id': 'db_id1',
                        'is_certified': True,
                        'churn': 123.3,
                        'sh_per_driver': 1.1,
                        'sh_per_driver_threshold': 1.1,
                        'dpsat': 1.1,
                        'dpsat_threshold': 1.1,
                        'churn_threshold': 1.1,
                        'share_of_bad_grades': 1.1,
                        'share_of_bad_grades_threshold': 1.1,
                        'drivers': 1.1,
                        'drivers_threshold': 1.1,
                        'share_drivers_with_kis_art_id': 1.1,
                        'kis_art_id_threshold': 1.1,
                        'show_kis_art_flg': True,
                        'reason': 'cert reason',
                        'type': 'cert type',
                        'expiration_date': '2020-11-17T17:00:00+00:00',
                    },
                ],
            },
        ),
        (
            {'park_ids': ['db_id1', 'db_id2']},
            {
                'certifications': [
                    {
                        'park_id': 'db_id1',
                        'is_certified': True,
                        'churn': 123.3,
                        'sh_per_driver': 1.1,
                        'sh_per_driver_threshold': 1.1,
                        'dpsat': 1.1,
                        'dpsat_threshold': 1.1,
                        'churn_threshold': 1.1,
                        'share_of_bad_grades': 1.1,
                        'share_of_bad_grades_threshold': 1.1,
                        'drivers': 1.1,
                        'drivers_threshold': 1.1,
                        'share_drivers_with_kis_art_id': 1.1,
                        'kis_art_id_threshold': 1.1,
                        'show_kis_art_flg': True,
                        'reason': 'cert reason',
                        'type': 'cert type',
                        'expiration_date': '2020-11-17T17:00:00+00:00',
                    },
                    {'park_id': 'db_id2', 'is_certified': False},
                ],
            },
        ),
        (
            {'park_ids': ['db_id3']},
            {'certifications': [{'park_id': 'db_id3', 'is_certified': False}]},
        ),
    ],
)
async def test_certifications_ok(
        taxi_parks_certifications, request_body, expected_response,
):
    response = await taxi_parks_certifications.post(
        '/v1/parks/certifications/list', headers=HEADERS, json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == expected_response
