import copy
import csv
import io


def output_json():
    return {
        'a': 1,
        'b.nested': '2',
        'b.nested2.0.arr1': '1',
        'b.nested2.1.arr2': '2',
        'c': None,
    }


def input_json():
    return {
        'a': '1',
        'b': {'nested': '2', 'nested2': [{'arr1': '1'}, {'arr2': '2'}]},
        'c': None,
    }


def json_with_nones():
    return {
        'a': '1',
        'b': None,
        'c': [{'e': None}, {'f': None}],
        'd': [{'g': '1'}, {'k': None}],
    }


def make_csv(file=io.StringIO()):
    row = output_json()
    writer = csv.DictWriter(file, fieldnames=row.keys())
    writer.writeheader()
    writer.writerow(row)
    return file.getvalue()


async def test_serialize_with_nones(taxi_cargo_reports_web):
    response = await taxi_cargo_reports_web.post(
        '/v1/csv/serialize-json', json={'table': [json_with_nones()]},
    )
    assert response.status == 200
    response = await taxi_cargo_reports_web.post(
        '/v1/csv/parse-to-json',
        data=await response.text(),
        headers={'Content-Type': 'text/csv'},
    )
    assert response.status == 200
    result = await response.json()
    assert result == {'table': [{'a': '1', 'c': [], 'd': [{'g': '1'}]}]}


async def test_happy_path(taxi_cargo_reports_web):

    response = await taxi_cargo_reports_web.post(
        '/v1/csv/serialize-json', json={'table': [input_json()]},
    )
    assert response.status == 200

    response = await taxi_cargo_reports_web.post(
        '/v1/csv/parse-to-json',
        data=await response.text(),
        headers={'Content-Type': 'text/csv'},
    )
    assert response.status == 200
    result = await response.json()
    exp = copy.deepcopy(input_json())
    del exp['c']
    assert result == {'table': [exp]}


async def test_with_offset(taxi_cargo_reports_web):
    file = io.StringIO()
    file.write('some description,of my csv\r\n')

    response = await taxi_cargo_reports_web.post(
        '/v1/csv/parse-to-json',
        data=make_csv(file),
        params={'start_from_line': 1},
        headers={'Content-Type': 'text/csv'},
    )
    assert response.status == 200
    result = await response.json()
    exp = copy.deepcopy(input_json())
    del exp['c']
    assert result == {'table': [exp]}


async def test_bad_request(taxi_cargo_reports_web):
    response = await taxi_cargo_reports_web.post(
        '/v1/csv/parse-to-json', data='', headers={'Content-Type': 'text/csv'},
    )
    assert response.status == 400
