from taxi_driver_metrics.common.models import dist_tasks_params

TST_TYPE = 'newbies_import'
TST_NAME = 'last_rev'


async def test_all(cron_context):
    async def tst_get():
        return await dist_tasks_params.get_param(
            cron_context.mongo, TST_TYPE, TST_NAME,
        )

    async def tst_set(val):
        return await dist_tasks_params.set_param(
            cron_context.mongo, TST_TYPE, TST_NAME, val,
        )

    res = await tst_get()
    assert res is None

    res = await tst_set('145')
    assert res is None

    res = await tst_get()
    assert res == '145'

    res = await tst_set('147')
    assert res == '145'
