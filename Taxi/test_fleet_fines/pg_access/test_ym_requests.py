import datetime

from fleet_fines.generated.cron import cron_context as context_module


async def test_ym_requests(cron_context: context_module.Context):
    req_id1 = 'req_id1'
    req_id2 = 'req_id2'
    req_id3 = 'req_id3'
    await cron_context.pg_access.ym_requests.store_request(
        req_id=req_id1,
        dl_pd_ids=['num1', 'num2'],
        vcs=['num1', 'num2', 'num3'],
        create_time=datetime.datetime.utcnow(),
        next_poll=datetime.datetime.utcnow(),
    )
    await cron_context.pg_access.ym_requests.store_request(
        req_id=req_id2,
        dl_pd_ids=['num3', 'num4'],
        vcs=None,
        create_time=datetime.datetime.utcnow(),
        next_poll=datetime.datetime.utcnow(),
    )
    await cron_context.pg_access.ym_requests.store_request(
        req_id=req_id3,
        dl_pd_ids=None,
        vcs=['num3', 'num4', 'num5'],
        create_time=datetime.datetime.utcnow(),
        next_poll=datetime.datetime.utcnow(),
    )
    num_dls = await cron_context.pg_access.ym_requests.current_amount_dls()
    num_vcs = await cron_context.pg_access.ym_requests.current_amount_vcs()
    assert num_dls == 4
    assert num_vcs == 6
    await cron_context.pg_access.ym_requests.remove_request(req_id1)
    num_dls = await cron_context.pg_access.ym_requests.current_amount_dls()
    num_vcs = await cron_context.pg_access.ym_requests.current_amount_vcs()
    assert num_dls == 2
    assert num_vcs == 3
