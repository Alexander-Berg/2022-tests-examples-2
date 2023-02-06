import pytest

from eats_layout_constructor import configs


@pytest.mark.parametrize(
    'layout_id,expected_status,expected_data,expected_layouts_count,'
    'expected_layout_widgets_count',
    [
        (1, 200, {}, 3, 2),
        (2, 200, {}, 3, 0),
        (
            3,
            404,
            {
                'code': 'LAYOUT_IS_NOT_FOUND',
                'message': 'Layout with id \'3\' is not found',
            },
            None,
            None,
        ),
    ],
)
async def test_delete_layout(
        taxi_eats_layout_constructor,
        mockserver,
        pgsql,
        layout_id,
        expected_status,
        expected_data,
        expected_layouts_count,
        expected_layout_widgets_count,
):
    response = await taxi_eats_layout_constructor.delete(
        'layout-constructor/v1/constructor/layouts/',
        params={'layout_id': layout_id},
    )

    assert response.status == expected_status
    assert response.json() == expected_data
    if expected_status == 200:
        pg_cursor = pgsql['eats_layout_constructor'].cursor()
        pg_cursor.execute('SELECT count(*) FROM constructor.layouts;')
        layouts_count = pg_cursor.fetchone()[0]
        pg_cursor.execute('SELECT count(*) FROM constructor.layout_widgets;')
        layout_widgets_count = pg_cursor.fetchone()[0]
        assert layouts_count == expected_layouts_count
        assert layout_widgets_count == expected_layout_widgets_count


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1,
        'experiment_name': 'experiment_1',
    },
)
@pytest.mark.parametrize(
    'layout_id,expected_status,expected_data',
    [
        (1, 200, None),
        (
            100,
            400,
            {
                'code': 'LAYOUT_IS_ALREADY_PUBLISHED',
                'message': (
                    'Layout with slug \'layout_100\' is not editable cause it '
                    'is already published'
                ),
            },
        ),
        (
            101,
            400,
            {
                'code': 'LAYOUT_IS_ALREADY_PUBLISHED',
                'message': (
                    'Layout with slug \'layout_101\' is not editable cause it '
                    'is already published'
                ),
            },
        ),
    ],
)
async def test_delete_published_layout(
        taxi_eats_layout_constructor,
        mockserver,
        layout_id,
        expected_status,
        expected_data,
):
    await taxi_eats_layout_constructor.run_periodic_task('layout-status')
    response = await taxi_eats_layout_constructor.delete(
        'layout-constructor/v1/constructor/layouts/',
        params={'layout_id': layout_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_data is not None:
        assert data == expected_data


@configs.fallback_layout('layout_100', collection_slug='layout_101')
@pytest.mark.parametrize(
    'layout_id,expected_status,expected_data',
    [
        (1, 200, None),
        (
            100,
            400,
            {
                'code': 'LAYOUT_IS_FALLBACK',
                'message': (
                    'Layout with slug \'layout_100\' is not editable '
                    'because it is used as fallback.'
                ),
            },
        ),
        (
            101,
            400,
            {
                'code': 'LAYOUT_IS_FALLBACK',
                'message': (
                    'Layout with slug \'layout_101\' is not editable '
                    'because it is used as fallback.'
                ),
            },
        ),
    ],
)
async def test_delete_fallback_layout(
        taxi_eats_layout_constructor,
        mockserver,
        layout_id,
        expected_status,
        expected_data,
):
    await taxi_eats_layout_constructor.run_periodic_task('layout-status')
    response = await taxi_eats_layout_constructor.delete(
        'layout-constructor/v1/constructor/layouts/',
        params={'layout_id': layout_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_data is not None:
        assert data == expected_data
