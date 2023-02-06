# pylint: disable=unused-variable

ST_MESSAGE = (
    """
Скрипт (в окружении unstable)http://fake-url завершился.
Статус: succeeded.

(({}/dev/scripts/{{}} [ссылка]))
""".format(
        'https://tariff-editor-unstable.taxi.tst.yandex-team.ru',
    ).strip()
)


async def test_send_report_to_ticket(patch, scripts_client):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, **kwargs):
        assert ticket == 'TAXIPLATFORM-1'
        assert kwargs['text'] == ST_MESSAGE.format('1234')

    response = await scripts_client.post(
        '/v1/cross-env/send-st-report/',
        json={
            'id': '1234',
            'status': 'succeeded',
            'url': 'http://fake-url',
            'ticket': 'TAXIPLATFORM-1',
            'env': 'unstable',
        },
    )
    assert response.status == 200
    assert create_comment.calls
