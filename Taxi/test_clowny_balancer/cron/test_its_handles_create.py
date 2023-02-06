# pylint: disable=redefined-outer-name
from clowny_balancer.generated.cron import run_cron


async def test_its_handles_create(
        patch, awacs_mockserver, relative_load_plaintext,
):
    awacs_mockserver()

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def create_ticket(**kwargs):
        test_description = relative_load_plaintext(
            'startrek_ticket_description.txt',
        )
        assert (
            kwargs['summary'] == 'Taxi, Eda, Lavka - изменение конфига ITS'
            and kwargs['description'] == test_description
        )
        return {'key': 'TAXIADMIN-1'}

    await run_cron.main(
        ['clowny_balancer.crontasks.its_handles_create', '-t', '0'],
    )

    assert len(create_ticket.calls) == 1
