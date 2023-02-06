import copy

import pytest


async def test_admin_downgrade_resource(testpoint, resources):
    doc_id = 'example-foo'
    doc_uno = {
        'revision': 0,
        'url': 'http://example.com/foo/1',
        'tvm-name': 'example-tvm-1',
        'method': 'post',
        'summary': 'Revision uno',
        'dev_team': 'foo',
        'caching-enabled': False,
        'use_envoy': False,
    }

    # create first revision
    await resources.put_resource(params={'id': doc_id}, json=doc_uno)
    await _ensure_doc(resources, copy.deepcopy(doc_uno), 0, doc_id)

    # create second revsion
    doc_dos = {
        'revision': 1,
        'url': 'http://example.com/foo/2',
        'tvm-name': 'example-tvm-2',
        'method': 'post',
        'summary': 'Revision dos',
        'dev_team': 'foo',
        'caching-enabled': False,
        'use_envoy': False,
    }

    await resources.put_resource(
        params={
            'id': doc_id,
            'stable_revision': doc_uno['revision'],
            'percent': 10,
        },
        json=doc_dos,
        prestable=True,
    )
    await resources.release_prestable_resource(
        params={
            'id': doc_id,
            'last_revision': doc_uno['revision'],
            'prestable_revision': doc_uno['revision'] + 1,
        },
    )
    await _ensure_doc(resources, copy.deepcopy(doc_dos), 1, doc_id)

    # downgrade to first one
    await resources.downgrade_resource(
        params={
            'id': doc_id,
            'last_revision': doc_dos['revision'],
            'donor_revision': doc_uno['revision'],
        },
        expected_new=doc_uno,
    )
    await _ensure_doc(resources, copy.deepcopy(doc_uno), 2, doc_id)

    # downgrade to non-existsing
    with pytest.raises(resources.Failure) as exc:
        await resources.downgrade_resource(
            params={
                'id': doc_id,
                'last_revision': 2,
                'donor_revision': 100500,
            },
        )
    assert exc.value.response.status_code == 400
    assert exc.value.response.json() == {
        'code': 'resource_revision_not_found',
        'message': 'Resource \'example-foo\' of revision \'100500\' not found',
    }
    await _ensure_doc(resources, copy.deepcopy(doc_uno), 2, doc_id)

    # create prestable
    await resources.put_resource(
        params={'id': doc_id, 'stable_revision': 2, 'percent': 10},
        json={
            'revision': 3,
            'url': 'http://prestable_value',
            'method': 'post',
            'summary': 'tmp',
            'dev_team': 'foo',
        },
        prestable=True,
    )

    # downgrade to first one
    with pytest.raises(resources.Failure) as exc:
        await resources.downgrade_resource(
            params={
                'id': doc_id,
                'last_revision': 2,
                'donor_revision': doc_uno['revision'],
            },
        )
    assert exc.value.response.status_code == 400
    assert exc.value.response.json()['code'] == 'prestable_exists'
    await resources.delete_prestable_resource(
        params={'id': doc_id, 'stable_revision': 2, 'prestable_revision': 3},
    )

    # restore second
    await resources.downgrade_resource(
        params={
            'id': doc_id,
            'last_revision': 2,
            'donor_revision': doc_dos['revision'],
        },
    )
    await _ensure_doc(resources, copy.deepcopy(doc_dos), 3, doc_id)


async def _ensure_doc(resources, expected_doc, expected_revision, doc_id):
    doc = await resources.fetch_current_stable(doc_id)
    assert doc.pop('revision') == expected_revision
    expected_doc.pop('revision')
    assert doc == expected_doc
