# pylint: disable=C0302
import pytest

from tests_subvention_schedule import utils

GEO_NODES = [
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
    {
        'name': 'br_russia',
        'name_en': 'Russia',
        'name_ru': 'Россия',
        'node_type': 'root',
        'parent_name': 'br_root',
        'region_id': '225',
    },
    {
        'name': 'br_moscow',
        'name_en': 'Moscow',
        'name_ru': 'Москва',
        'node_type': 'root',
        'parent_name': 'br_russia',
        'tariff_zones': ['moscow'],
    },
    {
        'name': 'br_spb',
        'name_en': 'St. Petersburg',
        'name_ru': 'Cанкт-Петербург',
        'node_type': 'root',
        'parent_name': 'br_russia',
        'tariff_zones': ['spb'],
        'region_id': '2',
    },
    {
        'name': 'br_almaty',
        'name_en': 'Almaty',
        'name_ru': 'Алматы',
        'node_type': 'root',
        'parent_name': 'br_russia',
        'tariff_zones': ['almaty'],
        'region_id': '162',
    },
]


async def update_rule_test_base(
        rules,
        closed,
        original_db,
        expected_db,
        expected_last_updated,
        expected_update_calls,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        updates_throws_call=None,
        check_bsx_calls=True,
        mocked_time=None,
        bsx_count_responses=None,
):
    bsx.reset()

    if updates_throws_call:
        bsx.set_updates_throws_call(updates_throws_call)

    if bsx_count_responses:
        bsx.set_count_answers(bsx_count_responses)

    if rules:
        bsx.set_rules(load_json(rules)['rules'][0])
    bsx.set_updated_rules(load_json(closed)['rules'])

    if original_db:
        utils.load_db(pgsql, load_json(original_db), mocked_time)

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': 'update-schedules'},
        )
    ).status_code == (500 if updates_throws_call else 200)

    assert utils.get_schedules(pgsql) == load_json(expected_db)

    if check_bsx_calls:
        assert bsx.updates.times_called == len(expected_update_calls)
        for call in expected_update_calls:
            assert bsx.updates.next_call()['request_data'].json == call

    assert utils.check_update_time_valid(pgsql)
    assert utils.get_last_updated(pgsql) == [(expected_last_updated,)]


EXPECTED_CALLS = [
    {
        'cursor': {},
        'limit': 100,
        'time_range': {
            'end': '2021-02-01T08:50:00+00:00',
            'start': '2020-01-31T21:00:00+00:00',
        },
    },
]


@pytest.mark.now('2021-02-01T12:00:00+0300')
@pytest.mark.geo_nodes(GEO_NODES)
@pytest.mark.experiments3(filename='experiment_use_masks.json')
@pytest.mark.config(
    USE_TAGS_FOR_UPDATE=True,
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
    },
    CLAMP_ITEMS_TO_DESCRIPTOR_BEGIN=True,
    UPDATE_JOB_SETTINGS={
        'update_delay': 600,
        'batch_size': 100,
        'process_updates_type': 'atomic',
        'process_descriptors_type': 'atomic',
    },
)
@pytest.mark.parametrize(
    'updated, original_db, updates_throws_call,'
    'count_responses, expected_db, expected_last_updated',
    [
        (
            'simple_rule_created_no_tag.json',
            'simple_rule_db.json',
            False,
            None,
            'simple_rule_db.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_created_tag.json',
            'simple_rule_db.json',
            False,
            None,
            'expected_db_created_tag.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_created_tag_later.json',
            'simple_rule_db.json',
            False,
            None,
            'expected_db_created_tag_later.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_created_tag_diff_time.json',
            'simple_rule_db.json',
            False,
            None,
            'expected_db_created_tag_diff_time.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_created_2_tags.json',
            'simple_rule_db.json',
            False,
            None,
            'expected_db_created_2_tags.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_created_2_tags_diff_time.json',
            'simple_rule_db.json',
            False,
            None,
            'expected_db_created_2_tags_diff_time.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_closed_unused_tag.json',
            'simple_rule_db_with_tags.json',
            False,
            None,
            'simple_rule_db_with_tags.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_closed_tag.json',
            'simple_rule_db_with_tags.json',
            False,
            None,
            'expected_db_closed_tag.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_closed_2_tags.json',
            'simple_rule_db_with_tags.json',
            False,
            None,
            'expected_db_closed_2_tags.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_closed_2_tags_diff_time.json',
            'simple_rule_db_with_tags.json',
            False,
            [0, 1],
            'expected_db_closed_2_tags_diff_time_only_1st.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_closed_2_tags_diff_time.json',
            'simple_rule_db_with_tags.json',
            False,
            [1, 0],
            'expected_db_closed_2_tags_diff_time_only_2nd.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_closed_2_tags_diff_time.json',
            'simple_rule_db_with_tags_updating.json',
            False,
            None,
            'expected_db_closed_2_tags_diff_time_updating.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_closed_2_tags_diff_time.json',
            'simple_rule_db_with_tags_updating_future.json',
            True,
            None,
            'simple_rule_db_with_tags_updating_future.json',
            '2020-01-31 21:00:00',
        ),
        (
            'simple_rule_closed_2_tags_diff_time.json',
            'simple_rule_db_with_tags_updating_past.json',
            False,
            None,
            'expected_db_closed_2_tags_diff_time_updating_past.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_created_tag.json',
            'simple_rule_db_inf.json',
            False,
            None,
            'expected_db_inf.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_created_tag.json',
            'expected_active_db_inf.json',
            False,
            None,
            'expected_active_db_inf.json',
            '2021-02-01 08:50:00',
        ),
        (
            'simple_rule_created_tag_3.json',
            'expected_active_db_inf.json',
            False,
            None,
            'expected_db_inf_t3.json',
            '2021-02-01 08:50:00',
        ),
    ],
)
@pytest.mark.suspend_periodic_tasks('update-job-sharded-0')
async def test_mask_pre_update(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        updated,
        original_db,
        updates_throws_call,
        count_responses,
        expected_db,
        expected_last_updated,
):
    utils.set_last_updated(pgsql, '2020-01-31 21:00:00')
    await update_rule_test_base(
        updated,
        updated,
        original_db,
        expected_db,
        expected_last_updated,
        EXPECTED_CALLS,
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        bsx_count_responses=count_responses,
        updates_throws_call=updates_throws_call,
    )
    # testsuite запускает 'update-job-sharded-0' после завершения теста
    # джоба видит данные в sch.affected_schedules и начинает их обновлять
    # и следующий тест падает, тк джоба добаляет неожиданные данные
    utils.clean_db(pgsql)


@pytest.mark.now('2020-02-01T12:00:00+0300')
@pytest.mark.geo_nodes(GEO_NODES)
@pytest.mark.experiments3(filename='experiment_use_masks.json')
@pytest.mark.config(
    USE_TAGS_FOR_UPDATE=True,
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
        'activate_masks_job': {'enabled': True, 'update_period': 100},
    },
    CLAMP_ITEMS_TO_DESCRIPTOR_BEGIN=True,
    UPDATE_JOB_SETTINGS={
        'update_delay': 600,
        'batch_size': 100,
        'number_of_items_per_iteration': 1,
        'process_updates_type': 'atomic',
        'process_descriptors_type': 'atomic',
    },
)
@pytest.mark.parametrize(
    'original_db, expected_db',
    [
        (
            'predef_db_created_tag_2_classes.json',
            'expected_updated_db_created_tag_2_classes.json',
        ),
        ('predef_db_created_tag.json', 'expected_updated_db_created_tag.json'),
        (
            'predef_db_created_tag_same_day.json',
            'expected_updated_db_created_tag_same_day.json',
        ),
        (
            'predef_db_created_2tags.json',
            'expected_updated_db_created_2tags.json',
        ),
        (
            'predef_db_created_2tags2.json',
            'expected_updated_db_created_2tags2.json',
        ),
        ('expected_db_inf.json', 'expected_active_db_inf.json'),
    ],
)
@pytest.mark.suspend_periodic_tasks('update-job-sharded-0')
async def test_update(
        taxi_subvention_schedule,
        pgsql,
        bsx,
        mocked_time,
        load_json,
        original_db,
        expected_db,
):
    utils.load_db(pgsql, load_json(original_db), mocked_time)
    bsx.set_updated_rules(load_json('simple_rule_created_2.json')['rules'])

    response = await taxi_subvention_schedule.post(
        'service/cron', json={'task_name': 'activate-masks'},
    )
    assert response.status_code == 200

    assert utils.get_schedules(pgsql) == load_json(expected_db)
