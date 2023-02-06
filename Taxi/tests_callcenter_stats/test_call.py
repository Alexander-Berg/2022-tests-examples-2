import pytest

CALL_URL = '/cc/v1/callcenter-stats/v1/call'
CALLCENTER_STATS_DB_TIMEOUTS = {
    'admin_timeouts': {'network_timeout': 1200, 'statement_timeout': 1000},
    'calls_history': {'network_timeout': 1200, 'statement_timeout': 1000},
    'default': {'network_timeout': 1200, 'statement_timeout': 1000},
}


@pytest.mark.now('2019-09-03 11:00:00.00')
@pytest.mark.config(CALLCENTER_STATS_DB_TIMEOUTS=CALLCENTER_STATS_DB_TIMEOUTS)
@pytest.mark.pgsql('callcenter_stats', files=['call_history.sql'])
@pytest.mark.parametrize(
    ['call_link_id', 'expected_status', 'expected_data'],
    (
        ('good_id3_hash', 200, 'expected_data_1.json'),
        ('good_id9_hash', 200, 'expected_data_2.json'),
        ('id1_hash', 200, 'expected_data_3.json'),
        ('id42_hash', 404, 'expected_data_4.json'),
        ('id11_hash', 200, 'expected_data_5.json'),
    ),
)
async def test_call(
        taxi_callcenter_stats,
        load_json,
        call_link_id,
        expected_status,
        expected_data,
        mockserver,
):
    @mockserver.handler('/callcenter-qa/v1/feedback/info')
    def _mock_cc_qa(request):
        commutation_id = request.json['commutation_id']
        if commutation_id.startswith('good'):
            return mockserver.make_response(
                json={
                    'feedbacks': [
                        {
                            'created_at': '2019-09-03T07:30:00+0000',
                            'id': 'feedback_id_1',
                            'type': 'type_1',
                            'image_link': 'test_link_1',
                        },
                        {
                            'type': 'type_2',
                            'created_at': '2019-09-03T07:30:00+0000',
                            'id': 'feedback_id_2',
                        },
                    ],
                },
                status=200,
            )
        return mockserver.make_response(json={'feedbacks': []}, status=200)

    response = await taxi_callcenter_stats.post(
        f'{CALL_URL}?call_link_id={call_link_id}',
    )
    assert response.status_code == expected_status
    data = response.json()
    assert data == load_json(expected_data)
