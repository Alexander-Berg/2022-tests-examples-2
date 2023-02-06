import pytest

from fleet_fines.generated.cron import cron_context as context_module
from fleet_fines.pg_access import docs


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
        (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', 'oid1', 'nid1', TRUE, TRUE),
        ('p1', 'd2', 'oid3', 'nid3', TRUE, TRUE),
        ('p1', 'd3', 'oid2', 'nid2', TRUE, FALSE),
        ('p1', 'd4', 'oid0', 'nid0', TRUE, TRUE),
        ('p1', 'd5', 'oid3', 'nid3', TRUE, TRUE);
    """,
    ],
)
async def test_get_dl_pd_ids(cron_context: context_module.Context):
    nums0, cursor0 = await cron_context.pg_access.docs.get_dl_pd_ids(1, '')
    assert cursor0 == 'nid0'
    assert nums0 == ['nid0']
    nums1, cursor1 = await cron_context.pg_access.docs.get_dl_pd_ids(
        100, 'nid0',
    )
    assert cursor1 == 'nid3'
    assert nums1 == ['nid1', 'nid3']
    nums2, cursor2 = await cron_context.pg_access.docs.get_vcs(100, cursor1)
    assert cursor2 == ''
    assert nums2 == []


@pytest.mark.config(FLEET_FINES_REQUEST_DLS={'max_days_from_last_drive': 15})
@pytest.mark.now('2020-08-15')
@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
        (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
         is_normalized, is_valid, last_ride_time)
    VALUES
        ('p1', 'd1', 'oid1', 'nid1', TRUE, TRUE, '2020-07-10'),
        ('p1', 'd2', 'oid3', 'nid3', TRUE, TRUE, '2020-08-10'),
        ('p1', 'd3', 'oid2', 'nid2', TRUE, FALSE, '2020-08-10'),
        ('p1', 'd4', 'oid0', 'nid0', TRUE, TRUE, '2020-08-10'),
        ('p1', 'd5', 'oid3', 'nid3', TRUE, TRUE, NULL),
        ('p1', 'd6', 'oid6', 'nid4', TRUE, TRUE, '2020-08-10');
    """,
    ],
)
async def test_get_dl_pd_ids_filtered(cron_context: context_module.Context):
    nums0, cursor0 = await cron_context.pg_access.docs.get_dl_pd_ids(1, '')
    assert cursor0 == 'nid0'
    assert nums0 == ['nid0']
    nums1, cursor1 = await cron_context.pg_access.docs.get_dl_pd_ids(
        100, 'nid0',
    )
    assert cursor1 == 'nid4'
    assert nums1 == ['nid3', 'nid4']
    nums2, cursor2 = await cron_context.pg_access.docs.get_vcs(100, cursor1)
    assert cursor2 == ''
    assert nums2 == []


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_vc
        (park_id, car_id, vc_original, vc_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'c1', 'oid0', 'nid0', TRUE, TRUE),
        ('p1', 'c2', 'oid3', 'nid3', TRUE, TRUE),
        ('p1', 'c3', 'oid2', 'nid2', TRUE, FALSE),
        ('p1', 'c4', 'oid1', 'nid1', TRUE, TRUE),
        ('p1', 'c5', 'oid3', 'nid3', TRUE, TRUE);
    """,
    ],
)
async def test_get_vcs(cron_context: context_module.Context):
    nums0, cursor0 = await cron_context.pg_access.docs.get_vcs(1, '')
    assert cursor0 == 'nid0'
    assert nums0 == ['nid0']
    nums1, cursor1 = await cron_context.pg_access.docs.get_vcs(100, 'nid0')
    assert cursor1 == 'nid3'
    assert nums1 == ['nid1', 'nid3']
    nums2, cursor2 = await cron_context.pg_access.docs.get_vcs(100, cursor1)
    assert cursor2 == ''
    assert nums2 == []


@pytest.mark.config(FLEET_FINES_REQUEST_VCS={'max_days_from_last_drive': 15})
@pytest.mark.now('2020-08-15')
@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_vc
        (park_id, car_id, vc_original, vc_normalized,
         is_normalized, is_valid, last_ride_time)
    VALUES
        ('p1', 'c1', 'oid0', 'nid0', TRUE, TRUE, '2020-08-10'),
        ('p1', 'c2', 'oid3', 'nid3', TRUE, TRUE, '2020-07-10'),
        ('p1', 'c3', 'oid2', 'nid2', TRUE, FALSE, '2020-08-10'),
        ('p1', 'c4', 'oid1', 'nid1', TRUE, TRUE, '2020-07-10'),
        ('p1', 'c5', 'oid3', 'nid3', TRUE, TRUE, NULL),
        ('p1', 'c6', 'oid4', 'nid4', TRUE, TRUE, '2020-08-10');
    """,
    ],
)
async def test_get_vcs_ride_time_filtered(
        cron_context: context_module.Context,
):
    nums0, cursor0 = await cron_context.pg_access.docs.get_vcs(1, '')
    assert cursor0 == 'nid0'
    assert nums0 == ['nid0']
    nums1, cursor1 = await cron_context.pg_access.docs.get_vcs(100, 'nid0')
    assert cursor1 == 'nid4'
    assert nums1 == ['nid4']
    nums2, cursor2 = await cron_context.pg_access.docs.get_vcs(100, cursor1)
    assert cursor2 == ''
    assert nums2 == []


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
        (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', 'oid1', NULL, FALSE, FALSE),
        ('p1', 'd2', 'oid3', NULL, FALSE, FALSE),
        ('p1', 'd3', 'oid2', NULL, TRUE, FALSE),
        ('p1', 'd4', 'oid3', NULL, FALSE, FALSE);
    """,
    ],
)
async def test_not_normalized_dl_pd_ids(cron_context: context_module.Context):
    nums = await cron_context.pg_access.docs.get_not_normalized_dl_pd_ids(100)
    assert len(nums) == 2
    assert set(nums) == {'oid1', 'oid3'}


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_vc
        (park_id, car_id, vc_original, vc_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', 'oid1', NULL, FALSE, FALSE),
        ('p1', 'd2', 'oid3', NULL, FALSE, FALSE),
        ('p1', 'd3', 'oid2', NULL, TRUE, FALSE),
        ('p1', 'd4', 'oid3', NULL, FALSE, FALSE);
    """,
    ],
)
async def test_not_normalized_vcs(cron_context: context_module.Context):
    nums = await cron_context.pg_access.docs.get_not_normalized_vcs(100)
    assert len(nums) == 2
    assert set(nums) == {'oid1', 'oid3'}


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_dl
        (park_id, driver_id, dl_pd_id_original, dl_pd_id_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', 'oid1', NULL, FALSE, FALSE),
        ('p1', 'd2', 'oid3', NULL, FALSE, FALSE),
        ('p1', 'd3', 'oid2', NULL, FALSE, FALSE),
        ('p1', 'd4', 'oid3', NULL, FALSE, FALSE);
    """,
    ],
)
async def test_store_norm_dl_pd_ids(cron_context: context_module.Context):
    batch = [
        docs.PreparedNormalizedDL('oid1', 'nid1', True),
        docs.PreparedNormalizedDL('oid2', 'nid2', False),
        docs.PreparedNormalizedDL('oid3', 'nid3', True),
    ]
    await cron_context.pg_access.docs.bulk_store_normalized_dl_pd_ids(
        batch, lambda x: x,
    )
    nums, cursor = await cron_context.pg_access.docs.get_dl_pd_ids(100, '')
    assert cursor == 'nid3'
    assert nums == ['nid1', 'nid3']


@pytest.mark.pgsql(
    'taxi_fleet_fines',
    queries=[
        """
    INSERT INTO fleet_fines.documents_vc
        (park_id, car_id, vc_original, vc_normalized,
         is_normalized, is_valid)
    VALUES
        ('p1', 'd1', 'oid1', NULL, FALSE, FALSE),
        ('p1', 'd2', 'oid3', NULL, FALSE, FALSE),
        ('p1', 'd3', 'oid2', NULL, FALSE, FALSE),
        ('p1', 'd4', 'oid3', NULL, FALSE, FALSE);
    """,
    ],
)
async def test_store_norm_vcs(cron_context: context_module.Context):
    batch = [
        docs.PreparedNormalizedVC('oid1', 'nid1', True),
        docs.PreparedNormalizedVC('oid2', 'nid2', False),
        docs.PreparedNormalizedVC('oid3', 'nid3', True),
    ]
    await cron_context.pg_access.docs.bulk_store_normalized_vcs(
        batch, lambda x: x,
    )
    nums, cursor = await cron_context.pg_access.docs.get_vcs(100, '')
    assert cursor == 'nid3'
    assert nums == ['nid1', 'nid3']
