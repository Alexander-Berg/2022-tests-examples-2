import datetime

import psycopg2
import pytest

from tests_eats_business_rules.admin import commission_helper


def _pg_dttm(dttm):
    pg_tz = psycopg2.tz.FixedOffsetTimezone(offset=180)
    pg_dttm = datetime.datetime.strptime(dttm, '%Y-%m-%dT%H:%M:%S')
    return pg_dttm.replace(tzinfo=pg_tz)


async def test_commission_list_happy_path(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/commission/list'
    await (
        commission_helper.AdminCommissionTest()
        .list_request(2, 2, None, None, '2020-11-02T15:32:22+0000')
        .expected_result_list(
            [
                {
                    'rule_id': '2',
                    'applied_at': '2020-10-31T21:00:00+00:00',
                    'cancelled_at': '2020-11-02T21:00:00+00:00',
                    'client_id': '21',
                    'commission_type': 'pickup',
                    'commission_params': {
                        'commission': '8',
                        'fix_commission': '10',
                        'acquiring_commission': '1.5',
                    },
                },
                {
                    'rule_id': '7',
                    'applied_at': '2020-10-31T21:00:00+00:00',
                    'cancelled_at': '2021-10-31T21:00:00+00:00',
                    'client_id': '121',
                    'commission_type': 'picker_delivery',
                    'commission_params': {
                        'commission': '3.4',
                        'fix_commission': '0',
                        'acquiring_commission': '1',
                    },
                },
            ],
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


async def test_commission_list_default_id_happy_path(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/list'
    await (
        commission_helper.AdminCommissionTest()
        .list_request(
            None, 2, '12', 'picker_delivery', '2020-11-02T15:32:22+0000',
        )
        .expected_result_list(
            [
                {
                    'rule_id': '7',
                    'applied_at': '2020-10-31T21:00:00+00:00',
                    'cancelled_at': '2021-10-31T21:00:00+00:00',
                    'client_id': '121',
                    'commission_type': 'picker_delivery',
                    'commission_params': {
                        'commission': '3.4',
                        'fix_commission': '0',
                        'acquiring_commission': '1',
                    },
                },
            ],
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


async def test_commission_list_not_found(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/commission/list'
    await (
        commission_helper.AdminCommissionTest()
        .list_request(2, None, None, None, '2015-11-02T15:32:22+00:00')
        .should_fail(404, 'NOT_FOUND', 'Cannot find any commission')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_commission_create_happy_path(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/commission/create'
    await (
        commission_helper.AdminCommissionTest()
        .create_request(
            '2020-07-08T16:08:00+0000',
            '34',
            'place_delivery',
            {
                'commission': '10',
                'fix_commission': '250',
                'acquiring_commission': '1.1',
            },
        )
        .expected_result(
            'commission_13',
            '2',
            'place_delivery',
            '2020-07-08T16:08:00+00:00',
            None,
            {
                'commission': '10',
                'fix_commission': '250',
                'acquiring_commission': '1.1',
            },
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2021-01-01T12:00:00+0000')
async def test_commission_create_backdate_fail(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/create'
    await (
        commission_helper.AdminCommissionTest()
        .create_request(
            '2020-07-08T16:08:00+0000',
            '35',
            'place_delivery',
            {
                'commission': '10',
                'fix_commission': '250',
                'acquiring_commission': '1.1',
            },
        )
        .should_fail(400, 'FORMAT_ERROR', 'Cannot set backdated commission')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_commission_create_duplicate_fail(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/create'
    await (
        commission_helper.AdminCommissionTest()
        .create_request(
            '2020-07-08T16:08:00+00:00',
            '12',
            'place_delivery',
            {
                'commission': '10',
                'fix_commission': '250',
                'acquiring_commission': '1.1',
            },
        )
        .should_fail(
            400,
            'FORMAT_ERROR',
            'Cannot set commission. Is such counterparty already exists?',
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_commission_create_counterparty_not_found(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/create'
    await (
        commission_helper.AdminCommissionTest()
        .create_request(
            '2020-07-08T16:08:00+00:00',
            '13',
            'courier_delivery',
            {
                'commission': '10',
                'fix_commission': '250',
                'acquiring_commission': '1.1',
            },
        )
        .should_fail(
            404, 'NOT_FOUND', 'courier counterparty id == 13 not found',
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_commission_update_happy_path(taxi_eats_business_rules, pgsql):
    handler = '/admin/v1/commission/update'
    await (
        commission_helper.AdminCommissionTest()
        .update_request(
            '2020-11-30T21:00:00+00:00',
            '2021-12-01T00:00:00+00:00',
            '12',
            'place_delivery',
            {
                'commission': '4.54',
                'fix_commission': '200',
                'acquiring_commission': '0.2',
            },
        )
        .expected_result(
            'commission_13',
            '1',
            'place_delivery',
            '2021-12-01T00:00:00+00:00',
            None,
            {
                'commission': '4.54',
                'fix_commission': '200',
                'acquiring_commission': '0.2',
            },
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_commission_update_not_found_fail(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/update'
    await (
        commission_helper.AdminCommissionTest()
        .update_request(
            '2020-11-30T21:00:00+00:00',
            '2021-12-01T00:00:00+00:00',
            '15',
            'place_delivery',
            {
                'commission': '4.54',
                'fix_commission': '200',
                'acquiring_commission': '0.2',
            },
        )
        .should_fail(404, 'NOT_FOUND', 'place counterparty id == 15 not found')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_commission_update_backdate_fail(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/update'
    await (
        commission_helper.AdminCommissionTest()
        .update_request(
            '2020-11-30T21:00:00+00:00',
            '2021-11-30T21:00:00+00:00',
            '12',
            'place_delivery',
            {
                'commission': '4.54',
                'fix_commission': '200',
                'acquiring_commission': '0.2',
            },
        )
        .should_fail(400, 'FORMAT_ERROR', 'Cannot set backdated commission')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2020-01-01T12:00:00+0000')
async def test_commission_update_new_date_earlier_fail(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/update'
    await (
        commission_helper.AdminCommissionTest()
        .update_request(
            '2021-11-30T21:00:00+00:00',
            '2020-11-30T21:00:00+00:00',
            '12',
            'place_delivery',
            {
                'commission': '4.54',
                'fix_commission': '200',
                'acquiring_commission': '0.2',
            },
        )
        .should_fail(
            400,
            'FORMAT_ERROR',
            'New application date must be later than modifiable commission',
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_commission_delete_last_happy_path(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/delete'
    await (
        commission_helper.AdminCommissionTest()
        .delete_request('2020-12-01T00:00:00+00:00', '12', 'place_delivery')
        .expected_result(
            'commission_5',
            '1',
            'place_delivery',
            '2020-11-30T21:00:00+00:00',
            None,
            {
                'commission': '4.44',
                'fix_commission': '200',
                'acquiring_commission': '0.2',
            },
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )

    commission_helper.check_db_state(
        pgsql,
        '1',
        'place_delivery',
        [
            (
                1,
                _pg_dttm('2020-11-01T00:00:00'),
                _pg_dttm('2020-11-03T00:00:00'),
            ),
            (3, _pg_dttm('2020-11-03T00:00:00'), None),
        ],
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_commission_delete_middle_happy_path(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/delete'
    await (
        commission_helper.AdminCommissionTest()
        .delete_request('2020-11-03T00:00:00+00:00', '12', 'place_delivery')
        .expected_result(
            'commission_3',
            '1',
            'place_delivery',
            '2020-11-02T21:00:00+00:00',
            '2020-11-30T21:00:00+00:00',
            {
                'commission': '9',
                'fix_commission': '0',
                'acquiring_commission': '0.5',
            },
        )
        .run(taxi_eats_business_rules, pgsql, handler)
    )

    commission_helper.check_db_state(
        pgsql,
        '1',
        'place_delivery',
        [
            (
                1,
                _pg_dttm('2020-11-01T00:00:00'),
                _pg_dttm('2020-11-30T21:00:00'),
            ),
            (5, _pg_dttm('2020-12-01T00:00:00'), None),
        ],
    )


@pytest.mark.now('2021-01-01T12:00:00+0000')
async def test_commission_delete_backdated_fail(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/delete'
    await (
        commission_helper.AdminCommissionTest()
        .delete_request('2020-11-03T00:00:00+00:00', '12', 'place_delivery')
        .should_fail(400, 'FORMAT_ERROR', 'Cannot delete backdated commission')
        .run(taxi_eats_business_rules, pgsql, handler)
    )


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_commission_delete_not_found_fail(
        taxi_eats_business_rules, pgsql,
):
    handler = '/admin/v1/commission/delete'
    await (
        commission_helper.AdminCommissionTest()
        .delete_request('2020-08-03T00:00:00+00:00', '12', 'place_delivery')
        .should_fail(404, 'NOT_FOUND', 'Cannot find any commission')
        .run(taxi_eats_business_rules, pgsql, handler)
    )
