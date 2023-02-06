# pylint: disable=unused-variable


async def test_update_labels(
        load_json, create_tariff, get_tariff, update_labels_tariff,
):
    """Обновление списка меток"""

    tariff = await create_tariff(load_json('draft.json'))

    received = await update_labels_tariff(
        tariff_id=tariff['tariff_id'],
        revision=tariff['revision'],
        labels=['new1', 'new2'],
    )

    assert received['tariff_id'] == tariff['tariff_id'], 'Тариф тот же'
    assert received['revision'] == tariff['revision'], 'Получена та же ревизия'
    assert received['labels'] == ['new1', 'new2'], 'Метки обновлены'

    received2 = await get_tariff(tariff_id=tariff['tariff_id'])
    assert received2['labels'] == [
        'new1',
        'new2',
    ], 'Метки действительно обновлены'


async def test_clear_labels(
        load_json, create_tariff, get_tariff, update_labels_tariff,
):
    """Обновление на пустой список меток"""
    tariff = await create_tariff(load_json('draft.json'))

    received = await update_labels_tariff(
        tariff_id=tariff['tariff_id'], revision=tariff['revision'], labels=[],
    )

    assert received['tariff_id'] == tariff['tariff_id'], 'Тариф тот же'
    assert received['revision'] == tariff['revision'], 'Получена та же ревизия'
    assert received['labels'] == [], 'Метки очищены'


async def test_not_found(web_app_client):
    unknown_uuid = 'b203883efc21433e9e5a638c1e58bbdb'
    response = await web_app_client.post(
        '/v1/tariff/labels/',
        json={
            'tariff_id': unknown_uuid,
            'revision': 1,
            'labels': ['new1', 'new2'],
        },
    )
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'TARIFF_NOT_FOUND'
