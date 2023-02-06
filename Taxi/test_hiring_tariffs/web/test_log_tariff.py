# pylint: disable=unused-variable


async def test_log(
        load_json, create_draft, create_tariff, update_tariff, log_tariff,
):
    """Получение списка ревизий тарифа"""

    tariff_v1 = await create_tariff(load_json('draft.json'))
    tariff_v2 = await update_tariff(
        tariff_id=tariff_v1['tariff_id'], data=load_json('draft_future.json'),
    )
    tariff_v3 = await update_tariff(
        tariff_id=tariff_v1['tariff_id'], data=load_json('draft.json'),
    )

    draft_v4 = await create_draft(  # noqa: F841
        data=load_json('draft.json'), tariff_id=tariff_v1['tariff_id'],
    )

    received = await log_tariff(tariff_id=tariff_v1['tariff_id'])

    assert received['time_ts'], 'Время актуальности лога установлено'
    assert len(received['revisions']) == 3, 'Лог получен'
    assert (
        received['revisions'][0]['revision'] == tariff_v3['revision']
    ), 'Действующая ревизия'
    assert (
        received['revisions'][1]['revision'] == tariff_v2['revision']
    ), 'Действующая ревизия'
    assert (
        received['revisions'][2]['revision'] == tariff_v1['revision']
    ), 'Действующая ревизия'


async def test_not_found(web_app_client):
    unknown_uuid = 'b203883efc21433e9e5a638c1e58bbdb'
    response = await web_app_client.get(
        '/v1/tariff/log/', params={'tariff_id': unknown_uuid},
    )
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'TARIFF_NOT_FOUND'
