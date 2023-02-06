import pytest


@pytest.mark.parametrize(
    ('response_code', 'new_settings'),
    [
        (400, {}),
        (
            200,
            {
                'display_tab': False,
                'enable_stats_job': False,
                'enable_payments_job': False,
                'enable_antifraud_job': False,
                'enable_mapreduce_job': False,
                'generate_new_promocodes': False,
                'cities': ['Владивосток'],
            },
        ),
        (
            200,
            {
                'some_extra_field': True,
                'display_tab': False,
                'enable_stats_job': True,
                'enable_payments_job': True,
                'enable_antifraud_job': True,
                'enable_mapreduce_job': True,
                'generate_new_promocodes': True,
                'cities': [
                    'Москва',
                    'Тверь',
                    'Санкт-Петербург',
                    'Минск',
                    'Рига',
                ],
            },
        ),
    ],
)
async def test_admin_settings_post(
        web_app_client, response_code, new_settings,
):
    response = await web_app_client.post('/admin/settings/', json=new_settings)
    assert response.status == response_code
