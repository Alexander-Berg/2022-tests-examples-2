import pytest

from taxi_tracing.lib.es_index import taxi


# pylint: disable=invalid-name
@pytest.mark.parametrize(
    'parent_link_exists,parent_link,expected_parent_link',
    [
        (False, None, None),
        (True, 'some-parent-link', 'some-parent-link'),
        (True, 'None', None),
    ],
)
def test_transform_span_for_parent_link(
        parent_link_exists, parent_link, expected_parent_link,
):
    es_data = [
        {
            'type': 'request',
            '_source': {
                'link': 'some-link',
                'uri': '/test',
                '@timestamp': '2018-10-24T11:00:00.0Z',
                'host': 'test-host',
            },
        },
        {
            'type': 'response',
            '_source': {
                'link': 'some-link',
                'uri': '/test',
                '@timestamp': '2018-10-24T11:00:01.0Z',
            },
        },
    ]
    if parent_link_exists:
        es_data[0]['_source']['parent_link'] = parent_link

    span, p_ctx = taxi.transform_span(es_data, span_id=None)
    assert p_ctx.link_id == expected_parent_link
    assert span.link_id == 'some-link'
