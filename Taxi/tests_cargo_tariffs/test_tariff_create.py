from testsuite.utils import matching


async def test_same_conditions(v1_tariff_creator):
    v1_tariff_creator.conditions = [
        {
            'field_name': 'source_zone',
            'sign': 'equal',
            'value': 'some_geozone',
        },
        {
            'field_name': 'employer_id',
            'sign': 'equal',
            'value': 'some_corp_id',
        },
    ]
    resp = await v1_tariff_creator.create()
    assert resp.status_code == 200
    assert resp.json() == {'id': matching.any_string}
    tariff_id = resp.json()['id']

    other_resp = await v1_tariff_creator.create()
    assert other_resp.status_code == 200
    assert other_resp.json()['warning']['code'] == 'already_exists'
    assert other_resp.json()['id'] == tariff_id


async def test_wrong_conditions(v1_tariff_creator):
    v1_tariff_creator.conditions = [
        {
            'field_name': 'some_wrong_condition',
            'sign': 'equal',
            'value': 'some_value',
        },
    ]
    resp = await v1_tariff_creator.create()
    assert resp.status_code == 400
    assert resp.json()['code'] == 'validation_error'
