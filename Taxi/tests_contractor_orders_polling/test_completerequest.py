import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.parametrize(
    (
        'md5_completerequest',
        'headers',
        'expected_md5_completerequest',
        'expected_completerequest',
    ),
    (
        pytest.param('ETAG', utils.HEADERS, 'ETAG', None, id='Same tag'),
        pytest.param(None, utils.HEADERS, 'ETAG', ['Hello'], id='No tag'),
        pytest.param('', utils.HEADERS, 'ETAG', ['Hello'], id='Empty tag'),
        pytest.param(
            'ETAG_BAD', utils.HEADERS, 'ETAG', ['Hello'], id='Different tag',
        ),
    ),
)
@pytest.mark.redis_store(
    ['set', 'Order:Driver:CompleteRequest:MD5:999:888', 'ETAG'],
    ['lpush', 'Order:Driver:CompleteRequest:Items:999:888', 'Hello'],
)
async def test_complete_request(
        taxi_contractor_orders_polling,
        md5_completerequest,
        headers,
        expected_md5_completerequest,
        expected_completerequest,
):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=headers,
        params={'md5_completerequest': md5_completerequest}
        if md5_completerequest
        else None,
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp.get('md5_completerequest') == expected_md5_completerequest
    assert resp.get('completerequest') == expected_completerequest


async def test_complete_request_no_server_tag(taxi_contractor_orders_polling):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=utils.HEADERS,
        params={'md5_completerequest': 'ETAG'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp.get('md5_completerequest') == 'ETAG'
    assert resp.get('completerequest') is None
