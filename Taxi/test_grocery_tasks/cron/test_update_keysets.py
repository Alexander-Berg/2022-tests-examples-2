import pytest

from grocery_tasks.localization_update.update_keysets import run


@pytest.mark.translations(wms_items={})
@pytest.mark.config(
    GROCERY_KEYSETS_AUTO_UPDATE=[
        'pigeon-keyset',
        'overlord-keyset',
        'discounts-keyset',
    ],
)
@pytest.mark.parametrize(
    'keysets_to_update, updated_keysets',
    [
        (
            ['pigeon-keyset', 'discounts-keyset', 'default-keyset'],
            ['pigeon-keyset', 'discounts-keyset'],
        ),
        (['default-keyset-1', 'default-keyset-2'], []),
    ],
)
async def test_keysets_updated(
        cron_context, mockserver, keysets_to_update, updated_keysets,
):
    @mockserver.json_handler('/localizations-replica/v1/keysets/diff')
    async def _mock_keysets_diff(request):
        return {'keysets': [{'id': keyset} for keyset in keysets_to_update]}

    @mockserver.json_handler('/localizations-replica/v1/keysets/update')
    async def _mock_keysets_update(request):
        assert request.json['keyset'] == updated_keysets
        return mockserver.make_response(json={}, status=200)

    await run(cron_context)

    assert _mock_keysets_diff.times_called == 1
    if updated_keysets:
        assert _mock_keysets_update.times_called == 1
    else:
        assert _mock_keysets_update.times_called == 0
