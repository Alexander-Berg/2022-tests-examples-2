import datetime

from duty.internal.clients import gap


async def test_gap(web_context, gap_mockserver, simple_secdist):
    gap_mockserver()

    gap_client = gap.GapClient(
        web_context.session, '$mockserver/gap', simple_secdist['GAP_OAUTH'],
    )

    oxcd8o_gaps = await gap_client.gaps_for_login('oxcd8o')

    assert len(oxcd8o_gaps) == 4
    assert oxcd8o_gaps[1].date_from == datetime.datetime(2019, 9, 16, 0, 0)
