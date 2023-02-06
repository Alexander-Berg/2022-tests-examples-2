# pylint: disable=redefined-outer-name
import datetime
import json


async def test_insert_same_objects(load_json, resumes_upsert):
    data = load_json('same_resumes.json')
    resumes = [json.dumps(_) for _ in data]
    rows = await resumes_upsert(resumes)
    assert rows == 1


async def test_insert_different_objects(load_json, resumes_upsert):
    data = load_json('different_resumes.json')
    resumes = [json.dumps(_) for _ in data]
    rows = await resumes_upsert(resumes)
    assert rows == 2


async def test_insert_object(load_json, resumes_upsert, resume_get):
    data = load_json('same_resumes.json')
    resumes = [json.dumps(_) for _ in data]
    resume = data[0]
    await resumes_upsert(resumes)
    record = await resume_get(resume_id=resume['id'])

    assert json.loads(record['doc']) == resume
    assert isinstance(record['id'], int)
    assert isinstance(record['rev'], int)
    assert isinstance(record['created'], datetime.datetime)
    assert isinstance(record['updated'], datetime.datetime)


async def test_update_object(load_json, resumes_upsert, resume_get):
    data_bougth = load_json('resume_bought.json')
    data_not_bought = load_json('resume_not_bought.json')
    resume_bought = json.dumps(data_bougth)
    resume_not_bought = json.dumps(data_not_bought)

    await resumes_upsert([resume_not_bought])
    record_not_bouth = await resume_get(resume_id=data_not_bought['id'])
    assert record_not_bouth['rev'] == 1
    await resumes_upsert([resume_bought])
    record_bought = await resume_get(resume_id=data_not_bought['id'])
    assert record_bought['rev'] == 2
    assert record_bought['updated'] > record_not_bouth['updated']
    assert record_bought['created'] == record_not_bouth['created']
