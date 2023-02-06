import datetime
import typing

import pytest

from eats_courier_scoring.common import entities
from eats_courier_scoring.common import greenplum as greenplum_module
from test_eats_courier_scoring import consts


GP_SCHEMAS = [
    'eda_cdm_marketplace/dm_order.sql',
    'eda_cdm_quality/fct_executor_fault.sql',
    'eda_ods_bigfood/courier.sql',
    'eda_ods_bigfood/courier_deactivation_info.sql',
    'eda_ods_bigfood/courier_deactivation_reason.sql',
    'eda_ods_bigfood/courier_meta_data.sql',
    'eda_ods_bigfood/place_delivery_zone.sql',
    'eda_ods_bigfood/region.sql',
    'taxi_ods_dbdrivers/executor_profile.sql',
]

GP_REQUEST_SETTING: typing.Dict[str, typing.Any] = {
    'last_order_days': 10,
    'max_count_orders': 100,
    'min_count_orders': 1,
    'orders_window_days': 60,
}


def defect(
        defect_type: str, order_id: int = 101, courier_id: int = 1,
) -> entities.Defect:
    return entities.Defect(
        courier_id=courier_id,
        order_id=order_id,
        order_nr=f'{order_id}{order_id}-{order_id}{order_id}'
        if order_id
        else None,
        defect_type=entities.DefectType(defect_type),
        defect_dttm=datetime.datetime(2020, 9, 19, 8),
        crm_comment=None,
        our_refund_total_lcy=0,
        incentive_refunds_lcy=0,
        incentive_rejected_order_lcy=0,
    )


def courier_model(
        courier_id: int,
        n_orders_last_period: int,
        date_last_order: datetime.datetime,
        date_first_order: datetime.datetime,
) -> entities.CourierModel:
    return entities.CourierModel(
        courier_id=courier_id,
        courier_username=f'Username Courier {courier_id}',
        courier_type='courier_type',
        work_status='working',
        pool_name='eda',
        region_id=777,
        region_name='Москва',
        n_orders_last_period=n_orders_last_period,
        courier_uuid=f'courier_uuid{courier_id}',
        courier_dbid=f'courier_dbid{courier_id}',
        driver_license_pd_id=f'license_id{courier_id}',
        date_last_order=date_last_order,
        date_first_order=date_first_order,
    )


@pytest.mark.pgsql('eats_courier_scoring', files=GP_SCHEMAS)
async def test_void_greenplum(cron_context):
    setting = cron_context.config.EATS_COURIER_SCORING_DEFECTS_SETTINGS
    greenplum = greenplum_module.GreenplumDefectOrdersContext(
        cron_context, setting=setting,
    )
    couriers_models, defects = await greenplum.load_couriers_and_defects(
        use_max_count_limit=False,
    )
    assert not couriers_models
    assert not defects

    couriers_models, defects = await greenplum.load_couriers_and_defects(
        use_max_count_limit=True,
    )
    assert not couriers_models
    assert not defects


@pytest.mark.pgsql('eats_courier_scoring', files=GP_SCHEMAS + ['courier.sql'])
@pytest.mark.parametrize(
    'settings,expected_models',
    [
        pytest.param(
            dict(GP_REQUEST_SETTING),
            [
                courier_model(
                    courier_id=1,
                    n_orders_last_period=1,
                    date_last_order=datetime.datetime(2020, 9, 19, 8, 0),
                    date_first_order=datetime.datetime(2020, 9, 19, 8, 0),
                ),
                courier_model(
                    courier_id=2,
                    n_orders_last_period=1,
                    date_last_order=datetime.datetime(2020, 9, 19, 8, 0),
                    date_first_order=datetime.datetime(2020, 9, 19, 8, 0),
                ),
            ],
            marks=[pytest.mark.now('2020-09-20 08:00:00')],
            id='nullifying disabled',
        ),
        pytest.param(
            dict(GP_REQUEST_SETTING),
            [
                courier_model(
                    courier_id=1,
                    n_orders_last_period=1,
                    date_last_order=datetime.datetime(2020, 9, 19, 8, 0),
                    date_first_order=datetime.datetime(2020, 9, 19, 8, 0),
                ),
                courier_model(
                    courier_id=2,
                    n_orders_last_period=4,
                    date_last_order=datetime.datetime(2020, 9, 23, 12, 0),
                    date_first_order=datetime.datetime(2020, 9, 19, 8, 0),
                ),
            ],
            marks=[pytest.mark.now('2020-09-25 12:00:00')],
            id='nullifying disabled, date is 2020-09-25',
        ),
        pytest.param(
            {
                **GP_REQUEST_SETTING,
                'nullifying_order_list_blocking_reasons': ['oko'],
            },
            [
                courier_model(
                    courier_id=1,
                    n_orders_last_period=1,
                    date_last_order=datetime.datetime(2020, 9, 19, 8, 0),
                    date_first_order=datetime.datetime(2020, 9, 19, 8, 0),
                ),
            ],
            marks=[pytest.mark.now('2020-09-20 12:00:00')],
            id='nullifying enabled, only oko reason, date is 2020-09-20',
        ),
        pytest.param(
            {
                **GP_REQUEST_SETTING,
                'nullifying_order_list_blocking_reasons': ['oko'],
            },
            [
                courier_model(
                    courier_id=1,
                    n_orders_last_period=1,
                    date_last_order=datetime.datetime(2020, 9, 19, 8, 0),
                    date_first_order=datetime.datetime(2020, 9, 19, 8, 0),
                ),
                courier_model(
                    courier_id=2,
                    n_orders_last_period=3,
                    date_last_order=datetime.datetime(2020, 9, 23, 12, 0),
                    date_first_order=datetime.datetime(2020, 9, 23, 8, 0),
                ),
            ],
            marks=[pytest.mark.now('2020-09-25 12:00:00')],
            id='nullifying enabled, only oko reason, date is 2020-09-25',
        ),
        pytest.param(
            {
                **GP_REQUEST_SETTING,
                'nullifying_order_list_blocking_reasons': ['oko', 'other'],
            },
            [
                courier_model(
                    courier_id=1,
                    n_orders_last_period=1,
                    date_last_order=datetime.datetime(2020, 9, 19, 8, 0),
                    date_first_order=datetime.datetime(2020, 9, 19, 8, 0),
                ),
                courier_model(
                    courier_id=2,
                    n_orders_last_period=2,
                    date_last_order=datetime.datetime(2020, 9, 23, 12, 0),
                    date_first_order=datetime.datetime(2020, 9, 23, 10, 0),
                ),
            ],
            marks=[pytest.mark.now('2020-09-25 12:00:00')],
            id='nullifying enabled, multiple reasons, date is 2020-09-25',
        ),
        pytest.param(
            {
                **GP_REQUEST_SETTING,
                'nullifying_order_list_blocking_reasons': ['oko', 'other'],
                'orders_window_days': 1,
            },
            [
                courier_model(
                    courier_id=2,
                    n_orders_last_period=1,
                    date_last_order=datetime.datetime(2020, 9, 26, 10, 0),
                    date_first_order=datetime.datetime(2020, 9, 26, 10, 0),
                ),
            ],
            marks=[pytest.mark.now('2020-09-26 12:00:00')],
            id='nullifying enabled, multiple reasons, but orders_window_days'
            ' has higher priority, date is 2020-09-26',
        ),
    ],
)
async def test_not_defects(
        cron_context,
        settings: typing.Dict[str, typing.Any],
        expected_models: typing.List[entities.CourierModel],
):
    greenplum = greenplum_module.GreenplumDefectOrdersContext(
        cron_context, setting=settings,
    )
    couriers_models, defects = await greenplum.load_couriers_and_defects(
        use_max_count_limit=False,
    )
    assert len(couriers_models) == len(expected_models)
    for idx, expected_model in enumerate(expected_models):
        assert couriers_models[idx] == expected_model
    assert not defects


def param_defect(defect_type: str):
    return pytest.param(
        defect_type,
        marks=[
            pytest.mark.pgsql(
                'eats_courier_scoring', files=[f'defects/{defect_type}.sql'],
            ),
        ],
    )


@pytest.mark.now('2020-09-20 08:00:00')
@pytest.mark.config(
    EATS_COURIER_SCORING_DEFECT_TYPES=consts.EATS_COURIER_SCORING_DEFECT_TYPES,
)
@pytest.mark.pgsql('eats_courier_scoring', files=GP_SCHEMAS + ['courier.sql'])
@pytest.mark.parametrize(
    ('defect_type',),
    (
        param_defect('cancel_delay'),
        param_defect('cancel_not_connected_with_courier'),
        param_defect('cancel_postpayment'),
        param_defect('courier_denial'),
        param_defect('damaged_order'),
        param_defect('delay_short'),
        param_defect('fake_gps'),
        param_defect('force_majeure'),
        param_defect('frod_last_status'),
        param_defect('frod_not_delivered'),
        param_defect('frod_waiting_time'),
        param_defect('incorrect_status_contact'),
        param_defect('irrelevant_contact_waiting'),
        param_defect('long_in_rest'),
        param_defect('mismatch_orders'),
        param_defect('order_item_lost'),
        param_defect('taxi_contact'),
        param_defect('vehicle_change_contact'),
        param_defect('covid_fault'),
    ),
)
async def test_defects(cron_context, defect_type):
    greenplum = greenplum_module.GreenplumDefectOrdersContext(
        cron_context, setting=GP_REQUEST_SETTING,
    )
    _, defects = await greenplum.load_couriers_and_defects(
        use_max_count_limit=False,
    )
    assert len(defects) == 1
    assert defects[0] == defect(defect_type)
