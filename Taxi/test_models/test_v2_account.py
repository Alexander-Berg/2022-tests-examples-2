import json

import dateutil.parser
import pytest

from taxi.billing import util

from taxi_billing_accounts import models


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'json_str, expected',
    [
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.000000+00:00',
            },
            models.V2Account(
                entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
                agreement_id='AG-001',
                currency='RUB',
                sub_account='RIDE',
                expired=dateutil.parser.parse('2118-07-18T17:26:31'),
            ),
        ),
        (
            # non UTC timezone
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.000000+03:00',
            },
            models.V2Account(
                entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
                agreement_id='AG-001',
                currency='RUB',
                sub_account='RIDE',
                expired=dateutil.parser.parse('2118-07-18T14:26:31'),
            ),
        ),
    ],
)
def test_v2_account_from_json(json_str, expected):
    assert models.V2Account.from_json(json_str) == expected


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'account, expected',
    [
        # no account_id
        (
            models.V2Account(
                entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
                agreement_id='AG-001',
                currency='RUB',
                sub_account='RIDE',
                expired=dateutil.parser.parse('2118-07-18T17:26:31'),
            ),
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.000000+00:00',
            },
        ),
        # with account_id
        (
            models.V2Account(
                account_id=1000120,
                entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
                agreement_id='AG-001',
                currency='RUB',
                sub_account='RIDE',
                expired=dateutil.parser.parse('2118-07-18T17:26:31.123456'),
            ),
            {
                'account_id': 1000120,
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.123456+00:00',
            },
        ),
        # no null attributes
        (
            models.V2Account(
                account_id=1000120,
                entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
                agreement_id='AG-001',
                currency='RUB',
                sub_account='RIDE',
                expired=dateutil.parser.parse('2118-07-18T17:26:31.123456'),
                opened=dateutil.parser.parse('2118-07-18T17:26:32.123450'),
            ),
            {
                'account_id': 1000120,
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.123456+00:00',
                'opened': '2118-07-18T17:26:32.123450+00:00',
            },
        ),
    ],
)
def test_v2_account_to_json(account, expected):
    assert util.to_json(account) == json.dumps(expected)
