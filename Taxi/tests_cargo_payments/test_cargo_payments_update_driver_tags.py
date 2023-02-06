import pytest


def _build_diagnostics_tag_record(
        *, park_id: str, driver_id: str, ttl: str = None,
):
    tag_record = {
        'name': 'postpayment_diagnostics',
        'entity': f'{park_id}_{driver_id}',
    }
    if ttl is not None:
        tag_record['ttl'] = ttl
    return tag_record


def _build_upload_list(tags):
    return [{'entity_type': 'dbid_uuid', 'tags': tags}]


@pytest.fixture(name='call_cargo_payments_updated_driver_tags')
async def _call_cargo_payments_updated_driver_tags(stq_runner, driver_headers):
    async def _wrapper(*, park_id, driver_id):
        return await stq_runner.cargo_payments_update_driver_tags.call(
            task_id='test',
            kwargs={
                'park_id': park_id,
                'driver_id': driver_id,
                'diagnostics_tags_version': 0,  # will upload tags
            },
        )

    return _wrapper


@pytest.mark.parametrize('is_diagnostics_passed', [True, False])
async def test_tags_upload(
        state_performer_found,
        mock_tags_upload,
        call_cargo_payments_updated_driver_tags,
        confirm_diagnostics,
        is_diagnostics_passed: bool,
):
    """
        Check diagnostics dbid_uuid tags are appended/removed.
    """
    state = await state_performer_found()

    await confirm_diagnostics(is_diagnostics_passed=is_diagnostics_passed)

    await call_cargo_payments_updated_driver_tags(
        park_id=state.performer.park_id, driver_id=state.performer.driver_id,
    )

    assert len(mock_tags_upload.requests) == 1  # tags was called once
    # Check tags request (single tag to append or remove)
    last_request = mock_tags_upload.requests[0].json

    diagnostics_tag = _build_diagnostics_tag_record(
        park_id=state.performer.park_id, driver_id=state.performer.driver_id,
    )
    if is_diagnostics_passed:
        expected_append = _build_upload_list([diagnostics_tag])
        expected_remove = None
    else:
        expected_append = None
        expected_remove = _build_upload_list([diagnostics_tag])

    assert last_request.get('append') == expected_append
    assert last_request.get('remove') == expected_remove


async def test_ttl_config(
        state_performer_found,
        mock_tags_upload,
        confirm_diagnostics,
        call_cargo_payments_updated_driver_tags,
        exp_cargo_payments_diagnostics_tags,
        ttl: int = 60,  # 1 min
):
    """
        Check tag ttl is passed to tags.
    """
    state = await state_performer_found()
    await confirm_diagnostics()
    await exp_cargo_payments_diagnostics_tags(ttl=ttl)

    await call_cargo_payments_updated_driver_tags(
        park_id=state.performer.park_id, driver_id=state.performer.driver_id,
    )

    assert len(mock_tags_upload.requests) == 1  # tags was called once
    last_request = mock_tags_upload.requests[0].json

    assert last_request['append'][0]['tags'][0]['ttl'] == ttl
