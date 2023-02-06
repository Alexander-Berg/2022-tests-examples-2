import pytest


@pytest.mark.config(
    DRIVER_STORIES_CUSTOM_CONTEXT_TABLES={
        '__default__': {},
        '5bca0c9e7bcecff318fef3aa': {
            'cluster': 'senecasas',
            'table': '//home/taxi-analytics/ny_2022_stories/stories',
        },
        '5bca0c9e7bcecff318fef3bb': {
            'cluster': 'senecavla',
            'table': '//home/taxi-analytics/ny_2022_stories/stories',
        },
        '5bca0c9e7bcecff318fef3cc': {
            'cluster': 'senecasas',
            'table': '//home/taxi-analytics/ny_2022_stories/stories',
        },
    },
)
@pytest.mark.yt(dyn_table_data=['yt_driver_context.yaml'])
@pytest.mark.parametrize(
    'lesson_id, driver, stories_response_mock, locale',
    [
        (
            '5bca0c9e7bcecff318fef3aa',
            'driver1',
            'stories_response_mock_az.json',
            'az',
        ),
        (
            '5bca0c9e7bcecff318fef3bb',
            'driver2',
            'stories_response_mock_he.json',
            'he',
        ),
        (
            '5bca0c9e7bcecff318fef3cc',
            'driver3',
            'stories_response_mock_ru.json',
            'ru',
        ),
    ],
)
async def test_stories_custom_context(
        yt_apply,
        web_app_client,
        mock_unique_drivers,
        load_json,
        localizations,
        make_dap_headers,
        lesson_id,
        driver,
        stories_response_mock,
        locale,
):
    response = await web_app_client.get(
        '/driver/v1/driver-lessons/v1/lessons/' + lesson_id,
        headers=make_dap_headers(
            park_id='park',
            driver_id=driver,
            additional_headers={'Accept-Language': locale},
        ),
    )
    assert response.status == 200
    content = await response.json()
    response_mock = load_json(stories_response_mock)
    assert content == response_mock
