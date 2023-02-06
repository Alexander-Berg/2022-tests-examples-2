import pytest

from test_callcenter_exams import conftest
from test_callcenter_exams.web.static.default import (
    passport_responses as blackbox,
)  # noqa  # pylint: disable=line-too-long


@pytest.mark.parametrize('body', [blackbox.PASSPORT_RESPONSE_USER_1])
@pytest.mark.parametrize('empty_yamaps', [True, False])
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_handler(
        mock_yamaps, load_json, web_app_client, body, empty_yamaps,
):
    @mock_yamaps('/yandsearch')
    async def _handle(request):
        file_name = 'yamaps.json'
        if empty_yamaps:
            file_name = 'yamaps_empty.json'
        return load_json(file_name)

    test_request = {
        'exam_data': {'question_id': 'q_1', 'exam_id': 'exam_1'},
        'll': [37.5, 55.7],
    }

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/form/v1/nearestposition',
        json=test_request,
        headers=conftest.pasport_headers(body['uid']['value']),
    )

    if empty_yamaps:
        assert response.status == 404
    else:
        assert response.status == 200
        true_response = {
            'point': [37.5, 55.7],
            'short_text': 'Большая Татарская улица, 35с4',
            'full_text': 'Россия, Москва, Большая Татарская улица, 35с4',
            'description': 'Большая Татарская улица, 35с4',
            'city': 'Москва',
        }
        assert await response.json() == true_response
