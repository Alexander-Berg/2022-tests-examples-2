import pytest

HANDLER_PATH = 'v1/order/match_properties'
DRIVER_UDID = '5b05621ee6c22ea2654849c9'
TST_ZONE = 'burgund'
TST_DESTINATION = 'moon'
TST_ALIAS_ID = 'tstalias'


class Const:
    TARIFF_CLASS_EXPRESS = 'express'
    TARIFF_CLASS_ECONOM = 'econom'
    TARIFF_CLASS_BUSINESS = 'business'
    TARIFF_CLASS_COMFORTPLUS = 'comfortplus'
    TARIFF_CLASS_VIP = 'vip'
    TARIFF_CLASS_MINIVAN = 'minivan'
    TARIFF_CLASS_UNIVERSAL = 'universal'
    TARIFF_CLASS_POOL = 'pool'


@pytest.mark.filldb()
@pytest.mark.config(
    LONG_TRIP_CRITERIA={
        '__default__': {
            '__default__': {
                'apply': 'either',
                'distance': 25000,
                'duration': 2400,
            },
        },
    },
    ADVERSE_ZONES={
        TST_ZONE: {
            TST_DESTINATION: {'show_destination': True, 'skip_fields': ''},
        },
    },
    DRIVER_METRICS_ACTIVITY_FROM_DMS_IN_LOOKUP={
        'enabled': True,
        'timeout_ms': 1000,
    },
    DRIVER_METRICS_DISPATCH_LENGTH_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'dispatch_length_thresholds',
                                'time': [2, 10],
                            },
                        ],
                        'tags': '\'tags::boring_tag\'',
                    },
                    {
                        'action': [
                            {
                                'type': 'dispatch_length_thresholds',
                                'time': [20, 100],
                                'distance': [1000, 2000],
                                'aggregation_type': 'min',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'SimpleDispatch',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'tst_request, tst_response',
    [
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'tariff_zone': '',
                'distance_to_a': 222,
                'tariff_class': Const.TARIFF_CLASS_MINIVAN,
            },
            {'dispatch_distance_type': 'dispatch_short'},
        ),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'tariff_zone': TST_ZONE,
                'adverse_destination_zone': TST_DESTINATION,
                'distance_to_a': 222,
                'tariff_class': Const.TARIFF_CLASS_MINIVAN,
            },
            {
                'dispatch_distance_type': 'dispatch_short',
                'properties': ['adverse_zone'],
            },
        ),
        (
            {
                'unique_driver_id': '5b05621ee6c22ea2654849c0',
                'tariff_zone': TST_ZONE,
                'distance_to_a': 2000,
                'time_to_a': 30,
                'tariff_class': Const.TARIFF_CLASS_MINIVAN,
                'driver_tags': ['boring_tag'],
            },
            {'dispatch_distance_type': 'dispatch_long'},
        ),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'tariff_zone': TST_ZONE,
                'distance_to_a': 1100,
                'time_to_a': 30,
                'tariff_class': Const.TARIFF_CLASS_MINIVAN,
            },
            {'dispatch_distance_type': 'dispatch_medium'},
        ),
        (
            {
                'unique_driver_id': DRIVER_UDID,
                'tariff_zone': TST_ZONE,
                'distance_to_a': 222000,
                'route_distance': 10000,
                'route_time': 100000,
                'tariff_class': Const.TARIFF_CLASS_ECONOM,
            },
            {
                'dispatch_distance_type': 'dispatch_short',
                'trip_distance_type': 'long_trip',
            },
        ),
    ],
)
async def test_base(web_app_client, mockserver, tst_request, tst_response):
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    async def fetch_activity_value(*args, **kwargs):
        return {'items': [{'unique_driver_id': 'asd', 'value': 93}]}

    response = await web_app_client.post(HANDLER_PATH, json=tst_request)

    content = await response.json()
    assert content == tst_response

    assert fetch_activity_value.times_called
