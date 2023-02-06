import typing

import pytest


HEADERS = {'Accept-Language': 'ruRu'}
BACKEND_DRIVER_MESSAGES = {
    'exams.dkk.media.media_code_1.title': {'ru': 'Код медиа 1'},
    'exams.dkk.media.media_code_without_ru_locale.title': {},
    'exams.sts.media.media_code_1.title': {'ru': 'Код медиа 1'},
    'exams.sts.media.media_code_without_ru_locale.title': {},
}

BACKEND_MESSAGES = {
    'key_dkk_failed_1': {'ru': 'ДКК перевод 1'},
    'key_dkk_failed_2': {'ru': 'ДКК перевод 2'},
    'key_dkk_without_ru_locale': {},
}


@pytest.mark.translations(
    taximeter_backend_driver_messages=BACKEND_DRIVER_MESSAGES,
    taximeter_backend_messages=BACKEND_MESSAGES,
)
async def test_history_driver(web_app_client, mockserver, load_json):
    def _mock_responses(mockserver, load_json: typing.Callable[[str], dict]):
        @mockserver.json_handler('/quality-control-py3/api/v1/pass/history')
        def _quality_control_history_handler(request):
            return load_json('qc_get_dkk_history_response.json')

    _mock_responses(mockserver, load_json)
    response = await web_app_client.post(
        '/qc-admin/v1/dkk/history',
        json={'filter': dict(id='entity_id_1')},
        headers=HEADERS,
    )

    assert response.status == 200
    assert await response.json() == load_json('history_response_dkk.json')


@pytest.mark.translations(
    taximeter_backend_driver_messages=BACKEND_DRIVER_MESSAGES,
    taximeter_backend_messages=BACKEND_MESSAGES,
)
async def test_history_car(web_app_client, mockserver, load_json):
    def _mock_responses(mockserver, load_json: typing.Callable[[str], dict]):
        @mockserver.json_handler('/quality-control-py3/api/v1/pass/history')
        def _quality_control_history_handler(request):
            return load_json('qc_get_sts_history_response.json')

    _mock_responses(mockserver, load_json)
    response = await web_app_client.post(
        '/qc-admin/v1/sts/history',
        json={'filter': dict(id='entity_id_1')},
        headers=HEADERS,
    )

    assert response.status == 200
    assert await response.json() == load_json('history_response_sts.json')
