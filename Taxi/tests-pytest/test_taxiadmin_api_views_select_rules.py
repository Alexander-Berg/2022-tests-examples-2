import json
import pytest

from django import test as django_test

from taxi.core import async


@pytest.mark.parametrize(
    'rule', [
        (
            {
                "is_personal": False,
                "time_range": {
                    "started_before_inclusive": "2018-05-01T13:00:00.000+00:00",
                    "ended_after_inclusive": "2018-05-01T13:00:00.000+00:00"
                }
            }
        ),
        (
            {
                "is_personal": True,
                "time_range": {
                    "started_before_inclusive": "2018-05-01T13:00:00.000+00:00",
                    "ended_after_inclusive": "2018-05-01T13:00:00.000+00:00"
                },
                "drivers": [
                    {
                        "unique_driver_id": "some_id"
                    }
                ],
                "types": [
                    "daily_guarantee"
                ]
            }
        )
    ]
)
@pytest.mark.asyncenv('blocking')
def test_select_subvention_rules(patch, rule):

    @patch('taxi.external.subventions.select_subvention_rules')
    @async.inline_callbacks
    def select_subvention_rules(data, **kwargs):
        yield async.return_value({})

    test_client = django_test.Client()
    response = test_client.post(
        '/api/subventions/select_rules/',
        data=json.dumps(rule),
        content_type='application/json'
    )

    assert response.status_code == 200


@pytest.mark.parametrize('billing_response', [
    (
        {
        "subventions": [
            {
                "taxirate": "TAXIRATE-15",
                "workshift": {
                    "start": "00:00",
                    "end": "23:00"
                },
                "currency": "RUB",
                "rate_on_order_per_minute": "1.5",
                "rate_free_per_minute": "10",
                "end": "2018-05-29T21:00:00.000000+00:00",
                "log": [
                    {
                        "start": "2018-01-10T21:00:00.000000+00:00",
                        "login": "username",
                        "end": "2018-05-29T21:00:00.000000+00:00",
                        "updated": "2019-01-29T16:06:45.196000+00:00",
                        "ticket": "TAXIRATE-15"
                    }
                ],
                "subvention_rule_id": "_id/5c507a15ca0d425619d22699",
                "profile_payment_type_restrictions": "any",
                "start": "2018-01-10T21:00:00.000000+00:00",
                "min_online_minutes": "10",
                "is_personal": False,
                "driver_points": "10",
                "type": "geo_booking",
                "tariff_classes": [],
                "status": "enabled",
                "updated": "2019-08-11T19:59:58.350000+00:00",
                "tags": ["tag1"],
                "hours": [],
                "has_commission": False,
                "tariff_zones": ["moscow"],
                "week_days": [
                    "mon",
                    "tue",
                    "wed",
                    "thu",
                    "fri",
                    "sat",
                    "sun"
                ],
                "order_payment_type": None,
                "time_zone": {
                    "id": "Europe/Moscow",
                    "offset": "+03:00"
                },
                "cursor":
                    "2018-05-29T21:00:00.000000+00:00/5c507a15ca0d425619d22699",
                "min_activity_points": "10",
                "payment_type": "guarantee",
                "geoareas": ["msk-big"],
                "visible_to_driver": True,
            },
        ]}
    ),
])
@pytest.mark.asyncenv('blocking')
def test_select_subvention_rules_geo_booking(patch, billing_response):

    request = {
        "is_personal": False,
        "tariff_zone": "moscow",
        "time_range": {
            "ended_before": "9999-12-31T23:59:59.000+00:00"
        },
        "types": [
            "geo_booking"
        ]
    }

    @patch('taxi.external.subventions.select_subvention_rules')
    @async.inline_callbacks
    def select_subvention_rules(data, **kwargs):
        yield async.return_value(billing_response)

    test_client = django_test.Client()
    response = test_client.post(
        '/api/subventions/select_rules/',
        data=json.dumps(request),
        content_type='application/json'
    )
    assert response.status_code == 200
    response_content = json.loads(response.content)
    assert response_content == billing_response
