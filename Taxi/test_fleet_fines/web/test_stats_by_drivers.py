import pytest


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
    (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
     is_normalized, is_valid, last_check_date, last_successful_check)
    VALUES
        ('p1', 'd1', 'oid1', 'nid1', TRUE, TRUE, '2020-01-31', '2020-01-31')
        """,
        """
    INSERT INTO fleet_fines.fines_dl
    (uin, dl_pd_id_normalized, payment_link, bill_date, sum, discounted_sum,
     loaded_at, article_code, location, disappeared_at)
    VALUES
        ('1', 'nid1', 'payme1', '2020-01-01', 100.0, NULL,
         '2020-01-20', 'Статья 1', 'Место 1', '2020-01-30'),
        ('2', 'nid1', 'payme2', '2020-01-02', 100.0, NULL,
         '2020-01-20', 'Статья 2', 'Место 2', NULL),
        ('3', 'nid1', 'payme3', '2020-01-03', 100.0, NULL,
         '2020-01-20', 'Статья 3', 'Место 3', '2020-01-30'),
        ('4', 'nid1', 'payme4', '2020-01-04', 100.0, 50.0,
         '2020-01-20', 'Статья 4', 'Место 4', NULL),
        ('5', 'nid1', 'payme5', '2020-01-05', 100.0, NULL,
         '2020-01-20', 'Статья 5', 'Место 5', '2020-01-30'),
        ('6', 'nid1', 'payme6', '2020-01-06', 100.0, NULL,
         '2020-01-20', 'Статья 6', 'Место 6', NULL);
        """,
    ],
)
async def test_success(web_app_client):
    response = await web_app_client.post(
        '/v1/stats-by-drivers',
        json={
            'park_id': 'p1',
            'driver_ids': ['d1'],
            'has_disappeared': False,
            'bill_date': {
                'from': '2020-01-02T00:00:00',
                'to': '2020-01-05T00:00:00',
            },
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'quantity': 2,
        'sum': 200.0,
        'discounted_sum': 150.0,
        'earliest_successful_check': '2020-01-31T03:00:00+03:00',
    }


async def test_empty(web_app_client):
    response = await web_app_client.post(
        '/v1/stats-by-drivers',
        json={
            'park_id': 'p1',
            'driver_ids': ['d1'],
            'has_disappeared': False,
            'bill_date': {
                'from': '2020-01-02T00:00:00',
                'to': '2020-01-05T00:00:00',
            },
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'quantity': 0, 'sum': 0, 'discounted_sum': 0}
