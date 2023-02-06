from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


class TagWithTtl(NamedTuple):
    name: str
    ttl: Optional[int] = None


PROVIDER_BASE = 'driver-mode-subscription'
PROVIDER_GEOBOOKING = 'driver-mode-geobooking'


def _make_key_params_mock(mockserver):
    @mockserver.json_handler('/driver-fix/v1/view/rule_key_params')
    async def _mock_view_offer(request):
        return {
            'rules': [
                {
                    'rule_id': 'next_rule_id',
                    'key_params': {
                        'tariff_zone': 'next_zone',
                        'subvention_geoarea': 'next_area',
                        'tag': 'next_tag',
                    },
                },
                {
                    'rule_id': 'prev_rule_id',
                    'key_params': {
                        'tariff_zone': 'prev_zone',
                        'subvention_geoarea': 'prev_area',
                        'tag': 'prev_tag',
                    },
                },
            ],
        }


def check_tags_request_with_ttl(
        request: Dict[str, Any],
        expected_removed_tags: Optional[List[TagWithTtl]],
        expected_append_tags: Optional[List[TagWithTtl]],
        expected_dbid_uuid: str,
        provider: str,
):
    if expected_removed_tags:
        tags_records_remove = request.pop('remove')
        tags_set = set()
        assert len(tags_records_remove) == 1
        tags_records = tags_records_remove[0].pop('tags')
        for record in tags_records:
            tags_set.add(
                TagWithTtl(record.pop('name'), record.pop('ttl', None)),
            )
            assert record == {'entity': expected_dbid_uuid}
        assert tags_set == set(expected_removed_tags)
    if expected_append_tags:
        tags_records_append = request.pop('append')
        tags_set = set()
        assert len(tags_records_append) == 1
        tags_records = tags_records_append[0].pop('tags')
        for record in tags_records:
            tags_set.add(
                TagWithTtl(record.pop('name'), record.pop('ttl', None)),
            )
            assert record == {'entity': expected_dbid_uuid}
        assert tags_set == set(expected_append_tags)

    assert request == {'provider_id': provider}


def to_tag_with_ttl(tags: Optional[List[str]]):
    if not tags:
        return []
    return list(map(lambda tag: TagWithTtl(tag, None), tags))


def check_tags_request(
        request: Dict[str, Any],
        expected_removed_tags: Optional[List[str]],
        expected_append_tags: Optional[List[str]],
        expected_dbid_uuid: str,
        provider: str,
):
    check_tags_request_with_ttl(
        request,
        to_tag_with_ttl(expected_removed_tags),
        to_tag_with_ttl(expected_append_tags),
        expected_dbid_uuid,
        provider,
    )


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'tag_removed, tag_appened, expect_tag_remove, expect_tag_append',
    (
        pytest.param(None, None, None, None, id='no feature, no tags calls'),
        pytest.param(
            ['tag1', 'tag2'],
            None,
            ['tag1', 'tag2'],
            None,
            id='remove tags from prev mode',
        ),
        pytest.param(
            None,
            ['tag1', 'tag2'],
            None,
            ['tag1', 'tag2'],
            id='append tags to next mode',
        ),
        pytest.param(
            ['removed_tag'],
            ['appended_tag'],
            ['removed_tag'],
            ['appended_tag'],
            id='append with remove',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            ['tag1', 'tag2'],
            None,
            None,
            id='same tags optimization',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            ['tag3', 'tag2'],
            ['tag1'],
            ['tag3'],
            id='exclude same tags append',
        ),
        pytest.param(
            ['removed_tag'],
            ['appended_tag'],
            ['appended_tag'],
            ['removed_tag'],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['blocked_state.sql'],
                ),
            ],
            id='compensate append with remove',
        ),
    ),
)
async def test_subscription_saga_tags(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        tag_removed: Optional[List[str]],
        tag_appened: Optional[List[str]],
        expect_tag_remove: Optional[List[str]],
        expect_tag_append: Optional[List[str]],
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode', assign_tags=tag_appened,
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode', assign_tags=tag_removed,
                ),
            ],
        ),
    )

    taxi_config.set_values(
        dict(
            DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
                saga_tools.SAGA_SETTINGS_ENABLE_COMPENSATION
            ),
        ),
    )

    await taxi_driver_mode_subscription.invalidate_caches()

    _old_mode = 'prev_work_mode'

    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(profiles={test_profile: driver.Mode(_old_mode)})
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        return {'status': 'ok'}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if expect_tag_remove or expect_tag_append:
        upload_request = _v2_upload.next_call()['request']

        check_tags_request(
            upload_request.json,
            expect_tag_remove,
            expect_tag_append,
            test_profile.dbid_uuid(),
            PROVIDER_BASE,
        )

    assert not _v2_upload.has_calls


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'reservation.sql'],
)
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'prev_mode_features, next_mode_features, '
    'expect_tag_remove, expect_tag_append',
    (
        pytest.param(
            {},
            {'geobooking': {}},
            None,
            ['next_tag'],
            id='next mode booking tags',
        ),
        pytest.param(
            {'geobooking': {}},
            {},
            ['prev_tag'],
            None,
            id='prev mode booking tags',
        ),
        pytest.param(
            {'geobooking': {}},
            {'geobooking': {}},
            ['prev_tag'],
            ['next_tag'],
            id='prev and next mode booking tags',
        ),
    ),
)
async def test_subscription_saga_geobooking_tags(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        prev_mode_features: Dict[str, Any],
        next_mode_features: Dict[str, Any],
        expect_tag_remove: Optional[List[str]],
        expect_tag_append: Optional[List[str]],
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode', features=next_mode_features,
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode', features=prev_mode_features,
                ),
            ],
        ),
    )

    taxi_config.set_values(
        dict(
            DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
                saga_tools.SAGA_SETTINGS_ENABLE_COMPENSATION
            ),
        ),
    )
    await taxi_driver_mode_subscription.invalidate_caches()
    _old_mode = 'prev_work_mode'

    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(profiles={test_profile: driver.Mode(_old_mode)})
    scene.setup(mockserver, mocked_time)
    _make_key_params_mock(mockserver)

    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        return {'status': 'ok'}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if expect_tag_remove or expect_tag_append:
        upload_request = _v2_upload.next_call()['request']

        check_tags_request(
            upload_request.json,
            expect_tag_remove,
            expect_tag_append,
            test_profile.dbid_uuid(),
            PROVIDER_GEOBOOKING,
        )

    assert not _v2_upload.has_calls


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS={
        'important_reason': {
            'current_mode_params': {},
            'actions': {
                'assign_tags': [
                    {'name': 'many_rejects_recently', 'ttl_m': 120},
                    {'name': 'some_tag'},
                ],
            },
        },
    },
)
@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'tag_removed, tag_appened, expect_tag_remove, expect_tag_append',
    (
        pytest.param(
            None,
            None,
            None,
            [
                TagWithTtl('many_rejects_recently', 7200),
                TagWithTtl('some_tag', None),
            ],
            id='no feature, assign tags from reason',
        ),
        pytest.param(
            ['tag1'],
            ['tag2'],
            [TagWithTtl('tag1', None)],
            [
                TagWithTtl('many_rejects_recently', 7200),
                TagWithTtl('some_tag', None),
                TagWithTtl('tag2', None),
            ],
            id='with feature, assign tags from reason',
        ),
        pytest.param(
            None,
            None,
            [
                TagWithTtl('many_rejects_recently', 7200),
                TagWithTtl('some_tag', None),
            ],
            None,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['blocked_state.sql'],
                ),
            ],
            id='compensate',
        ),
    ),
)
async def test_subscription_saga_tags_from_reason(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        tag_removed: Optional[List[str]],
        tag_appened: Optional[List[str]],
        expect_tag_remove: Optional[List[TagWithTtl]],
        expect_tag_append: Optional[List[TagWithTtl]],
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode', assign_tags=tag_appened,
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode', assign_tags=tag_removed,
                ),
            ],
        ),
    )

    taxi_config.set_values(
        dict(
            DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
                saga_tools.SAGA_SETTINGS_ENABLE_COMPENSATION
            ),
        ),
    )

    await taxi_driver_mode_subscription.invalidate_caches()

    _old_mode = 'prev_work_mode'

    test_profile = driver.Profile(f'parkid2_uuid2')

    scene = scenario.Scene(profiles={test_profile: driver.Mode(_old_mode)})
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        return {'status': 'ok'}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if expect_tag_remove or expect_tag_append:
        upload_request = _v2_upload.next_call()['request']

        check_tags_request_with_ttl(
            upload_request.json,
            expect_tag_remove,
            expect_tag_append,
            test_profile.dbid_uuid(),
            PROVIDER_BASE,
        )

    assert not _v2_upload.has_calls
