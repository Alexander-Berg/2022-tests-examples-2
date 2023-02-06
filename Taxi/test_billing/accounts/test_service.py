import datetime

import pytest

from billing.accounts import service
from billing.tests import mocks


async def test_entities_get_or_create():
    entities = mocks.TestEntities()
    create = service.EntityCreateRequest(
        external_id='external_id', kind='kind',
    )
    expected_entity = service.Entity(external_id='external_id', kind='kind')
    actual_entity = await entities.get_or_create(create)
    assert actual_entity == expected_entity
    create_another = service.EntityCreateRequest(
        external_id='external_id', kind='kind2',
    )
    actual_entity = await entities.get_or_create(create_another)
    assert actual_entity == expected_entity


async def test_entities_get_or_create_many():
    entities = mocks.TestEntities()
    create_1 = service.EntityCreateRequest(
        external_id='external_id_1', kind='kind',
    )
    create_2 = service.EntityCreateRequest(
        external_id='external_id_2', kind='kind',
    )
    actual_entity = await entities.get_or_create_many([create_1, create_2])
    assert actual_entity == [
        service.Entity(external_id='external_id_1', kind='kind'),
        service.Entity(external_id='external_id_2', kind='kind'),
    ]
    create_3 = service.EntityCreateRequest(
        external_id='external_id_3', kind='kind',
    )
    actual_entity = await entities.get_or_create_many(
        [create_1, create_2, create_3],
    )
    assert actual_entity == [
        service.Entity(external_id='external_id_1', kind='kind'),
        service.Entity(external_id='external_id_2', kind='kind'),
        service.Entity(external_id='external_id_3', kind='kind'),
    ]


@pytest.mark.config(BILLING_ACCOUNTS_SEARCH_ACCOUNT_LIMIT=1)
async def test_accounts_get_or_create_many(
        library_context, do_mock_billing_accounts,
):
    do_mock_billing_accounts()
    # test create
    create_1 = service.AccountCreateRequest(
        entity_external_id='entity_external_id_1',
        agreement_id='agreement_id',
        currency='currency',
        sub_account='sub_account',
        expired=service.MAX_ACCOUNT_EXPIRY_DATE,
    )
    create_2 = service.AccountCreateRequest(
        entity_external_id='entity_external_id_2',
        agreement_id='agreement_id',
        currency='currency',
        sub_account='sub_account',
        expired=service.MAX_ACCOUNT_EXPIRY_DATE,
    )
    actual = await library_context.accounts.get_or_create_many(
        [create_1, create_2],
    )
    assert actual == [
        service.Account(
            id=0,
            entity_external_id='entity_external_id_1',
            agreement_id='agreement_id',
            currency='currency',
            sub_account='sub_account',
        ),
        service.Account(
            id=1,
            entity_external_id='entity_external_id_2',
            agreement_id='agreement_id',
            currency='currency',
            sub_account='sub_account',
        ),
    ]

    # test get and create
    create_3 = service.AccountCreateRequest(
        entity_external_id='entity_external_id_3',
        agreement_id='agreement_id',
        currency='currency',
        sub_account='sub_account',
        expired=service.MAX_ACCOUNT_EXPIRY_DATE,
    )
    actual = await library_context.accounts.get_or_create_many(
        [create_1, create_2, create_3],
    )
    assert actual == [
        service.Account(
            id=0,
            entity_external_id='entity_external_id_1',
            agreement_id='agreement_id',
            currency='currency',
            sub_account='sub_account',
        ),
        service.Account(
            id=1,
            entity_external_id='entity_external_id_2',
            agreement_id='agreement_id',
            currency='currency',
            sub_account='sub_account',
        ),
        service.Account(
            id=2,
            entity_external_id='entity_external_id_3',
            agreement_id='agreement_id',
            currency='currency',
            sub_account='sub_account',
        ),
    ]


@pytest.mark.config(BILLING_ACCOUNTS_JOURNAL_REPLICATION_LAG_MS=500)
async def test_get_replication_lag(library_context):
    assert library_context.journal.replication_lag == datetime.timedelta(
        milliseconds=500,
    )
