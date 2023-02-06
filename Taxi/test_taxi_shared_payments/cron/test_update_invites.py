from taxi_shared_payments.generated.cron import run_cron
from taxi_shared_payments.repositories import members as members_repo


async def test_update_invites_cron_task(cron_context, patch):
    fetched_uids = set()
    portal_uids = {
        'P1': ['p1_has_portal_uid'],
        'P3': ['p3_has_portal_uid'],
        'P4': ['p4_has_portal_uid'],
    }

    @patch(
        'taxi_shared_payments.repositories.'
        'phone_confirmations.fetch_portal_uids',
    )
    async def _fetch_portal_uids(*args, **kwargs):
        assert len(args[1]) == 3
        fetched_uids.update(args[1])
        return portal_uids

    await run_cron.main(
        ['taxi_shared_payments.crontasks.update_invites', '-t', '0'],
    )

    assert {'P1', 'P2', 'P3'} == fetched_uids
    assert len(_fetch_portal_uids.calls) == 1

    fresh_invites = await members_repo.get_pending_phonish_invites(
        cron_context,
    )
    assert len(fresh_invites) == 1
