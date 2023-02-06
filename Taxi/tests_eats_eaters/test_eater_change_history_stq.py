TEST_EATER_ID = '0'
HISTORY = {
    'eater_id': TEST_EATER_ID,
    'initiator_id': TEST_EATER_ID,
    'initiator_type': 'user',
    'changeset': '{"name":["", ""]}',
    'update_time': '2021-05-13T16:07:27.411636+0000',
}
HISTORY_EXPECTED = [
    {
        'initiator_id': TEST_EATER_ID,
        'initiator_type': 'user',
        'changeset': {'name': ['', '']},
        'update_time': '2021-05-13T16:07:27.411636+00:00',
    },
]


async def test_eater_change_history_ok(stq_runner, taxi_eats_eaters):
    await stq_runner.eater_change_history.call(
        task_id='test_id', kwargs=HISTORY,
    )

    response = await taxi_eats_eaters.post(
        '/v1/eaters/get-eater-change-history', json={'id': str(TEST_EATER_ID)},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'history' in response_json

    assert HISTORY_EXPECTED == response_json['history']
