def select_gateway_region_settings(pgsql):
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT gr.region_id, gr.gateway_id, '
        '  array_remove('
        '    array_agg(ves.consumer_id ORDER BY ves.consumer_id), NULL'
        '  ), '
        '  array_remove('
        '    array_agg(ves.enabled ORDER BY ves.consumer_id), NULL'
        '  ), '
        '  gr.city_id, gr.enabled_for, gr.enabled '
        'FROM regions.gateway_region_settings gr '
        'LEFT JOIN regions.vgw_enable_settings ves '
        '  ON ves.region_id = gr.region_id AND ves.gateway_id = gr.gateway_id '
        'GROUP BY gr.region_id, gr.gateway_id '
        'ORDER BY gr.region_id, gr.gateway_id',
    )
    result = cursor.fetchall()
    cursor.close()
    return result
