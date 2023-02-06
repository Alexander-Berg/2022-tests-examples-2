# pylint: disable=invalid-name, unused-variable, redefined-outer-name
import pytest

from taxi.clients import startrack

from scripts.stuff import startrack_report


ST_MESSAGE = (
    """
Скрипт (в окружении unittests)fake-url завершился.
Статус: succeeded.

(({}/dev/scripts/{{}} [ссылка]))
""".format(
        'https://tariff-editor-unstable.taxi.tst.yandex-team.ru',
    ).strip()
)


@pytest.fixture
def check_script_is_reported(find_script):
    async def do_it(_id):
        script = await find_script(_id)
        assert script['is_reported']

    return do_it


@pytest.mark.config(
    SCRIPTS_FEATURES={'reporting_enabled': True, 'report_to_prod': True},
)
async def test_do_stuff(
        patch,
        loop,
        scripts_tasks_app,
        setup_scripts,
        find_script,
        check_script_is_reported,
):
    await setup_scripts(
        [
            {
                'is_reported': False,
                'status': 'succeeded',
                '_id': 'non_reported_succeeded',
                'report_to_prod': True,
            },
            {
                'is_reported': False,
                'status': 'succeeded',
                '_id': 'non_reported_succeeded_bad_ticket',
                'ticket': 'SOME-STRANGE-1',
            },
            {
                'is_reported': False,
                'status': 'succeeded',
                '_id': 'non_reported_succeeded_ticket_url',
                'ticket': 'https://st.yandex-team.ru/TAXIBACKEND-1',
            },
            {
                'is_reported': False,
                'status': 'succeeded',
                '_id': 'non_reported_succeeded_empty_ticket',
                'ticket': None,
            },
        ],
    )

    @patch('scripts.lib.clients.scripts.Client.send_report')
    async def create_comment_remote(script, env):
        assert script.primary_key in {
            'non_reported_succeeded',
            'non_reported_succeeded_ticket_url',
        }
        assert (
            {
                'status': script.status,
                'url': script.url,
                'ticket': script.ticket,
                'env': env,
            }
            == {
                'status': 'succeeded',
                'url': 'fake-url',
                'ticket': 'TAXIBACKEND-1',
                'env': 'unittests',
            }
        )
        return {}

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment_local(ticket, **kwargs):
        assert ticket == 'TAXIBACKEND-1'
        assert kwargs['text'] == ST_MESSAGE.format(
            'non_reported_succeeded_ticket_url',
        )

    class StuffContext:
        data = scripts_tasks_app
        id = '123'

    await startrack_report.do_stuff(StuffContext(), loop)
    for _id in ('non_reported_succeeded', 'non_reported_succeeded_ticket_url'):
        await check_script_is_reported(_id)
    assert len(create_comment_remote.calls) == 1
    assert len(create_comment_local.calls) == 1

    for _id in [
            'non_reported_succeeded',
            'non_reported_succeeded_ticket_url',
            'non_reported_succeeded_empty_ticket',
    ]:
        script = await find_script(_id)
        assert script['is_reported']
    for _id in ['non_reported_succeeded_bad_ticket']:
        script = await find_script(_id)
        assert not script['is_reported']


@pytest.mark.config(SCRIPTS_FEATURES={'reporting_enabled': True})
async def test_test_some_fail_to_report(
        loop, patch, scripts_tasks_app, setup_scripts, find_script,
):
    await setup_scripts(
        [
            {
                'is_reported': False,
                'status': 'succeeded',
                '_id': 'non_reported_succeeded',
                'ticket': 'TAXIBACKEND-existing',
            },
            {
                'is_reported': False,
                'status': 'succeeded',
                '_id': 'non_reported_succeeded_bad_ticket',
                'ticket': 'TAXIBACKEND-non_existing',
            },
        ],
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticker, text):
        if text == ST_MESSAGE.format('non_reported_succeeded_bad_ticket'):
            raise startrack.NotFoundError(
                'Url issues/TAXIBACKEND-non_existing not found',
            )

    class StuffContext:
        data = scripts_tasks_app
        id = '123'

    await startrack_report.do_stuff(StuffContext(), loop)
    script = await find_script('non_reported_succeeded')
    assert script['is_reported']

    script = await find_script('non_reported_succeeded_bad_ticket')
    assert not script['is_reported']
