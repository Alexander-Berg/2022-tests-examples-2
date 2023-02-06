# pylint: disable=redefined-outer-name
import json


async def test_io(load_json, resumes_upsert, resumes_by_rev):
    data = load_json('resumes.json')
    resumes = [json.dumps(_) for _ in data]
    await resumes_upsert(resumes)

    records = await resumes_by_rev(rev=0)
    assert len(records) == 1 and records[0]['id'] == 1
