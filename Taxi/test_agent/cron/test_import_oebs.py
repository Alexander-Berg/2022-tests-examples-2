# pylint: disable=redefined-outer-name
from aiohttp import web
import pytest

from agent import utils
from agent.generated.cron import run_cron


@pytest.mark.parametrize(
    'login,oebs_data,user_data',
    [
        (
            'webalex',
            {
                'logins': [
                    {
                        'login': 'webalex',
                        'assignments': [
                            {
                                'assignmentID': 487609,
                                'assignmentNumber': '528-71',
                                'taxUnitID': '111042',
                                'taxUnitName': 'ЯТ',
                                'orgID': 230835,
                                'orgName': 'ЯТ',
                                'contractType': 'Основное место работы',
                                'primaryFlag': 'Y',
                                'legislationCode': 'ru',
                                'salaryBasis': 'RUB (оклад)',
                            },
                        ],
                    },
                ],
            },
            {
                'piece': False,
                'country': 'ru',
                'location': None,
                'hr_position': 'Специалист поддержки сервиса.',
            },
        ),
        (
            'webalex',
            {
                'logins': [
                    {
                        'login': 'webalex',
                        'assignments': [
                            {
                                'assignmentID': 487609,
                                'assignmentNumber': '528-71',
                                'taxUnitID': '111042',
                                'taxUnitName': 'ООО Убер Системс Бел',
                                'orgID': 230835,
                                'orgName': 'org',
                                'contractType': 'Основное место работы',
                                'primaryFlag': 'Y',
                                'legislationCode': 'BY',
                                'salaryBasis': 'RUB (часовая ставка сделка)',
                            },
                        ],
                    },
                ],
            },
            {
                'piece': True,
                'country': 'by',
                'location': 'Беларусь',
                'hr_position': 'Специалист поддержки сервиса.',
            },
        ),
        (
            'webalex',
            {
                'logins': [
                    {
                        'login': 'webalex',
                        'assignments': [
                            {
                                'assignmentID': 487609,
                                'assignmentNumber': '528-71',
                                'taxUnitID': '111042',
                                'taxUnitName': 'Яндекс Такси Технологии',
                                'orgID': 230835,
                                'orgName': 'Яндекс Такси',
                                'contractType': 'Основное место работы',
                                'primaryFlag': 'Y',
                                'legislationCode': 'RU',
                                'salaryBasis': 'RUB (часовая ставка сделка)',
                            },
                        ],
                    },
                ],
            },
            {
                'piece': True,
                'country': 'ru',
                'location': None,
                'hr_position': 'Специалист поддержки сервиса.',
            },
        ),
        (
            'webalex',
            {
                'logins': [
                    {
                        'login': 'webalex',
                        'assignments': [
                            {
                                'assignmentID': 487609,
                                'assignmentNumber': '528-71',
                                'taxUnitID': '111042',
                                'taxUnitName': 'Яндекс Такси Технологии',
                                'orgID': 230835,
                                'orgName': 'Яндекс Такси',
                                'contractType': 'Основное место работы',
                                'primaryFlag': 'Y',
                                'legislationCode': 'RU',
                                'salaryBasis': None,
                            },
                        ],
                    },
                ],
            },
            {
                'piece': False,
                'country': 'ru',
                'location': None,
                'hr_position': 'Специалист поддержки сервиса.',
            },
        ),
        (
            'webalex',
            [],
            {
                'piece': False,
                'country': None,
                'location': None,
                'hr_position': 'Специалист поддержки сервиса.',
            },
        ),
        (
            'webalex',
            None,
            {
                'piece': False,
                'country': None,
                'location': None,
                'hr_position': 'Специалист поддержки сервиса.',
            },
        ),
    ],
)
async def test_oebs(
        cron_context,
        mock_oebs,
        mock_oebs_primary,
        taxi_config,
        login,
        oebs_data,
        user_data,
):
    @mock_oebs('/rest/assgtList', prefix=True)
    def handler(request):  # pylint: disable=unused-variable
        return web.json_response(oebs_data)

    await run_cron.main(['agent.crontasks.import_oebs', '-t', '0'])
    async with cron_context.pg.slave_pool.acquire() as conn:
        sql_query = 'SELECT * FROM agent.users WHERE login=\'{login}\''.format(
            login=login,
        )
        user = await conn.fetchrow(sql_query)
        assert user['piece'] == user_data['piece']
        assert user['location'] == user_data['location']
        assert user['country'] == user_data['country']
        assert user['hr_position'] == user_data['hr_position']


@pytest.mark.parametrize(
    'input_str,flag',
    [
        ('сделка', True),
        ('123', False),
        ('RUB (часовая ставка сделка)', True),
        ('RUB (сдельная оплата)', True),
        (None, False),
    ],
)
async def test_check_sdel(input_str, flag):
    assert utils.check_piece(input_str) == flag
