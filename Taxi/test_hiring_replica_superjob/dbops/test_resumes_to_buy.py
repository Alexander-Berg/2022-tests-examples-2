# pylint: disable=redefined-outer-name
import json

import pytest


async def test_big_integers(load_json, resumes_upsert, resumes_to_buy):
    doc = load_json('big_integers.json')
    result = await resumes_upsert([json.dumps(doc)])
    assert result == 1
    resumes = await resumes_to_buy()
    for item in resumes:
        assert item['payment'] == doc['payment']
        assert item['age'] == doc['age']


@pytest.mark.config(
    HIRING_REPLICA_SUPERJOB_CONTACTS_PURCHASE_ENABLED=True,
    HIRING_REPLICA_SUPERJOB_AGE_FROM=21,
    HIRING_REPLICA_SUPERJOB_AGE_TO=60,
    HIRING_REPLICA_SUPERJOB_PAYMENT_TO=120000,
    HIRING_REPLICA_SUPERJOB_DRIVING_LICENSE=['B'],
    HIRING_REPLICA_SUPERJOB_GENDER='Мужской',
    HIRING_REPLICA_SUPERJOB_JOB_TYPES=['Оператор машинного доения'],
    HIRING_REPLICA_SUPERJOB_ALLOWED_CITIZENSHIPS=['Россия', 'Зимбабве'],
)
async def test_crimea(load_json, resumes_upsert, resumes_to_buy):
    doc = load_json('crimea.json')
    result = await resumes_upsert([json.dumps(doc)])
    assert result == 1
    resumes = await resumes_to_buy()
    assert not resumes


@pytest.mark.config(
    HIRING_REPLICA_SUPERJOB_CONTACTS_PURCHASE_ENABLED=True,
    HIRING_REPLICA_SUPERJOB_AGE_FROM=21,
    HIRING_REPLICA_SUPERJOB_AGE_TO=60,
    HIRING_REPLICA_SUPERJOB_PAYMENT_TO=120000,
    HIRING_REPLICA_SUPERJOB_DRIVING_LICENSE=['B'],
    HIRING_REPLICA_SUPERJOB_GENDER='Мужской',
    HIRING_REPLICA_SUPERJOB_JOB_TYPES=['Оператор машинного доения'],
    HIRING_REPLICA_SUPERJOB_ALLOWED_CITIZENSHIPS=['Россия'],
)
async def test_citizenship(load_json, resumes_upsert, resumes_to_buy):
    doc = load_json('citizenship.json')
    _json = [json.dumps(r) for r in doc]
    result = await resumes_upsert(_json)
    assert result == 2
    resumes = await resumes_to_buy()
    assert len(resumes) == 1
