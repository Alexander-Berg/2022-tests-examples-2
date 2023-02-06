import pytest


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
        (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', 'oid1', 'nid1', TRUE, TRUE),
        ('p1', 'd2', 'oid2', 'nid2', TRUE, TRUE),
        ('p2', 'd1', 'oid3', 'nid3', TRUE, TRUE);
    """,
        """
    INSERT INTO fleet_fines.fines_dl
        (uin, dl_pd_id_normalized, payment_link, bill_date, sum, loaded_at,
         article_code, location, disappeared_at)
    VALUES
        ('1', 'nid1', 'payme1', '2020-01-06', 100.0, '2020-01-02',
        'Статья 1', 'Место 1', '2020-01-03'),
        ('2', 'nid3', 'payme2', '2020-01-05', 100.0, '2020-01-02',
        'Статья 2', 'Место 2', NULL),
        ('3', 'nid2', 'payme3', '2020-01-04', 100.0, '2020-01-02',
        'Статья 3', 'Место 3', NULL),
        ('4', 'nid1', 'payme4', '2020-01-03', 100.0, '2020-01-02',
        'Статья 4', 'Место 4', '2020-01-03'),
        ('5', 'nid2', 'payme5', '2020-01-02', 100.0, '2020-01-02',
        'Статья 5', 'Место 5', '2020-01-03'),
        ('6', 'nid1', 'payme6', '2020-01-01', 100.0, '2020-01-02',
        'Статья 6', 'Место 6', NULL);
        """,
    ],
)
async def test_success(web_app_client):
    response1 = await web_app_client.post(
        '/v1/list-by-drivers',
        json={'park_id': 'p1', 'driver_ids': ['d1', 'd2'], 'limit': 2},
    )
    assert response1.status == 200
    content1 = await response1.json()
    assert content1['fines'] == [
        {
            'article_code': 'Статья 6',
            'bill_date': '2020-01-01T03:00:00+03:00',
            'driver_id': 'd1',
            'doc_pd_id': 'nid1',
            'loaded_at': '2020-01-02T03:00:00+03:00',
            'location': 'Место 6',
            'park_id': 'p1',
            'payment_link': 'payme6',
            'sum': 100.0,
            'uin': '6',
        },
        {
            'article_code': 'Статья 5',
            'bill_date': '2020-01-02T03:00:00+03:00',
            'driver_id': 'd2',
            'disappeared_at': '2020-01-03T03:00:00+03:00',
            'doc_pd_id': 'nid2',
            'loaded_at': '2020-01-02T03:00:00+03:00',
            'location': 'Место 5',
            'park_id': 'p1',
            'payment_link': 'payme5',
            'sum': 100.0,
            'uin': '5',
        },
    ]
    assert 'cursor' in content1

    response2 = await web_app_client.post(
        '/v1/list-by-drivers',
        json={
            'park_id': 'p1',
            'driver_ids': ['d1', 'd2'],
            'limit': 2,
            'cursor': content1['cursor'],
        },
    )
    assert response2.status == 200
    content2 = await response2.json()
    assert content2['fines'] == [
        {
            'article_code': 'Статья 4',
            'bill_date': '2020-01-03T03:00:00+03:00',
            'driver_id': 'd1',
            'disappeared_at': '2020-01-03T03:00:00+03:00',
            'doc_pd_id': 'nid1',
            'loaded_at': '2020-01-02T03:00:00+03:00',
            'location': 'Место 4',
            'park_id': 'p1',
            'payment_link': 'payme4',
            'sum': 100.0,
            'uin': '4',
        },
        {
            'article_code': 'Статья 3',
            'bill_date': '2020-01-04T03:00:00+03:00',
            'driver_id': 'd2',
            'doc_pd_id': 'nid2',
            'loaded_at': '2020-01-02T03:00:00+03:00',
            'location': 'Место 3',
            'park_id': 'p1',
            'payment_link': 'payme3',
            'sum': 100.0,
            'uin': '3',
        },
    ]
    assert 'cursor' in content2


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
        (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', 'oid1', 'nid1', TRUE, TRUE)
        """,
        """
    INSERT INTO fleet_fines.fines_dl
        (uin, dl_pd_id_normalized, payment_link, bill_date, sum, loaded_at,
         article_code, location, disappeared_at)
    VALUES
        ('1', 'nid1', 'payme1', '2020-01-01', 100.0, '2020-01-20',
        'Статья 1', 'Место 1', '2020-01-30'),
        ('2', 'nid1', 'payme2', '2020-01-02', 100.0, '2020-01-20',
        'Статья 2', 'Место 2', NULL),
        ('3', 'nid1', 'payme3', '2020-01-03', 100.0, '2020-01-20',
        'Статья 3', 'Место 3', '2020-01-30'),
        ('4', 'nid1', 'payme4', '2020-01-04', 100.0, '2020-01-20',
        'Статья 4', 'Место 4', NULL),
        ('5', 'nid1', 'payme5', '2020-01-05', 100.0, '2020-01-20',
        'Статья 5', 'Место 5', '2020-01-30'),
        ('6', 'nid1', 'payme6', '2020-01-06', 100.0, '2020-01-20',
        'Статья 6', 'Место 6', NULL);
        """,
    ],
)
async def test_filters(web_app_client):
    response = await web_app_client.post(
        '/v1/list-by-drivers',
        json={
            'park_id': 'p1',
            'driver_ids': ['d1'],
            'limit': 100,
            'has_disappeared': False,
            'bill_date': {
                'from': '2020-01-02T00:00:00',
                'to': '2020-01-05T00:00:00',
            },
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content['fines'] == [
        {
            'park_id': 'p1',
            'driver_id': 'd1',
            'uin': '2',
            'payment_link': 'payme2',
            'bill_date': '2020-01-02T03:00:00+03:00',
            'sum': 100.0,
            'article_code': 'Статья 2',
            'location': 'Место 2',
            'doc_pd_id': 'nid1',
            'loaded_at': '2020-01-20T03:00:00+03:00',
        },
        {
            'park_id': 'p1',
            'driver_id': 'd1',
            'uin': '4',
            'payment_link': 'payme4',
            'bill_date': '2020-01-04T03:00:00+03:00',
            'sum': 100.0,
            'article_code': 'Статья 4',
            'location': 'Место 4',
            'doc_pd_id': 'nid1',
            'loaded_at': '2020-01-20T03:00:00+03:00',
        },
    ]
    assert 'cursor' not in content
