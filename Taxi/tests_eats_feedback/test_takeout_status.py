import pytest


@pytest.mark.pgsql('eats_feedback', files=['order.sql'])
@pytest.mark.parametrize(
    ['eater_id', 'expected_status'],
    [
        pytest.param('111', 'ready_to_delete', id='order_found'),
        pytest.param('eater_id_1', 'empty', id='order_not_found'),
    ],
)
async def test_when_eater_found(
        taxi_eats_feedback, mockserver, eater_id, expected_status,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eats_eaters(request):
        assert request.json['passport_uids'] == [
            'yandex_uid_1',
            'yandex_uid_2',
        ]
        return mockserver.make_response(
            status=200,
            json={
                'eaters': [
                    {
                        'id': eater_id,
                        'uuid': 'eater_uuid_1',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'updated_at': '2020-01-01T00:00:00+00:00',
                    },
                ],
                'pagination': {'limit': 1000, 'has_more': False},
            },
        )

    response = await taxi_eats_feedback.post(
        '/takeout/v1/status',
        json={
            'request_id': 'abc',
            'yandex_uids': [
                {'uid': 'yandex_uid_1', 'is_portal': False},
                {'uid': 'yandex_uid_2', 'is_portal': False},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == expected_status


@pytest.mark.pgsql('eats_feedback', files=['order.sql'])
async def test_when_eater_not_found(taxi_eats_feedback, mockserver):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eats_eaters(request):
        assert request.json['passport_uids'] == [
            'yandex_uid_1',
            'yandex_uid_2',
        ]
        return mockserver.make_response(
            status=200,
            json={
                'eaters': [],
                'pagination': {'limit': 1000, 'has_more': False},
            },
        )

    response = await taxi_eats_feedback.post(
        '/takeout/v1/status',
        json={
            'request_id': 'abc',
            'yandex_uids': [
                {'uid': 'yandex_uid_1', 'is_portal': False},
                {'uid': 'yandex_uid_2', 'is_portal': False},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()['data_state'] == 'empty'
