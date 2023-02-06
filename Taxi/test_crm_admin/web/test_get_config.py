import pytest


_AUDIENCES_SETTINGS = [
    {
        'id': 'User',
        'test_users': [{'label': 'qwerty', 'value': '+666666'}],
        'directions': [{'label': 'zxc', 'value': 'somewhere'}],
    },
]


@pytest.mark.config(
    CRM_ADMIN_FEAUTERES={
        'local_to_utc_time_migration_date': '2022-04-18T10:00:00+03:00',
    },
    CRM_ADMIN_EFFICIENCY_SETTINGS={
        'group_size': 1000,
        'ignore_efficiency': False,
        'ignore_resolution': False,
        'efficiency_resolution_sla_in_hours': {'User': 72, 'Driver': 168},
    },
    CRM_ADMIN_SETTINGS={
        'QuicksegmentSettings': {
            'default_version': {'User': 10, 'Driver': 20},
        },
    },
    CRM_ADMIN_AUDIENCES_SETTINGS=_AUDIENCES_SETTINGS,
    CRM_ADMIN_FEATURE_FLAGS={'fancy_feature_enabled': True},
)
@pytest.mark.config(CRM_ADMIN_LINKS={'SupportChatUrl': 'https://ya.ru'})
async def test_get_config(web_app_client, mockserver):
    response = await web_app_client.get('/v1/config')
    assert response.status == 200
    response_data = await response.json()
    assert response_data == {
        'support_chat_url': 'https://ya.ru',
        'efficiency_size': 2100,
        'default_quicksegment_version': {'User': 10, 'Driver': 20},
        'efficiency_resolution_sla_in_hours': {'User': 72, 'Driver': 168},
        'feature_flags': {'fancy_feature_enabled': True},
        'feed_link_template': 'https://tariff-editor.taxi.dev.yandex-team.ru/newsletters/newsfeed/show/',  # noqa E501
        'audience_settings': _AUDIENCES_SETTINGS,
        'local_to_utc_time_migration_date': '2022-04-18T10:00:00+03:00',
    }
