import pytest


@pytest.mark.config(
    HIRING_TELEPHONY_ENABLE_CREATE_LEAD_FOR_INCOMING_CALL=False,
)
async def test_incoming_call_acquire_task(
        load_json, taxi_hiring_telephony_oktell_callback_web, pgsql, personal,
):
    # arrange
    request = load_json('requests.json')['acquire']
    expected = load_json('responses.json')['acquire']

    # act
    response = await taxi_hiring_telephony_oktell_callback_web.post(
        '/v2/tasks/oktell/incomming', json=request,
    )

    # assert
    assert response.status == 200
    data = await response.json()
    assert data == expected


@pytest.mark.config(HIRING_TELEPHONY_ENABLE_CREATE_LEAD_FOR_INCOMING_CALL=True)
async def test_incoming_call_create_task(
        load_json,
        taxi_hiring_telephony_oktell_callback_web,
        pgsql,
        personal,
        composite_lead_task,
        web_context,
):
    # arrange
    request = load_json('requests.json')['create']
    expected = load_json('responses.json')['create']
    composite_lead_task(load_json('responses.json')['hiring-api'])

    # act
    response = await taxi_hiring_telephony_oktell_callback_web.post(
        '/v2/tasks/oktell/incomming?endpoint=test', json=request,
    )

    # assert
    assert response.status == 200
    data = await response.json()
    assert data == expected

    async with web_context.pg.master_pool.acquire() as conn:
        results = await conn.fetch(
            """SELECT count(*)
            FROM "hiring_telephony_oktell_callback"."tasks"
            WHERE task_id='{}'""".format(
                expected['task']['task_id'],
            ),
        )
    assert results[0]['count'] == 1
