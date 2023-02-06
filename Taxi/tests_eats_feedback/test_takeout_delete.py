import pytest


def load_orders(pgsql):
    with pgsql['eats_feedback'].cursor() as cursor:
        cursor.execute(
            'SELECT eater_id, order_nr '
            + 'FROM eats_feedback.orders '
            + 'ORDER BY eater_id, order_nr ASC',
        )
        return list(list(row) for row in cursor)


@pytest.mark.pgsql('eats_feedback', files=['add_orders.sql'])
async def test_happy_path(taxi_eats_feedback, mockserver, pgsql):
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
                        'id': 'eater_id_1',
                        'uuid': 'eater_uuid_1',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'updated_at': '2020-01-01T00:00:00+00:00',
                    },
                    {
                        'id': 'eater_id_2',
                        'uuid': 'eater_uuid_2',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'updated_at': '2020-01-01T00:00:00+00:00',
                    },
                    {
                        'id': 'eater_id_3',
                        'uuid': 'eater_uuid_3',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'updated_at': '2020-01-01T00:00:00+00:00',
                    },
                ],
                'pagination': {'limit': 1000, 'has_more': False},
            },
        )

    response = await taxi_eats_feedback.post(
        '/takeout/v1/delete',
        json={
            'request_id': 'abc',
            'yandex_uids': [
                {'uid': 'yandex_uid_1', 'is_portal': False},
                {'uid': 'yandex_uid_2', 'is_portal': False},
            ],
        },
    )
    assert response.status_code == 200

    assert load_orders(pgsql) == [
        ['eater_id_4', 'order_nr_41'],
        ['eater_id_4', 'order_nr_42'],
    ]


@pytest.mark.pgsql('eats_feedback', files=['add_orders.sql'])
async def test_eaters_not_found(taxi_eats_feedback, mockserver, pgsql):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eats_eaters(request):
        assert request.json['passport_uids'] == ['yandex_uid_1']
        return mockserver.make_response(
            status=200,
            json={
                'eaters': [],
                'pagination': {'limit': 1000, 'has_more': False},
            },
        )

    response = await taxi_eats_feedback.post(
        '/takeout/v1/delete',
        json={
            'request_id': 'abc',
            'yandex_uids': [{'uid': 'yandex_uid_1', 'is_portal': False}],
        },
    )
    assert response.status_code == 200

    assert load_orders(pgsql) == [
        ['eater_id_1', 'order_nr_11'],
        ['eater_id_1', 'order_nr_12'],
        ['eater_id_2', 'order_nr_21'],
        ['eater_id_2', 'order_nr_22'],
        ['eater_id_4', 'order_nr_41'],
        ['eater_id_4', 'order_nr_42'],
    ]
