import pytest

from fleet_fines.generated.cron import cron_context as context_module


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_vc
        (park_id, car_id, vc_original, vc_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'c1', 'oid1', 'nid1', TRUE, TRUE),
        ('p1', 'c2', 'oid2', 'nid2', TRUE, TRUE),
        ('p2', 'c1', 'oid3', 'nid3', TRUE, TRUE);
    """,
        """
    INSERT INTO fleet_fines.fines_vc
        (uin, vc_normalized, payment_link, bill_date, sum, loaded_at)
    VALUES
        ('1', 'nid1', 'payme1', '2020-01-01', 100.0, '2020-01-02'),
        ('2', 'nid3', 'payme2', '2020-01-01', 100.0, '2020-01-02'),
        ('3', 'nid2', 'payme3', '2020-01-01', 100.0, '2020-01-02'),
        ('4', 'nid1', 'payme4', '2020-01-01', 100.0, '2020-01-02'),
        ('5', 'nid2', 'payme5', '2020-01-01', 100.0, '2020-01-02'),
        ('6', 'nid1', 'payme6', '2020-01-01', 100.0, '2020-01-02');
        """,
    ],
)
async def test_fines_aggregation(cron_context: context_module.Context):
    data1, curs1 = await cron_context.pg_access.fines_aggregation.get_by_cars(
        park_id='p1', car_ids=['c1', 'c2'], limit=2,
    )
    assert curs1
    assert len(data1) == 2
    assert data1[0]['uin'] == '1'
    assert data1[1]['uin'] == '3'
    data2, curs2 = await cron_context.pg_access.fines_aggregation.get_by_cars(
        park_id='p1', car_ids=['c1', 'c2'], limit=2, cursor=curs1,
    )
    assert curs2
    assert len(data2) == 2
    assert data2[0]['uin'] == '4'
    assert data2[1]['uin'] == '5'
