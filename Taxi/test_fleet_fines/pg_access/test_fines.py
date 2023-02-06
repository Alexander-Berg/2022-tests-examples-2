import datetime

from fleet_fines.generated.cron import cron_context as context_module
from fleet_fines.pg_access import fines


async def test_store_dl(cron_context: context_module.Context):
    batch = [
        fines.PreparedDL(
            'n1',
            'uin1',
            'http://gib_moneys/1',
            datetime.datetime(2020, 1, 1),
            100.0,
            50.0,
            datetime.datetime(2019, 12, 31),
        ),
        fines.PreparedDL(
            'n2',
            'uin2',
            'http://gib_moneys/2',
            datetime.datetime(2020, 1, 2),
            200.0,
        ),
    ]
    await cron_context.pg_access.fines.bulk_store_dl(batch, lambda x: x)
    batch2 = [
        fines.PreparedDL(
            'n1',
            'uin1',
            'http://gib_moneys/1',
            datetime.datetime(2020, 1, 1),
            200.0,
        ),
    ]
    await cron_context.pg_access.fines.bulk_store_dl(batch2, lambda x: x)
    sql = 'SELECT * FROM fleet_fines.fines_dl ORDER BY dl_pd_id_normalized'
    stored = await cron_context.pg.main.fetch(sql)
    stored_dicts = [dict(record) for record in stored]
    assert stored_dicts[0].pop('loaded_at')
    assert stored_dicts[0].pop('modified_at')
    assert stored_dicts[0].pop('last_reloaded_at')
    assert stored_dicts[1].pop('loaded_at')
    assert stored_dicts[1].pop('modified_at')
    assert not stored_dicts[1].pop('last_reloaded_at')
    assert stored_dicts == [
        dict(
            uin='uin1',
            dl_pd_id_normalized='n1',
            payment_link='http://gib_moneys/1',
            bill_date=datetime.datetime(2020, 1, 1, 0, 0),
            sum=200.0,
            discounted_sum=None,
            discount_date=None,
            article_code=None,
            location=None,
            disappeared_at=None,
        ),
        dict(
            uin='uin2',
            dl_pd_id_normalized='n2',
            payment_link='http://gib_moneys/2',
            bill_date=datetime.datetime(2020, 1, 2, 0, 0),
            sum=200.0,
            discounted_sum=None,
            discount_date=None,
            article_code=None,
            location=None,
            disappeared_at=None,
        ),
    ]


async def test_store_vc(cron_context: context_module.Context):
    batch = [
        fines.PreparedVC(
            'n1',
            'uin1',
            'http://gib_moneys/1',
            datetime.datetime(2020, 1, 1),
            100.0,
            50.0,
            datetime.datetime(2019, 12, 31),
        ),
        fines.PreparedVC(
            'n2',
            'uin2',
            'http://gib_moneys/2',
            datetime.datetime(2020, 1, 2),
            200.0,
        ),
    ]
    await cron_context.pg_access.fines.bulk_store_vc(batch, lambda x: x)
    batch2 = [
        fines.PreparedVC(
            'n1',
            'uin1',
            'http://gib_moneys/1',
            datetime.datetime(2020, 1, 1),
            200.0,
        ),
    ]
    await cron_context.pg_access.fines.bulk_store_vc(batch2, lambda x: x)
    sql = 'SELECT * FROM fleet_fines.fines_vc ORDER BY vc_normalized'
    stored = await cron_context.pg.main.fetch(sql)
    stored_dicts = [dict(record) for record in stored]
    assert stored_dicts[0].pop('loaded_at')
    assert stored_dicts[0].pop('modified_at')
    assert stored_dicts[0].pop('last_reloaded_at')
    assert stored_dicts[1].pop('loaded_at')
    assert stored_dicts[1].pop('modified_at')
    assert not stored_dicts[1].pop('last_reloaded_at')
    assert stored_dicts == [
        dict(
            uin='uin1',
            vc_normalized='n1',
            payment_link='http://gib_moneys/1',
            bill_date=datetime.datetime(2020, 1, 1, 0, 0),
            sum=200.0,
            discounted_sum=None,
            discount_date=None,
            article_code=None,
            location=None,
            disappeared_at=None,
        ),
        dict(
            uin='uin2',
            vc_normalized='n2',
            payment_link='http://gib_moneys/2',
            bill_date=datetime.datetime(2020, 1, 2, 0, 0),
            sum=200.0,
            discounted_sum=None,
            discount_date=None,
            article_code=None,
            location=None,
            disappeared_at=None,
        ),
    ]
