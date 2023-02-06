import datetime as dt

import pytest

from tests_eats_order_revision import helpers


async def test_revision_list_correct(taxi_eats_order_revision, pgsql):
    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision_1',
        document='{}',
    )

    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision_0',
        created_at=dt.datetime.now() - dt.timedelta(hours=3),
        document='{}',
    )

    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision_2',
        document='{}',
        is_applied=False,
    )

    response = await taxi_eats_order_revision.get(
        '/v1/revision/list?order_id=test_order',
    )
    assert response.status == 200

    revisions = response.json()['revisions']

    assert len(revisions) == 2

    assert (
        response.json()['order_id'] == 'test_order'
        and revisions[0]['origin_revision_id'] == 'test_revision_0'
        and revisions[1]['origin_revision_id'] == 'test_revision_1'
    )


async def test_revision_list_tags_correct(taxi_eats_order_revision, pgsql):
    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order',
        origin_revision_id='test_revision',
        document='{}',
    )

    tags = ['initial', 'refund']

    helpers.insert_tags(pgsql=pgsql, revision_id=1, tags=tags)

    response = await taxi_eats_order_revision.get(
        '/v1/revision/list?order_id=test_order',
    )
    assert response.status == 200

    revisions = response.json()['revisions']
    assert len(revisions) == 1

    tags.sort()
    response_tags = revisions[0]['tags']
    response_tags.sort()
    assert (
        response.json()['order_id'] == 'test_order'
        and revisions[0]['origin_revision_id'] == 'test_revision'
        and response_tags == tags
    )


async def test_revision_list_not_found(taxi_eats_order_revision):
    response = await taxi_eats_order_revision.get(
        '/v1/revision/list?order_id=test_order',
    )

    assert response.status == 404


async def test_revision_list_bad_request(taxi_eats_order_revision):
    response = await taxi_eats_order_revision.get('/v1/revision/list?/%')

    assert response.status == 400


@pytest.mark.config(
    EATS_ORDER_REVISION_FALLBACK={'core_fallback_enabled': True},
)
async def test_revision_list_server_error(
        taxi_eats_order_revision, mock_core_revision_list,
):
    mock_core_revision_list(order_id='test_order_id', response={}, status=500)
    response = await taxi_eats_order_revision.get(
        '/v1/revision/list?order_id=test_order_id',
    )
    assert response.status == 500


@pytest.mark.config(
    EATS_ORDER_REVISION_FALLBACK={'core_fallback_enabled': True},
)
async def test_revision_list_fallback(
        taxi_eats_order_revision, pgsql, load_json, mock_core_revision_list,
):
    revision_list = load_json('core_revision_list.json')
    mock = mock_core_revision_list(
        order_id='test_order_id', response=revision_list,
    )
    response = await taxi_eats_order_revision.get(
        '/v1/revision/list?order_id=test_order_id',
    )
    assert response.status == 200
    assert mock.times_called == 1

    helpers.insert_revision(
        pgsql=pgsql,
        order_id='test_order_id',
        origin_revision_id='test_revision_id',
        document='{}',
    )
    response = await taxi_eats_order_revision.get(
        '/v1/revision/list?order_id=test_order_id',
    )
    assert response.status == 200
    assert mock.times_called == 1

    mock = mock_core_revision_list(
        order_id='test_order_id_1', response={}, status=404,
    )
    response = await taxi_eats_order_revision.get(
        '/v1/revision/list?order_id=test_order_id_1',
    )
    assert response.status == 404
    assert mock.times_called == 1
