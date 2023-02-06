# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json

import pytest

from taxi.external import billing_commissions


@pytest.mark.parametrize(
    'kwargs, response, expected_method, expected_url, expected_kwargs',
    [
        (
            {
                'zone': 'moscow',
                'reference_time': datetime.datetime(2020, 2, 12, 12, 1, 2),
                'tariff_class': 'econom',
            },
            {
                'agreement': {
                    'id': '2abf062a-b607-11ea-998e-07e60204cbcf',
                    'base_rule_id': (
                        'some_fixed_percent_commission'
                        '_contract_id_in_future_end'
                    ),
                    'cancellation_settings': {
                        'park_billable_cancel_interval': ['420', '600'],
                        'pickup_location_radius': 300,
                        'user_billable_cancel_interval': ['120', '600'],
                    },
                    'cost_info': {
                        'kind': 'boundaries',
                        'max_cost': '6000',
                        'min_cost': '0',
                    },
                    'rate': {'kind': 'flat', 'rate': '42'},
                    'vat': '1.18',
                },
            },
            'POST',
            'http://billing-commissions.taxi.tst.yandex.net/v1/rebate/match',
            {
                'json': {
                    'reference_time': '2020-02-12T12:01:02+00:00',
                    'tariff_class': 'econom',
                    'zone': 'moscow',
                },
                'exponential_backoff': True,
                'retry_on_fails': True,
                'headers': {'Content-Type': 'application/json'},
                'timeout': 200,
                'log_extra': None,
            },
        ),
    ],
)
@pytest.inline_callbacks
def test_request(
        mock,
        areq_request,
        kwargs,
        response,
        expected_method,
        expected_url,
        expected_kwargs,
):
    @mock
    @areq_request
    def _dummy_request(method, url, **kwargs):
        return 200, json.dumps(response)

    data = yield billing_commissions.get_agreement(**kwargs)

    arequests_call = _dummy_request.calls[0]
    assert arequests_call['args'] == (expected_method, expected_url)
    assert arequests_call['kwargs'] == expected_kwargs
    assert data.id == response['agreement']['id']
