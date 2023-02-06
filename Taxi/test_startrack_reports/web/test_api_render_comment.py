import pytest


@pytest.fixture
def taxi_startrack_reports_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.translations(
    startrack_reports={
        'drafts.commissions_create.enabled': {
            'ru': 'Включена',
            'en': 'Enabled',
        },
        'drafts.commissions_create.representation_template': {
            'ru': (
                'В рамках данного тикета кто:{login} создал черновик '
                'создания комиссии в {time}(MSK){data}'
            ),
            'en': (
                'кто:{login} created a draft of the сommission'
                ' in {time}(MSK){data}'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'data_file, locale, expected_file',
    [
        (
            'commissions_create/request.json',
            'ru',
            'commissions_create/response_ru.json',
        ),
        (
            'commissions_create/request.json',
            'en',
            'commissions_create/response_en.json',
        ),
        (
            'commissions_create/request_non_diff.json',
            'en',
            'commissions_create/response_non_diff_en.json',
        ),
    ],
)
@pytest.mark.pgsql(
    'startrack_reports', files=['startrack_reports_commissions.sql'],
)
@pytest.mark.usefixtures('taxi_startrack_reports_mocks')
async def test_render_comment(
        taxi_startrack_reports_web,
        load_json,
        data_file,
        locale,
        expected_file,
):
    response = await taxi_startrack_reports_web.post(
        '/v1/render_comment/',
        json=load_json(data_file),
        headers={'Accept-Language': locale},
    )
    assert response.status == 200
    content = await response.json()
    assert content == load_json(expected_file)
