def check_data_count(data, charts_len, points_len):
    assert len(data['charts']) == charts_len
    for chart in data['charts']:
        assert len(chart['points_data']) == points_len


def check_data(
        data,
        status,
        metrics_total_value,
        metrics_delta_value,
        metrics_values,
        html,
        total_value,
        restapp_link,
        extra_content,
):
    if html:
        assert data['html_content'] == html
    if total_value:
        assert data['widget_total_value']['title'] == total_value
    if restapp_link:
        assert data['restapp_link'] == restapp_link
    for chart in range(len(data['charts'])):
        if metrics_total_value:
            assert (
                data['charts'][chart]['total_value']['title']
                == metrics_total_value[chart]
            )
        if metrics_delta_value:
            assert (
                data['charts'][chart]['delta_value']['title']
                == metrics_delta_value[chart]
            )
        for point in range(len(data['charts'][chart]['points_data'])):
            assert (
                data['charts'][chart]['points_data'][point]['value']
                == metrics_values[point][chart]
            )
            if status:
                assert (
                    data['charts'][chart]['points_data'][point]['status']
                    == status[point]
                )
    if extra_content:
        assert data['extra_content'] == extra_content
