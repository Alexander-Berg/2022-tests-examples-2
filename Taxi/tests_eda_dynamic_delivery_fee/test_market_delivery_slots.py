import pytest


@pytest.mark.parametrize(
    'request_query, response_expected',
    [
        pytest.param(
            {'place_id': 1234},
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T14:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '18:00',
                        'toTime': '20:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T13:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '200',
                        'delivery_slot_interval': 240,
                        'skip_delivery_slots_count': 1,
                        'place_starts_work_at': '09:00',
                        'place_finishes_work_at': '22:00',
                    },
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET_OVERRIDE={
                        'overrides': [
                            {
                                'place_id': 1234,
                                'settings': {
                                    'delivery_cost': '100',
                                    'delivery_slot_interval': 120,
                                    'skip_delivery_slots_count': 0,
                                    'place_starts_work_at': '08:00',
                                    'place_finishes_work_at': '20:00',
                                },
                            },
                        ],
                    },
                ),
            ],
            id='order after start work override',
        ),
        pytest.param(
            {'place_id': 1234},
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T14:00:00.000+05:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '18:00',
                        'toTime': '20:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T13:11:00+05:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '200',
                        'delivery_slot_interval': 240,
                        'skip_delivery_slots_count': 1,
                        'place_starts_work_at': '09:00',
                        'place_finishes_work_at': '22:00',
                    },
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET_OVERRIDE={
                        'overrides': [
                            {
                                'place_id': 1234,
                                'settings': {
                                    'delivery_cost': '100',
                                    'delivery_slot_interval': 120,
                                    'skip_delivery_slots_count': 0,
                                    'place_starts_work_at': '08:00',
                                    'place_finishes_work_at': '20:00',
                                    'time_zone': 'Indian/Maldives',  # +05:00
                                },
                            },
                        ],
                    },
                ),
            ],
            id='order after start work override timezone',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T14:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '18:00',
                        'toTime': '20:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T13:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='order after start work',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T08:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T00:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='order before start work',
        ),
        pytest.param(
            None,
            {
                'fromDate': '17-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-17T10:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T18:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '10:00',
                        'place_finishes_work_at': '18:00',
                    },
                ),
            ],
            id='order after end work',
        ),
        pytest.param(
            None,
            {
                'fromDate': '17-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-17T10:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '11:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '11:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '13:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '13:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '15:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T17:10:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 60,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '10:00',
                        'place_finishes_work_at': '18:00',
                    },
                ),
            ],
            id='order in last slot',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T14:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '18:00',
                        'toTime': '20:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T05:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 3,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='skip slots',
        ),
        pytest.param(
            None,
            {
                'fromDate': '17-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-17T08:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T05:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 6,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='skip current day slots',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'intervals': [],
            },
            marks=[
                pytest.mark.now('2021-02-16T05:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 12,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='skip all slots',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T14:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '18:00',
                        'toTime': '20:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T13:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '21:00',
                    },
                ),
            ],
            id='skip half slot',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T10:33:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '10:33',
                        'toTime': '11:06',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '11:06',
                        'toTime': '11:39',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '10:33',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:33',
                        'toTime': '11:06',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '11:06',
                        'toTime': '11:39',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T10:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 33,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '10:00',
                        'place_finishes_work_at': '12:00',
                    },
                ),
            ],
            id='strange interval',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T10:45:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '10:45',
                        'toTime': '10:50',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '10:50',
                        'toTime': '10:55',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '10:55',
                        'toTime': '11:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:40',
                        'toTime': '10:45',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:45',
                        'toTime': '10:50',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:50',
                        'toTime': '10:55',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:55',
                        'toTime': '11:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T10:45:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 5,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '10:40',
                        'place_finishes_work_at': '11:00',
                    },
                ),
            ],
            id='small interval',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T14:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '18:00',
                        'toTime': '20:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T14:00:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='boundary values of start',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T16:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '18:00',
                        'toTime': '20:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '10:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T16:00:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='boundary values of end',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'firstDeliveryTimestamp': '2021-02-16T00:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '16-02-2021',
                        'fromTime': '00:00',
                        'toTime': '04:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '04:00',
                        'toTime': '08:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '08:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '12:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '16-02-2021',
                        'fromTime': '16:00',
                        'toTime': '20:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '00:00',
                        'toTime': '04:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '04:00',
                        'toTime': '08:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '08:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '12:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '17-02-2021',
                        'fromTime': '16:00',
                        'toTime': '20:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-16T00:00:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 240,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '00:00',
                        'place_finishes_work_at': '23:59',
                    },
                ),
            ],
            id='all day',
        ),
        pytest.param(
            None,
            {
                'fromDate': '28-02-2021',
                'toDate': '01-03-2021',
                'firstDeliveryTimestamp': '2021-02-28T18:00:00.000+03:00',
                'intervals': [
                    {
                        'date': '28-02-2021',
                        'fromTime': '18:00',
                        'toTime': '20:00',
                    },
                    {
                        'date': '01-03-2021',
                        'fromTime': '10:00',
                        'toTime': '12:00',
                    },
                    {
                        'date': '01-03-2021',
                        'fromTime': '12:00',
                        'toTime': '14:00',
                    },
                    {
                        'date': '01-03-2021',
                        'fromTime': '14:00',
                        'toTime': '16:00',
                    },
                    {
                        'date': '01-03-2021',
                        'fromTime': '16:00',
                        'toTime': '18:00',
                    },
                    {
                        'date': '01-03-2021',
                        'fromTime': '18:00',
                        'toTime': '20:00',
                    },
                ],
            },
            marks=[
                pytest.mark.now('2021-02-28T17:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '10:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='end month',
        ),
        pytest.param(
            None,
            {
                'fromDate': '16-02-2021',
                'toDate': '17-02-2021',
                'intervals': [],
            },
            marks=[
                pytest.mark.now('2021-02-16T05:11:00+03:00'),
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '23:00',
                        'place_finishes_work_at': '00:00',
                    },
                ),
            ],
            id='bad work',
        ),
    ],
)
async def test_market_delivery_slots(
        taxi_eda_dynamic_delivery_fee, request_query, response_expected,
):
    if request_query:
        query = (
            '/v1/eda-dynamic-delivery-fee/market/delivery_slots'
            '?place_id={place_id}'.format(place_id=request_query['place_id'])
        )
    else:
        query = '/v1/eda-dynamic-delivery-fee/market/delivery_slots'

    response = await taxi_eda_dynamic_delivery_fee.post(query)

    assert response.status_code == 200
    assert response.json() == response_expected
