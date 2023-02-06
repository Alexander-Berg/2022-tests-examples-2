# pylint: disable=redefined-outer-name
import pytest

from sf_data_load.generated.cron import run_cron


@pytest.mark.pgsql(
    'sf_data_load', files=('sf_data_load_last_sync_custom_process.sql',),
)
@pytest.mark.config(
    SF_DATA_LOAD_SF_RULES=[
        {
            'source': 'B2BCorpClients',
            'source_field': 'billing_id',
            'sf_api_name': 'BillingId',
            'lookup_alias': 'corp_clients',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpClients',
            'source_field': 'client_id',
            'sf_api_name': 'ClientId',
            'lookup_alias': 'corp_clients',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpClients',
            'source_field': 'name',
            'sf_api_name': 'Name',
            'lookup_alias': 'corp_clients',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpClientsService',
            'source_field': 'service_name',
            'sf_api_name': 'ServiceName',
            'lookup_alias': 'corp_clients_service',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpClientsService',
            'source_field': 'client_id',
            'sf_api_name': 'ClientIdForService',
            'lookup_alias': 'corp_clients_service',
            'load_period': 1,
        },
        {
            'source': 'B2BCorpClientsService',
            'source_field': 'is_visible',
            'sf_api_name': 'Visibility',
            'lookup_alias': 'corp_clients_service',
            'load_period': 1,
        },
    ],
    SF_DATA_LOAD_LOOKUPS={
        'corp_clients': {
            'sf_org': 'b2b',
            'sf_object': 'Account',
            'source_key': 'billing_id',
        },
        'corp_clients_service': {
            'sf_org': 'b2b',
            'sf_object': 'Account',
            'source_key': 'id_and_service_name',
        },
    },
)
async def test_get_corp_clients(mock_corp_clients, pgsql):
    await run_cron.main(
        ['sf_data_load.crontasks.custom.get_corp_clients', '-t', '0'],
    )

    cursor = pgsql['sf_data_load'].cursor()

    query = """
                SELECT
                    source_class_name,
                    source_field,
                    sf_api_field_name,
                    lookup_alias,
                    data_value
                FROM sf_data_load.loading_fields
                ORDER BY source_field;
            """

    cursor.execute(query)
    data = cursor.fetchall()
    assert data == [
        (
            'B2BCorpClients',
            'billing_id',
            'BillingId',
            'corp_clients',
            '100001',
        ),
        (
            'B2BCorpClients',
            'client_id',
            'ClientId',
            'corp_clients',
            'client_id_1',
        ),
        (
            'B2BCorpClientsService',
            'client_id',
            'ClientIdForService',
            'corp_clients_service',
            'client_id_1',
        ),
        (
            'B2BCorpClientsService',
            'client_id',
            'ClientIdForService',
            'corp_clients_service',
            'client_id_1',
        ),
        (
            'B2BCorpClientsService',
            'is_visible',
            'Visibility',
            'corp_clients_service',
            'True',
        ),
        (
            'B2BCorpClientsService',
            'is_visible',
            'Visibility',
            'corp_clients_service',
            'True',
        ),
        ('B2BCorpClients', 'name', 'Name', 'corp_clients', 'corp_client_1'),
        (
            'B2BCorpClientsService',
            'service_name',
            'ServiceName',
            'corp_clients_service',
            'Еда',
        ),
        (
            'B2BCorpClientsService',
            'service_name',
            'ServiceName',
            'corp_clients_service',
            'Такси',
        ),
    ]
