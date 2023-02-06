async def test_pugixml_node_simple(taxi_arcadia_userver_test):
    response = await taxi_arcadia_userver_test.post(
        '/pugixml/node', json={'name': 'simple', 'value': 'test'},
    )

    assert response.status_code == 200
    assert response.text == '<?xml version="1.0"?><simple>test</simple>'


async def test_pugixml_node_attrs(taxi_arcadia_userver_test):
    response = await taxi_arcadia_userver_test.post(
        '/pugixml/node',
        json={
            'name': 'attrs',
            'value': 'with attrs',
            'attributes': {'foo': 'bar'},
        },
    )

    assert response.status_code == 200
    assert (
        response.text
        == '<?xml version="1.0"?><attrs foo="bar">with attrs</attrs>'
    )
