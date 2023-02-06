import pytest

DEFAULT_LIMIT = 50
DEFAULT_PAGE = 1


@pytest.mark.parametrize(
    (
        'uuids',
        'status',
        '_type',
        'created_at_before',
        'created_at_after',
        'updated_at_before',
        'updated_at_after',
        'brand_ids',
        'place_ids',
        'limit',
        'page',
        'expected_page_count',
        'expected_element_count',
        'expected_elements_data',
    ),
    [
        (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            1,
            10,
            'all',
        ),
        (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            None,
            5,
            2,
            'first_page_limit_2',
        ),
        (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            2,
            5,
            2,
            'second_page_limit_2',
        ),
        (
            ['uuid1'],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            1,
            1,
            1,
            'uuid1_data',
        ),
        (
            ['uuid1'],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            None,
            1,
            1,
            'uuid1_data',
        ),
        (
            ['uuid1'],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            2,
            1,
            0,
            'none_data',
        ),
        (
            ['uuid1'],
            'new',
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            None,
            0,
            0,
            'none_data',
        ),
        (
            ['uuid1'],
            'in_progress',
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            None,
            1,
            1,
            'uuid1_data',
        ),
        (
            ['uuid1', 'uuid2'],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            None,
            1,
            2,
            'uuid1_uuid2_data',
        ),
        (
            ['uuid1', 'uuid2'],
            'new',
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            None,
            1,
            1,
            'uuid1_uuid2_data_status_new',
        ),
        (
            ['uuid1', 'uuid2', 'uuid3'],
            None,
            'sftp',
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            None,
            2,
            2,
            'uuid1_uuid2_uuid3_data_type_sftp_first_page',
        ),
        (
            ['uuid1', 'uuid2', 'uuid3'],
            None,
            'sftp',
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            2,
            2,
            1,
            'uuid1_uuid2_uuid3_data_type_sftp_second_page',
        ),
        (
            None,
            None,
            'sftp',
            None,
            None,
            None,
            None,
            None,
            None,
            2,
            2,
            5,
            2,
            'second_page_type_sftp',
        ),
        (
            None,
            None,
            None,
            '2021-06-21',
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            1,
            3,
            'created_at_before_2021_06_21',
        ),
        (
            None,
            None,
            None,
            '2021-06-21',
            '2021-06-20',
            None,
            None,
            None,
            None,
            None,
            None,
            1,
            2,
            'created_at_before_2021_06_21_after_2021_06_20',
        ),
        (
            None,
            None,
            None,
            None,
            None,
            '2021-06-22',
            '2021-06-20',
            None,
            None,
            None,
            None,
            1,
            3,
            'updated_at_before_2021_06_22_after_2021_06_20',
        ),
        (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            ['brand_id1', 'brand_id2'],
            None,
            None,
            None,
            1,
            3,
            'brand_ids_filtering',
        ),
        (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            ['place_id1', 'place_id2'],
            None,
            None,
            1,
            3,
            'place_ids_filtering',
        ),
    ],
)
@pytest.mark.pgsql('eats_report_sender', files=['reports.sql'])
async def test_should_find_reports(
        uuids,
        status,
        _type,
        created_at_before,
        created_at_after,
        updated_at_before,
        updated_at_after,
        brand_ids,
        place_ids,
        limit,
        page,
        expected_page_count,
        expected_element_count,
        expected_elements_data,
        load_json,
        web_app_client,
):
    response = await web_app_client.get(
        '/v1/reports',
        params=_get_params(
            brand_ids,
            created_at_after,
            created_at_before,
            limit,
            page,
            place_ids,
            _type,
            status,
            updated_at_after,
            updated_at_before,
            uuids,
        ),
    )
    assert response.status == 200
    response_json = await response.json()

    expected_limit = limit if limit else DEFAULT_LIMIT
    expected_page = page if page else DEFAULT_PAGE

    assert response_json['meta']['limit'] == expected_limit
    assert response_json['meta']['page'] == expected_page
    assert response_json['meta']['max_pages'] == expected_page_count

    assert len(response_json['reports']) == expected_element_count
    expected_elements = load_json('reports_response.json')[
        expected_elements_data
    ]['reports']

    assert response_json['reports'] == expected_elements


def _get_params(
        brand_ids,
        created_at_after,
        created_at_before,
        limit,
        page,
        place_ids,
        _type,
        status,
        updated_at_after,
        updated_at_before,
        uuids,
):
    result = {}

    if uuids:
        result['uuids'] = ','.join(uuids)
    if status:
        result['status'] = status
    if _type:
        result['_type'] = _type
    if created_at_before:
        result['created_at_before'] = created_at_before
    if created_at_after:
        result['created_at_after'] = created_at_after
    if updated_at_before:
        result['updated_at_before'] = updated_at_before
    if updated_at_after:
        result['updated_at_after'] = updated_at_after
    if brand_ids:
        result['brand_ids'] = ','.join(brand_ids)
    if place_ids:
        result['place_ids'] = ','.join(place_ids)
    if limit:
        result['limit'] = limit
    if page:
        result['page'] = page

    return result


# async def test_400_empty_params(web_app_client):
#     response = await web_app_client.get('/v1/reports')
#     assert response.status == 400
