import pytest

DELETE_TAG_URL = '/cc/v1/callcenter-qa/v1/tag/'


@pytest.mark.parametrize(
    ['tag_uuid', 'request_body', 'expected_status', 'expected_response'],
    (
        pytest.param('uuid1', {}, 200, {}, id='no_project'),
        pytest.param('uuid1', {'project': 'disp'}, 200, {}, id='with_project'),
        pytest.param(
            'uuid3',
            {},
            404,
            {'code': 'not_found', 'message': 'Tag not found'},
            id='not_found',
        ),
        pytest.param(
            'uuid1',
            {'project': 'help'},
            403,
            {
                'code': 'access_denied',
                'message': 'Access denied: invalid project',
            },
            id='access_denied',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_qa', files=['prepare_tags.sql'])
async def test_base(
        taxi_callcenter_qa,
        tag_uuid,
        request_body,
        expected_status,
        expected_response,
        mockserver,
        pgsql,
):
    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        f'SELECT feedback_id FROM callcenter_qa.tag_links WHERE '
        f'tag_uuid = \'{tag_uuid}\'',
    )
    feedback_ids = (
        set(x[0] for x in cursor.fetchall())
        if expected_status == 200
        else set()
    )

    response = await taxi_callcenter_qa.delete(
        DELETE_TAG_URL + tag_uuid, json=request_body,
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response

    cursor.execute(
        'SELECT id, enabled_for_aggregation FROM callcenter_qa.feedbacks',
    )
    for id, aggregation_flag in cursor.fetchall():
        if id in feedback_ids:
            assert not aggregation_flag
        else:
            assert aggregation_flag
    cursor.close()
