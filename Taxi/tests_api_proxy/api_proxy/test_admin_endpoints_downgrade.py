import copy

import pytest

from tests_api_proxy.api_proxy.utils import endpoints as utils_endpoints


async def test_admin_downgrade_endpoint(load_json, endpoints):
    doc_path = '/example-bar'
    doc_uno = load_json('doc_uno.json')

    # create first revision
    await endpoints.put_endpoint(
        params={'id': doc_path, 'path': doc_path}, json=doc_uno,
    )
    await _ensure_doc(endpoints, copy.deepcopy(doc_uno), 0, doc_path)

    # create second revsion
    doc_dos = load_json('doc_dos.json')

    await endpoints.put_endpoint(
        params={
            'id': doc_path,
            'path': doc_path,
            'stable_revision': doc_uno['revision'],
            'percent': 10,
        },
        json=doc_dos,
        prestable=True,
    )
    await endpoints.finalize_endpoint_prestable(doc_path, 'release')

    await _ensure_doc(endpoints, copy.deepcopy(doc_dos), 1, doc_path)

    # downgrade to first one
    await endpoints.downgrade_endpoint(
        params={
            'id': doc_path,
            'last_revision': doc_dos['revision'],
            'donor_revision': doc_uno['revision'],
        },
        expected_new=doc_uno,
    )
    await _ensure_doc(endpoints, copy.deepcopy(doc_uno), 2, doc_path)

    # downgrade to non-existsing
    with pytest.raises(endpoints.Failure) as exc:
        await endpoints.downgrade_endpoint(
            params={
                'id': doc_path,
                'last_revision': doc_dos['revision'],
                'donor_revision': 100500,
            },
        )
    assert exc.value.response.status_code == 400
    assert exc.value.response.json() == {
        'code': 'endpoint_revision_not_found',
        'message': (
            'Endpoint \'/example-bar\' of revision \'100500\' not found'
        ),
    }

    await _ensure_doc(endpoints, copy.deepcopy(doc_uno), 2, doc_path)

    # create prestable
    await endpoints.safely_update_endpoint(
        doc_path,
        get_handler=doc_dos['handlers']['patch'],
        dev_team=doc_dos['dev_team'],
        prestable=10,
    )

    # downgrade to first one
    with pytest.raises(endpoints.Failure) as exc:
        await endpoints.downgrade_endpoint(
            params={
                'id': doc_path,
                'last_revision': doc_dos['revision'],
                'donor_revision': doc_uno['revision'],
            },
        )
    assert exc.value.response.status_code == 400
    assert exc.value.response.json()['code'] == 'prestable_exists'
    await endpoints.finalize_endpoint_prestable(doc_path, 'dismiss')

    # restore second
    await endpoints.downgrade_endpoint(
        params={
            'id': doc_path,
            'last_revision': 2,
            'donor_revision': doc_dos['revision'],
        },
        expected_new=doc_dos,
    )
    await _ensure_doc(endpoints, copy.deepcopy(doc_dos), 3, doc_path)


async def _ensure_doc(endpoints, expected_doc, expected_revision, path):
    doc = await endpoints.fetch_current_stable(path)
    assert doc.pop('revision') == expected_revision
    expected_doc.pop('revision')
    utils_endpoints.assert_eq_endpoints(doc, expected_doc)
