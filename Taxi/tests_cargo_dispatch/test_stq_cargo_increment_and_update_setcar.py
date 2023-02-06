import dataclasses

import pytest


@dataclasses.dataclass
class WaybillVersions:
    taximeter_state_version: int
    revision: int


@pytest.fixture(name='fetch_waybill_versions')
async def _fetch_waybill_versions(pgsql):
    def wrapper(waybill_ref):
        cursor = pgsql['cargo_dispatch'].cursor()

        cursor.execute(
            """
            SELECT taximeter_state_version, revision
            FROM cargo_dispatch.waybills
            WHERE external_ref = %s
        """,
            (waybill_ref,),
        )
        rows = cursor.fetchall()
        if rows is None:
            raise RuntimeError(
                'waybill is not found' + f'waybill_ref: {waybill_ref}',
            )
        assert len(rows) == 1
        row = rows[0]
        return WaybillVersions(taximeter_state_version=row[0], revision=row[1])

    return wrapper


async def test_happy_path(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        read_waybill_info,
        fetch_waybill_versions,
        waybill_id='waybill_fb_3',
        driver_profile_id='driver_id_1',
        park_id='park_id_1',
):
    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    old_versions = fetch_waybill_versions(waybill_id)

    await stq_runner.cargo_increment_and_update_setcar_state_version.call(
        task_id='test',
        kwargs={
            'cargo_order_id': cargo_order_id,
            'driver_profile_id': driver_profile_id,
            'park_id': park_id,
        },
    )

    new_versions = fetch_waybill_versions(waybill_id)
    assert (
        new_versions.taximeter_state_version
        == old_versions.taximeter_state_version + 1
    )
    assert new_versions.revision == old_versions.revision + 1

    assert stq.cargo_update_setcar_state_version.times_called == 1
    stq_call = stq.cargo_update_setcar_state_version.next_call()
    assert stq_call['id'] == f'{cargo_order_id}_park_id_1_driver_id_1'
    assert stq_call['kwargs']['driver_profile_id'] == driver_profile_id
    assert stq_call['kwargs']['park_id'] == park_id
    assert stq_call['kwargs']['send_taximeter_push']


async def test_order_not_found(stq_runner, stq):
    await stq_runner.cargo_increment_and_update_setcar_state_version.call(
        task_id='test',
        kwargs={
            'cargo_order_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            'driver_profile_id': 'driver_id_1',
            'park_id': 'park_id_1',
        },
    )

    assert stq.cargo_update_setcar_state_version.times_called == 0
