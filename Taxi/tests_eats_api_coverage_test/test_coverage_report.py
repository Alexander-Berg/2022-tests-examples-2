def test_items_collection(request):
    assert request.session.items[-1].name == 'test_api_coverage'


def test_schema_endpoints(schema_endpoints):
    assert [str(x) for x in schema_endpoints] == [
        'PUT /sample/v1/action response=200 content-type=application/json',
        'POST /v1/pay/{trucks_entity} response=200',
        'POST /v1/pay/some response=200',
    ]
