import uuid

import pytest


CANDIDATE_ID = 'id'
EXTERNAL_ID = 'external_id'
LEAD_ID = 'lead_id'
LEAD_CANDIDATE_ID = 'candidate_id'
PHONE_PD_ID = 'personal_phone_id'
USER_INVITE_CODE = 'user_invite_code'


CANDIDATE_INSERT_QUERY = """
    INSERT INTO hiring_candidates.candidates (
        id,
        personal_phone_id
    ) VALUES (
        '{}', '{}'
    );
"""


async def test_lead_with_new_candidate(
        stq_runner, load_json, get_all_leads, get_all_candidates,
):
    request_body = 'full_data'
    data = load_json('requests.json')[request_body]
    await stq_runner.hiring_candidates_create_lead.call(
        task_id=uuid.uuid4().hex, args=(), kwargs=data,
    )

    candidate = get_all_candidates()[0]
    lead = get_all_leads()[0]

    assert candidate[PHONE_PD_ID] == data[PHONE_PD_ID]
    assert lead[EXTERNAL_ID] == lead[LEAD_ID] == data[EXTERNAL_ID]
    assert lead[LEAD_CANDIDATE_ID] == candidate[CANDIDATE_ID]


async def test_lead_with_existing_candidate(
        stq_runner, pgsql, load_json, get_all_leads, get_all_candidates,
):
    request_body = 'full_data'
    data = load_json('requests.json')[request_body]
    # add candidate to database
    candidate_id = uuid.uuid4().hex
    query = CANDIDATE_INSERT_QUERY.format(
        candidate_id, data.get('personal_phone_id'),
    )
    cursor = pgsql['hiring_candidates'].cursor()
    cursor.execute(query)

    await stq_runner.hiring_candidates_create_lead.call(
        task_id=uuid.uuid4().hex, args=(), kwargs=data,
    )

    candidate = get_all_candidates()[0]
    lead = get_all_leads()[0]

    assert candidate[PHONE_PD_ID] == data[PHONE_PD_ID]
    assert lead[EXTERNAL_ID] == lead[LEAD_ID] == data[EXTERNAL_ID]
    assert lead[LEAD_CANDIDATE_ID] == candidate[CANDIDATE_ID] == candidate_id


async def test_query_with_existing_external_id(
        stq_runner, pgsql, load_json, get_all_leads,
):
    request_body = 'full_data'
    data = load_json('requests.json')[request_body]

    # create primary lead
    await stq_runner.hiring_candidates_create_lead.call(
        task_id=uuid.uuid4().hex, args=(), kwargs=data,
    )
    first_leads_db_state = get_all_leads()

    # try again with same data
    await stq_runner.hiring_candidates_create_lead.call(
        task_id=uuid.uuid4().hex, args=(), kwargs=data,
    )
    second_leads_db_state = get_all_leads()

    assert first_leads_db_state == second_leads_db_state


async def test_lead_with_invite_code(
        stq_runner, load_json, get_all_leads, get_all_candidates,
):
    request_body = 'with_invite_code'
    data = load_json('requests.json')[request_body]
    await stq_runner.hiring_candidates_create_lead.call(
        task_id=uuid.uuid4().hex, args=(), kwargs=data,
    )

    candidate = get_all_candidates()[0]
    lead = get_all_leads()[0]

    assert candidate[PHONE_PD_ID] == data[PHONE_PD_ID]
    assert lead[EXTERNAL_ID] == lead[LEAD_ID] == data[EXTERNAL_ID]
    assert lead[LEAD_CANDIDATE_ID] == candidate[CANDIDATE_ID]
    assert lead[USER_INVITE_CODE] == data[USER_INVITE_CODE]


@pytest.mark.parametrize(
    'request_data', ['missing_phone', 'missing_external_id', 'null_data'],
)
@pytest.mark.xfail(raises=RuntimeError)
async def test_stq_run_with_missing_data(stq_runner, load_json, request_data):
    data = load_json('requests.json')[request_data]
    await stq_runner.hiring_candidates_create_lead.call(
        task_id=uuid.uuid4().hex, args=(), kwargs=data,
    )
