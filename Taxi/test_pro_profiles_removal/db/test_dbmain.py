import pytest

from pro_profiles_removal.db import dbmain
from pro_profiles_removal.db import models as db_models
from pro_profiles_removal.entities import contractor
from pro_profiles_removal.generated.cron import cron_context as context
from test_pro_profiles_removal import conftest


@pytest.mark.parametrize(
    'profile, states, expected_count',
    [
        (
            contractor.Profile(
                conftest.TEST_PARK_ID, conftest.TEST_DRIVER_ID_1,
            ),
            [db_models.RequestState.PENDING],
            1,
        ),
    ],
)
async def test_get_requests_by_profile(
        web_context, profile, states, expected_count,
):
    rows = await dbmain.get_requests_by_profile(web_context, profile, states)
    assert len(rows) == expected_count


@pytest.mark.parametrize(
    'phones, states, expected_count',
    [
        (
            [
                f'{conftest.TEST_PARK_ID}_{conftest.TEST_DRIVER_ID_1}_phone_pd_id',  # noqa: E501
            ],
            [db_models.RequestState.PENDING],
            1,
        ),
        (
            [
                f'{conftest.TEST_PARK_ID}_{conftest.TEST_DRIVER_ID_1}_phone_pd_id',  # noqa: E501
                f'{conftest.TEST_PARK_ID}_{conftest.TEST_DRIVER_ID_2}_phone_pd_id',  # noqa: E501
            ],
            [db_models.RequestState.CREATED, db_models.RequestState.PENDING],
            3,
        ),
    ],
)
async def test_get_requests_by_phones(
        web_context, phones, states, expected_count,
):
    rows = await dbmain.get_requests_by_phones(web_context, phones, states)
    assert len(rows) == expected_count


@pytest.mark.parametrize(
    'phone, profiles',
    [
        ('phone1', [contractor.Profile('park1', 'profile1')]),
        (
            'phone1',
            [
                contractor.Profile('park1', 'profile1'),
                contractor.Profile('park1', 'profile2'),
            ],
        ),
    ],
)
async def test_create_removal_request_record(web_context, phone, profiles):
    await dbmain.create_removal_request_record(web_context, {phone: profiles})
    rows = await dbmain.get_requests_by_profile(
        web_context, profiles[0], [db_models.RequestState.CREATED],
    )
    assert len(rows) == len(profiles)


@pytest.mark.parametrize(
    'request_ids, state',
    [
        (
            [
                '87677feefc2f43ca9939b2e74f094d29',
                '2e6c83a30e7c40589516ea8437007988',
            ],
            db_models.RequestState.COMPLETED,
        ),
    ],
)
async def test_update_requests_state(
        web_context: context.Context, request_ids, state,
):
    async with web_context.pg.main_master.acquire() as conn:
        await dbmain.update_requests_state(
            web_context, state, request_ids, conn,
        )
        sql = """
            select state from pro_profiles_removal.requests
            where state = $1
        """
        rows = await conn.fetch(sql, str(state))
        request_states = [row['state'] for row in rows]
        assert request_states == [str(state)] * len(request_ids)
