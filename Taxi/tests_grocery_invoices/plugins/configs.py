# pylint: disable=C0103
import datetime

import pytest

from tests_grocery_invoices import consts
from tests_grocery_invoices import models


class Context:
    def __init__(self, experiments3, taxi_config):
        self.experiments3 = experiments3
        self.taxi_config = taxi_config

        self.set_valid_vat()

        taxi_config.set(
            GROCERY_INVOICES_DOCUMENT_GROUP_ID_BY_COUNTRY=_COUNTRY_ISO3_TO_GROUP_ID,  # noqa: E501
            GROCERY_INVOICES_DEVELOPER_EMAIL_EASY_COUNT=consts.DEVELOPER_EMAIL,
            GROCERY_INVOICES_GROCERY_UUID_EASY_COUNT=consts.GROCERY_USER_UUID,
        )

    def eats_receipts_service(self, service):
        self.experiments3.add_config(
            name='grocery_eats_receipts_service',
            consumers=['grocery-invoices/stq'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'service': service},
                },
            ],
        )

    def set_valid_vat(self, **kwargs):
        self.experiments3.add_config(
            name='grocery_invoices_valid_vat',
            consumers=['grocery-invoices/stq'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': kwargs,
                },
            ],
        )

    def easy_count_doc_request_type(self, request_type):
        self.experiments3.add_config(
            name='grocery_invoices_easy_count_document_request_type',
            consumers=['grocery-invoices/easy-count'],
            default_value={'request_type': request_type},
        )

    def grocery_invoices_russia_tin_expat_params(self):
        self.experiments3.add_config(
            name='grocery_invoices_russia_tin_expat_params',
            consumers=['grocery-invoices/stq'],
            default_value={
                'tin': consts.GROCERY_TIN,
                'main_depot_id': consts.DEPOT_ID,
            },
        )

    def split_receipts_by_supplier_tin(self, enabled):
        self.experiments3.add_config(
            name='grocery_receipts_split_receipts_by_supplier_tin',
            consumers=['grocery-invoices/stq'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enabled},
                },
            ],
        )

    def set_error_policy(
            self, error_after: datetime.timedelta, delay: datetime.timedelta,
    ):
        self.experiments3.add_config(
            name='grocery_receipts_error_policy',
            consumers=['grocery-invoices/error_policy'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value={
                'error_after_seconds': error_after.total_seconds(),
                'delay_seconds': delay.total_seconds(),
            },
        )


@pytest.fixture(name='grocery_invoices_configs', autouse=True)
def grocery_invoices_configs(experiments3, taxi_config):
    return Context(experiments3, taxi_config)


POLICY_DELAY_SECONDS = 1234
POLICY_ERROR_AFTER_SECONDS = 5678

GROCERY_RECEIPTS_POLLING_POLICY = pytest.mark.experiments3(
    name='grocery_receipts_polling_policy',
    consumers=['grocery-invoices/stq'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'delay_seconds': POLICY_DELAY_SECONDS,
                'error_after_seconds': POLICY_ERROR_AFTER_SECONDS,
            },
        },
    ],
    is_config=True,
)


def get_group_id(country: models.Country):
    return f'{country.lower_name}-group-id'


_COUNTRY_ISO3_TO_GROUP_ID = {
    country.country_iso3.lower(): get_group_id(country)
    for country in models.Country
}
