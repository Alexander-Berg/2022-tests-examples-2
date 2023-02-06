# pylint: disable=too-many-lines

import pytest

from tests_eats_order_revision import helpers

NOW = '2021-08-25T07:20:00+00:00'


@pytest.mark.now(NOW)
@pytest.mark.config(
    EATS_ORDER_REVISION_ORIGINATOR_CHECK={
        'enabled': False,
        'allowed_for_services': [],
    },
    EATS_ORDER_REVISION_FEATURE_FLAGS={
        'post_processing_stq_enabled': True,
        'discounts_processing_stq_enabled': True,
    },
)
async def test_successful_raw_revision_creation(
        check_create_raw_revision, pgsql, load_json, stq,
):
    initial_doc = load_json(
        'revisions_without_details/revision_doc_with_mixins.json',
    )
    expected_doc = load_json('revisions_without_details/revision_doc.json')
    mixins = load_json('mixins.json')

    await check_create_raw_revision(
        'test_order', 'test_revision', '800.00', initial_doc, [],
    )
    actual_revision = helpers.fetch_revision(
        pgsql=pgsql, order_id='test_order', origin_revision_id='test_revision',
    )
    expected_revision = {
        'id': 1,
        'order_id': 'test_order',
        'origin_revision_id': 'test_revision',
        'cost_for_customer': 800.00,
        'document': expected_doc,
        'is_applied': True,
        'created_at': actual_revision['created_at'],
    }

    assert actual_revision == expected_revision
    check_mixins(
        pgsql,
        initial_doc,
        [mixins['mixins'][0], mixins['mixins'][0], mixins['mixins'][0]],
    )
    assert stq.eats_order_revision_creation_post_process.times_called == 1


@pytest.mark.now(NOW)
@pytest.mark.config(
    EATS_ORDER_REVISION_ORIGINATOR_CHECK={
        'enabled': False,
        'allowed_for_services': [],
    },
)
async def test_successful_revision_updating(
        check_create_raw_revision, pgsql, load_json,
):
    first_doc = load_json(
        'revisions_without_details/revision_doc_with_mixins.json',
    )
    second_doc = load_json(
        'revisions_without_details/revision_doc_with_mixins_2.json',
    )
    mixins = load_json('mixins.json')
    first_tags = ['initial', 'refund']
    second_tags = ['refund', 'final']
    tags = ['initial', 'refund', 'final']

    await check_create_raw_revision(
        'test_order', 'test_revision', '800.00', first_doc, first_tags,
    )
    await check_create_raw_revision(
        'test_order', 'test_revision', '800.00', second_doc, second_tags,
    )
    count = helpers.fetch_revision_count(pgsql=pgsql)
    assert count == 1

    check_mixins(
        pgsql,
        second_doc,
        [mixins['mixins'][0], mixins['mixins'][1], mixins['mixins'][1]],
    )

    response_tags = helpers.fetch_tags(pgsql, 1)
    tags.sort()
    response_tags.sort()
    assert tags == response_tags


@pytest.mark.now(NOW)
@pytest.mark.config(
    EATS_ORDER_REVISION_ORIGINATOR_CHECK={
        'enabled': False,
        'allowed_for_services': [],
    },
)
async def test_raw_revision_tags_correct(
        check_create_raw_revision, pgsql, load_json,
):
    doc = load_json('revisions_without_details/revision_doc_with_mixins.json')
    tags = ['initial', 'refund']
    await check_create_raw_revision(
        order_id='test_order',
        origin_revision_id='test_revision',
        cost_for_customer='200.00',
        document=doc,
        tags=tags,
    )
    response_tags = helpers.fetch_tags(pgsql, 1)
    tags.sort()
    response_tags.sort()
    assert tags == response_tags


@pytest.mark.now(NOW)
@pytest.mark.config(
    EATS_ORDER_REVISION_ORIGINATOR_CHECK={
        'enabled': False,
        'allowed_for_services': [],
    },
)
async def test_bad_request(check_create_raw_revision):
    await check_create_raw_revision(
        order_id='test_order',
        origin_revision_id='test_revision',
        cost_for_customer='200.00',
        document={'json': True},
        tags=[],
        response_status=400,
    )


def check_mixins(pgsql, doc, mixins):
    for i in range(3):
        mixin = helpers.fetch_revision_mixin_payload(
            pgsql, 'test_order', doc['customer_services'][i]['id'],
        )
        assert mixin == mixins[i]


async def test_create_raw_revision_bad_request(taxi_eats_order_revision):
    response = await taxi_eats_order_revision.post(
        'v1/revision/raw/create', json={},
    )
    assert response.status == 400


@pytest.mark.now(NOW)
@pytest.mark.config(
    EATS_ORDER_REVISION_ORIGINATOR_CHECK={
        'enabled': True,
        'allowed_for_services': [],
    },
)
async def test_create_raw_forbidden(check_create_raw_revision):
    await check_create_raw_revision(
        'test_order',
        'test_revision',
        '200.00',
        {'json': True},
        [],
        response_status=403,
    )
