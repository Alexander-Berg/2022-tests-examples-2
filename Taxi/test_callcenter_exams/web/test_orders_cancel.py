import pytest

from test_callcenter_exams import conftest
from test_callcenter_exams.web.static.default import (
    passport_responses as blackbox,
)  # noqa  # pylint: disable=line-too-long


@pytest.mark.parametrize('body', [blackbox.PASSPORT_RESPONSE_USER_1])
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_handler(web_app_client, body, pgsql):

    test_request = {'exam_data': {'question_id': 'q_1', 'exam_id': 'exam_1'}}

    response = await web_app_client.post(
        '/cc/v1/callcenter-exams/form/v1/orders/cancel',
        json=test_request,
        headers=conftest.pasport_headers(body['uid']['value']),
    )

    assert response.status == 200
    assert not await response.json()

    with pgsql['callcenter_exams'].cursor() as cursor:
        cursor.execute(
            'SELECT question_stat FROM callcenter_exams.questions_pass '
            'WHERE exam_id=\'exam_1\' and question_id=\'q_1\'',
        )
        assert cursor.rowcount == 1
        assert cursor.fetchone()[0]['orderscancel'] == 1
