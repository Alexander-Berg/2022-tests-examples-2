import typing

import pytest

from taxi_testsuite.plugins import api_coverage


@pytest.mark.parametrize(
    'endpoints_list,usage,expected_ratio,covered,uncovered,not_in_list',
    [
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/eats/v1/launch/v1/native',
                    path_params=[],
                ),
                api_coverage.SchemaEndpoint(
                    http_method='POST',
                    http_path='/eats/v1/launch/v1/native',
                    path_params=[],
                ),
            ],
            [('/eats/v1/launch/v1/native', 'GET')],
            0.5,
            ['GET /eats/v1/launch/v1/native'],
            ['POST /eats/v1/launch/v1/native'],
            [],
            id='happy_path',
        ),
        pytest.param([], [], 1.0, [], [], [], id='empty_endpoints_set'),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/eats/v1/launch/v1/native',
                    path_params=[],
                ),
            ],
            [('/eats/v1/launch/v1/native', 'GET')],
            1.0,
            ['GET /eats/v1/launch/v1/native'],
            [],
            [],
            id='full_covered',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/api/v1/catalog/{slug_id}',
                    path_params=[
                        api_coverage.PathParam(
                            name='slug_id', type_param='string',
                        ),
                    ],
                ),
            ],
            [('/api/v1/catalog/test', 'GET')],
            1.0,
            ['GET /api/v1/catalog/{slug_id}'],
            [],
            [],
            id='endpoint_with_slug',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/api/v1/catalog/{slug_id}',
                    path_params=[
                        api_coverage.PathParam(
                            name='slug_id', type_param='integer',
                        ),
                    ],
                ),
            ],
            [('/api/v1/catalog/qwerty', 'GET')],
            0.0,
            [],
            ['GET /api/v1/catalog/{slug_id}'],
            ['GET /api/v1/catalog/qwerty'],
            id='wrong_slug_type',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/api/v1/catalog/{slug_id}/item/{item_id}',
                    path_params=[
                        api_coverage.PathParam(
                            name='slug_id', type_param='string',
                        ),
                        api_coverage.PathParam(
                            name='item_id', type_param='integer',
                        ),
                    ],
                ),
            ],
            [('/api/v1/catalog/test/item/123', 'GET')],
            1.0,
            ['GET /api/v1/catalog/{slug_id}/item/{item_id}'],
            [],
            [],
            id='right_slug_type',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/api/v1/catalog/{slug_id}',
                    path_params=[
                        api_coverage.PathParam(
                            name='slug_id', type_param='string',
                        ),
                    ],
                ),
            ],
            [
                ('/api/v1/catalog/test1', 'GET'),
                ('/api/v1/catalog/test2', 'GET'),
            ],
            1.0,
            ['GET /api/v1/catalog/{slug_id}'],
            [],
            [],
            id='several_calls_of_slug_endpoint',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/eats/v1/launch/v1/native',
                    path_params=[],
                ),
                api_coverage.SchemaEndpoint(
                    http_method='POST',
                    http_path='/eats/v1/launch/v1/native',
                    path_params=[],
                ),
            ],
            [
                ('/eats/v1/launch/v1/native', 'GET'),
                ('/eats/v1/launch/v1/native', 'GET'),
                ('/eats/v1/launch/v1/native', 'POST'),
            ],
            1.0,
            [
                'POST /eats/v1/launch/v1/native',
                'GET /eats/v1/launch/v1/native',
            ],
            [],
            [],
            id='different_methods_in_url',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/eats/v1/launch/v1/native',
                    path_params=[],
                ),
            ],
            [('/eats/v1/launch/v1/native//', 'GET')],
            0.0,
            [],
            ['GET /eats/v1/launch/v1/native'],
            ['GET /eats/v1/launch/v1/native/'],
            id='double_trailing_slash',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET', http_path='/aaa/bbb', path_params=[],
                ),
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/aaa/bbb/ccc',
                    path_params=[],
                ),
            ],
            [('/aaa/bbb', 'GET'), ('/aaa/bbb/ccc', 'GET')],
            1.0,
            ['GET /aaa/bbb', 'GET /aaa/bbb/ccc'],
            [],
            [],
            id='prefix_endpoints',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/aaa/bbb-ccc',
                    path_params=[],
                ),
            ],
            [('/aaa/bbb-ccc', 'GET')],
            1.0,
            ['GET /aaa/bbb-ccc'],
            [],
            [],
            id='endpoints_with_dash',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='POST',
                    http_path='/api/v2/menu/goods/get-categories/',
                    path_params=[],
                ),
            ],
            [('/api/v2/menu/goods/get-categories', 'POST')],
            1.0,
            ['POST /api/v2/menu/goods/get-categories'],
            [],
            [],
            id='spec_with_trailing_slash',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='POST',
                    http_path='/aaa/bbb/ccc',
                    path_params=[],
                ),
            ],
            [('/aaa/bbb/ccc', 'POST'), ('/aaa/bbb/ddd', 'POST')],
            1.0,
            ['POST /aaa/bbb/ccc'],
            [],
            ['POST /aaa/bbb/ddd'],
            id='covered_endpoints_not_in_list',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='POST',
                    http_path='/aaa/bbb/ccc',
                    path_params=[],
                    status_code=201,
                ),
                api_coverage.SchemaEndpoint(
                    http_method='POST',
                    http_path='/aaa/bbb/ccc',
                    path_params=[],
                    status_code=401,
                ),
            ],
            [('/aaa/bbb/ccc', 'POST', 201)],
            0.5,
            {'POST /aaa/bbb/ccc': ['response=201']},
            {'POST /aaa/bbb/ccc': ['response=401']},
            [],
            id='check_response_codes',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/aaa/bbb/ccc',
                    path_params=[],
                    status_code=200,
                    content_type='application/json',
                ),
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/aaa/bbb/ccc',
                    path_params=[],
                    status_code=200,
                    content_type='application/html',
                ),
            ],
            [('/aaa/bbb/ccc', 'GET', 200, 'application/json')],
            0.5,
            {
                'GET /aaa/bbb/ccc': [
                    'response=200 content-type=application/json',
                ],
            },
            {
                'GET /aaa/bbb/ccc': [
                    'response=200 content-type=application/html',
                ],
            },
            [],
            id='check_content_type',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/aaa/bbb/ccc',
                    path_params=[],
                    status_code=200,
                ),
            ],
            [('/aaa/bbb/ccc', 'GET', 200, 'application/json')],
            1.0,
            {'GET /aaa/bbb/ccc': ['response=200']},
            [],
            [],
            id='no_content_type_param_in_schema',
        ),
        pytest.param(
            [
                api_coverage.SchemaEndpoint(
                    http_method='GET',
                    http_path='/v1/pay/{trucks_entity}',
                    path_params=[
                        api_coverage.PathParam(
                            name='trucks_entity',
                            type_param='string',
                            value_enum=['shipper', 'carrier'],
                        ),
                    ],
                    status_code=200,
                    content_type='application/json',
                ),
            ],
            [('/v1/pay/staffer', 'GET', 200, 'application/json')],
            0.0,
            [],
            {'GET /v1/pay/{trucks_entity}': ['response=200']},
            {'GET /v1/pay/staffer': ['response=200']},
            id='enum_in_path_param',
        ),
    ],
)
def test_coverage_report(
        endpoints_list: typing.List[api_coverage.SchemaEndpoint],
        usage: typing.List,
        expected_ratio: float,
        covered: typing.List,
        uncovered: typing.List,
        not_in_list: typing.List,
):
    coverage_report = api_coverage.CoverageReport()
    schema_endpoints: typing.List[api_coverage.SchemaEndpoint] = endpoints_list

    for item in usage:
        coverage_report.update_usage_stat(*item)
    report = coverage_report.generate_report(schema_endpoints)
    stat = report.to_json()

    assert stat['coverage_ratio'] == expected_ratio
    assert sorted(stat['covered_endpoints']) == sorted(covered)
    assert sorted(stat['uncovered_endpoints']) == sorted(uncovered)
    assert sorted(stat['covered_endpoints_not_in_list']) == sorted(not_in_list)


def test_report_error():
    coverage_report = api_coverage.CoverageReport()
    schema_endpoints: typing.List[api_coverage.SchemaEndpoint] = [
        api_coverage.SchemaEndpoint(
            http_method='GET',
            http_path='/eats/v1/launch/v1/native',
            path_params=[],
            status_code=200,
        ),
        api_coverage.SchemaEndpoint(
            http_method='POST',
            http_path='/eats/v1/launch/v1/native',
            path_params=[],
            status_code=200,
        ),
    ]

    coverage_report.update_usage_stat(
        *('/eats/v1/launch/v1/native', 'GET', 200),
    )
    report = coverage_report.generate_report(schema_endpoints)
    expected = (
        'API coverage check failed! '
        'Please write tests for the following endpoints: \n'
        '  - POST /eats/v1/launch/v1/native\n'
        '    Uncovered responses:\n'
        '      - code=200\n'
    )

    try:
        report.coverage_validate(strict=True)
    except Exception as e:  # pylint: disable=broad-except
        assert isinstance(e, api_coverage.UncoveredEndpointsError)
        assert str(e) == expected


def test_report_warning(recwarn):
    coverage_report = api_coverage.CoverageReport()
    schema_endpoints: typing.List[api_coverage.SchemaEndpoint] = [
        api_coverage.SchemaEndpoint(
            http_method='GET',
            http_path='/eats/v1/launch/v1/native',
            path_params=[],
            status_code=200,
        ),
        api_coverage.SchemaEndpoint(
            http_method='POST',
            http_path='/eats/v1/launch/v1/native',
            path_params=[],
            status_code=200,
        ),
    ]

    coverage_report.update_usage_stat(
        *('/eats/v1/launch/v1/native', 'GET', 200),
    )
    report = coverage_report.generate_report(schema_endpoints)
    expected = (
        'API coverage check failed! '
        'Please write tests for the following endpoints: \n'
        '  - POST /eats/v1/launch/v1/native\n'
        '    Uncovered responses:\n'
        '      - code=200\n'
    )
    report.coverage_validate(strict=False)
    record = recwarn.pop()
    assert issubclass(record.category, UserWarning)
    assert str(record.message) == expected


def test_path_params_error():
    expected = (
        'For endpoint \'/abc/def/{slug_id}\' there is'
        ' unsupported path-param type: '
        ' name=slug_id, type=float'
    )
    try:
        api_coverage.SchemaEndpoint(
            http_method='GET',
            http_path='/abc/def/{slug_id}',
            path_params=[
                api_coverage.PathParam(name='slug_id', type_param='float'),
            ],
        )
    except Exception as e:  # pylint: disable=broad-except
        assert isinstance(e, api_coverage.UnsupportedPathParamType)
        assert str(e) == expected
