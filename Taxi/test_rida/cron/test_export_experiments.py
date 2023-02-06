import pytest

from rida.generated.cron import run_cron

EXPERIMENTS_ANSWER = (
    '<table><tr><td>media_world_new_year_iphone&emsp;</td>'
    '<td>2020-12-24T15:52:21.277735+03:00</td></tr>'
    '<tr><td>another_media_world_new_year_android&emsp;</td>'
    '<td>2020-12-24T15:51:21.277735+03:00</td></tr></table>'
)


@pytest.mark.config(
    EXPERIMENTS_EXPORT_SETTINGS={
        'recipient_emails': ['login@yandex-team.ru'],
        'sleep_time': 0.001,
        'experiments_blacklist': ['media_world_new_year_android'],
        'letter_template': 'test_slug',
        'max_experiments': 20,
        'enabled': True,
    },
)
@pytest.mark.translations(tariff={})
async def test_export_experiments(cron_context, mockserver, patch, load_json):
    @mockserver.json_handler('/taxi-exp/v1/experiments/list/')
    async def _handler(request):
        assert request.method == 'GET'
        offset = request.query.get('offset')
        return mockserver.make_response(
            status=200,
            json=(
                load_json('experiments.json')
                if offset == '0'
                else {'experiments': []}
            ),
        )

    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    async def _exp_handler(request):
        assert request.method == 'GET'
        name = request.query.get('name')
        exps = load_json('experiments.json')['experiments']
        for exp in exps:
            if exp['name'] == name:
                return mockserver.make_response(status=200, json=exp)
        return mockserver.make_response(
            status=400, json={'Error': 'No such experiment'},
        )

    @patch('taxi.clients.sender.SenderClient.send_transactional_email')
    async def _send(slug, emails, **kwargs):
        assert slug == 'test_slug'
        assert emails == 'login@yandex-team.ru'
        assert kwargs['template_vars'] == {
            'n_exp': 2,
            'experiments': EXPERIMENTS_ANSWER,
        }

    await run_cron.main(['rida.crontasks.export_experiments', '-t', '0'])
    assert _handler.times_called >= 1
    assert _exp_handler.times_called >= 1
    assert len(_send.calls) == 1
