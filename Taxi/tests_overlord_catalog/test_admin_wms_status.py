import pytest


def check_updated_time(all_handles_by_source, source, handle_name, expected):
    if expected['updated'][source][handle_name]['is_equal']:
        assert (
            all_handles_by_source[source]['handles'][handle_name]['updated']
            == expected['updated'][source][handle_name]['value']
        )
    else:
        assert (
            all_handles_by_source[source]['handles'][handle_name]['updated']
            != expected['updated'][source][handle_name]['value']
        )


@pytest.mark.pgsql('overlord_catalog', files=['catalog_wms_cursor.sql'])
async def test_wms_status(taxi_overlord_catalog, load_json):
    response = await taxi_overlord_catalog.post('/admin/catalog/v1/wms/status')

    assert response.status_code == 200
    response_json = response.json()

    expected = load_json('expected_wms_status.json')

    all_handles_by_source = {}

    for source_info in response_json['info']:
        source = source_info['source']
        url_to_kibana = source_info['url_to_kibana']

        all_handles_by_source[source] = {
            'handles': {},
            'url_to_kibana': url_to_kibana,
        }

        handles = all_handles_by_source[source]['handles']

        for handle_info in source_info['handlers']:
            url = handle_info['url']
            name = handle_info['name']
            cursor = handle_info['cursor']
            updated = handle_info['updated']

            handles[name] = {'url': url, 'cursor': cursor, 'updated': updated}

    for source, handles in expected['handles_info'].items():
        for handle in handles:
            name = handle['name']
            url = handle['url']
            cursor = handle['cursor']
            assert all_handles_by_source[source]['handles'][name]['url'] == url
            assert (
                all_handles_by_source[source]['handles'][name]['cursor']
                == cursor
            )

    assert (
        all_handles_by_source['assortment']['url_to_kibana']
        == expected['assortment_url_to_kibana']
    )

    assert (
        all_handles_by_source['all']['url_to_kibana']
        == expected['all_url_to_kibana']
    )

    check_updated_time(
        all_handles_by_source, 'assortment', 'wms_assortment', expected,
    )

    check_updated_time(
        all_handles_by_source, 'assortment', 'wms_assortment_items', expected,
    )
