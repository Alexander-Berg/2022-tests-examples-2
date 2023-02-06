import pytest

from discounts_operation_calculations.repositories import segment_stats


@pytest.mark.parametrize('metric', ['city', 'discount', 'random_word', 555])
async def test_wrong_metric_names(web_app_client, metric):
    resp = await web_app_client.post(
        '/v2/suggests/1/metric/', json={'metric_name': metric},
    )

    assert resp.status == 400


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_segment_stats_all.sql', 'fill_pg_suggests_v2.sql'],
)
@pytest.mark.parametrize('metric', ['gmv', 'extra_trips', 'extra_gmv'])
async def test_not_existed_suggest(web_app_client, metric):
    resp = await web_app_client.post(
        '/v2/suggests/13/metric/', json={'metric_name': metric},
    )

    assert resp.status == 400


@pytest.mark.parametrize('metric', ['gmv', 'extra_trips'])
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_segment_stats_all.sql', 'fill_pg_suggests_v2.sql'],
)
async def test_metric_changed(web_app_client, pgsql, metric):
    suggest_id = 1
    resp = await web_app_client.post(
        f'/v2/suggests/{suggest_id}/metric/', json={'metric_name': metric},
    )

    assert resp.status == 200, await resp.json()

    internal_metric_name = segment_stats.Metric[metric].value
    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(
        f"""
        SELECT metric, {internal_metric_name}
        FROM discounts_operation_calculations.segment_stats_all
        WHERE suggest_id={suggest_id}
        """,
    )

    assert all(
        metric_col == source_metric_col
        for metric_col, source_metric_col in list(cursor)
    )


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_segment_stats_all.sql', 'fill_pg_suggests_v2.sql'],
)
async def test_extra_gmv_metric_changed(web_app_client, pgsql):
    suggest_id = 1
    resp = await web_app_client.post(
        f'/v2/suggests/{suggest_id}/metric/',
        json={'metric_name': 'extra_gmv'},
    )

    assert resp.status == 200, await resp.json()
    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(
        f"""
        SELECT metric, new_gmv - gmv
        FROM discounts_operation_calculations.segment_stats_all
        WHERE suggest_id={suggest_id}
        """,
    )

    assert all(
        metric_col == source_metric_val
        for metric_col, source_metric_val in list(cursor)
    )


@pytest.mark.parametrize('metric', ['gmv', 'extra_trips', 'extra_gmv'])
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=[
        'fill_pg_suggests_v2.sql',
        'fill_pg_calc_segment_stats_tasks.sql',
        'fill_pg_segment_stats_all.sql',
    ],
)
async def test_metric_detailed_info(web_app_client, pgsql, metric):
    suggest_id = 1
    resp = await web_app_client.post(
        f'/v2/suggests/{suggest_id}/metric/', json={'metric_name': metric},
    )

    assert resp.status == 200

    info_resp = await web_app_client.get(
        f'/v2/suggests/{suggest_id}/detailed_info',
    )

    assert info_resp.status == 200, await info_resp.json()
    content = await info_resp.json()

    assert content['metric'] == metric
