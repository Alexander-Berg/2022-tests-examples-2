import json

import pytest

from tests_eats_order_revision import helpers


async def test_revision_diff_nothing_changes(
        taxi_eats_order_revision, pgsql, load_json,
):
    response = await get_revision_diff(
        taxi_eats_order_revision,
        pgsql,
        load_json,
        'revisions_with_details/revision_doc.json',
        'revisions_with_details/revision_doc.json',
    )
    assert not response.json()['diffs']


async def test_revision_diff_not_found(taxi_eats_order_revision):
    response = await taxi_eats_order_revision.get(
        '/v1/revision/diff?order_id=test_order&'
        'first_revision_id=test_revision&second_revision_id=test_revision_1',
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'file1, file2, diff_type, path',
    [
        (
            'revisions_with_details/revision_doc.json',
            'revisions_with_details/revision_doc_add_cs.json',
            'add_diff',
            'path_second',
        ),
        (
            'revisions_with_details/revision_doc_add_cs.json',
            'revisions_with_details/revision_doc.json',
            'delete_diff',
            'path_first',
        ),
    ],
)
async def test_revision_diff_customer_services_change(
        taxi_eats_order_revision,
        pgsql,
        load_json,
        file1,
        file2,
        diff_type,
        path,
):
    response = await get_revision_diff(
        taxi_eats_order_revision, pgsql, load_json, file1, file2,
    )
    assert len(response.json()['diffs']) == 1
    assert response.json()['diffs'][0]['type'] == diff_type
    assert response.json()['diffs'][0][path] == '/customer_services/3'


@pytest.mark.parametrize(
    'file1, file2, res_path, desc',
    [
        (
            'revisions_with_details/revision_doc.json',
            'revisions_with_details/revision_doc_change_cs.json',
            '/customer_services/1',
            'Изменение заказа',
        ),
        (
            'revisions_with_details/revision_doc.json',
            'revisions_with_details/revision_doc_add_refund.json',
            '/customer_services/0',
            'Изменение заказа. Изменение в возвратах',
        ),
    ],
)
async def test_revision_diff_change_order(
        taxi_eats_order_revision,
        pgsql,
        load_json,
        file1,
        file2,
        res_path,
        desc,
):
    response = await get_revision_diff(
        taxi_eats_order_revision, pgsql, load_json, file1, file2,
    )
    assert len(response.json()['diffs']) == 1
    assert response.json()['diffs'][0]['type'] == 'change_diff'
    assert response.json()['diffs'][0]['path_first'] == res_path
    assert response.json()['diffs'][0]['path_second'] == res_path
    assert response.json()['diffs'][0]['description'] == desc


async def test_revision_diff_complex(
        taxi_eats_order_revision, pgsql, load_json,
):
    response = await get_revision_diff(
        taxi_eats_order_revision,
        pgsql,
        load_json,
        'revisions_with_details/revision_doc.json',
        'revisions_with_details/revision_doc_complex.json',
    )
    assert len(response.json()['diffs']) == 3
    assert response.json()['diffs'][0]['type'] == 'change_diff'
    assert response.json()['diffs'][1]['type'] == 'change_diff'
    assert response.json()['diffs'][2]['type'] == 'add_diff'


async def get_revision_diff(
        taxi_eats_order_revision, pgsql, load_json, file1, file2,
):
    doc = load_json(file1)
    doc_changed = load_json(file2)
    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision',
        document=json.dumps(doc),
    )
    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision_1',
        document=json.dumps(doc_changed),
    )
    response = await taxi_eats_order_revision.get(
        '/v1/revision/diff?order_id=test_order&'
        'first_revision_id=test_revision&second_revision_id=test_revision_1',
    )
    assert response.status == 200
    assert response.json()['first_revision_id'] == 'test_revision'
    assert response.json()['second_revision_id'] == 'test_revision_1'
    return response


async def test_revision_diff_bad_request(taxi_eats_order_revision):
    response = await taxi_eats_order_revision.get(
        '/v1/revision/diff?order_id/%',
    )
    assert response.status == 400
