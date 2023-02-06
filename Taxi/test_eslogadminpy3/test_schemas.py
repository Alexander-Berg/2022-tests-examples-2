# pylint: disable=redefined-outer-name
import inspect
import os
from typing import Any
from typing import Optional

import jsonschema
import pytest
import yaml

from eslogadminpy3.generated.service.service_schemas import (
    plugin as service_schemas,
)
from eslogadminpy3.generated.web import web_context
from eslogadminpy3.lib import preformatters


def _check_preformatter(preformatter):
    assert inspect.iscoroutinefunction(preformatter)

    signature = inspect.signature(preformatter)

    assert signature is not inspect.Signature.empty
    assert signature.return_annotation == Optional[Any]

    params = signature.parameters
    assert len(params) == 4

    for param in params.values():
        assert (
            param.kind is inspect.Parameter.KEYWORD_ONLY
            and param.annotation is not inspect.Parameter.empty
        ) or param.kind is inspect.Parameter.VAR_KEYWORD

    assert params['context'].annotation is web_context.Context
    assert params['log_extra'].default is None


@pytest.fixture
def filters_schema_validator():
    path = os.path.join(
        os.path.dirname(__file__), '..', 'docs', 'yaml', 'filters_schema.yaml',
    )
    with open(path) as fp:
        validator_schema = yaml.safe_load(fp)
    jsonschema.Draft4Validator.check_schema(validator_schema)
    return jsonschema.Draft4Validator(validator_schema)


def test_validate_schemas(web_app, filters_schema_validator):
    orders = set()
    names = set()

    def check_name(item: service_schemas.Filter):
        msg = f'"{item.name}" name already in use'
        assert item.name not in names, msg
        names.add(item.name)

    def check_order(item: service_schemas.Filter):
        if item.order is None:
            return
        msg = (
            f'Order param "{item.order}" '
            f'for filter "{item.name}" already exists'
        )
        assert item.order not in orders, msg
        orders.add(item.order)

    assert web_app['context'].service_schemas.schemas
    for schema in web_app['context'].service_schemas.schemas.values():
        filters_schema_validator.validate(schema)

        for filter_item in schema.get('filters', []):
            _item = service_schemas.Filter(**filter_item)
            if 'preformatter' in filter_item:
                assert hasattr(preformatters, _item.preformatter)
                _check_preformatter(getattr(preformatters, _item.preformatter))

            check_name(_item)
            check_order(_item)


@pytest.mark.parametrize(
    'schema_to_validate,is_valid',
    [
        ([], False),
        ({}, False),
        (
            {'filters': [{'name': 'some', 'type': 'text', 'title': 'test'}]},
            True,
        ),
        ([{'name': 'some', 'type': 'text', 'title': 'test'}], False),
        (
            {'filters': [{'name': 'some', 'type': 'string', 'title': 'test'}]},
            False,
        ),
        (
            {
                'filters': [
                    {'name': 'some', 'es_name': 'meta_some', 'title': 'test'},
                ],
            },
            False,
        ),
    ],
)
def test_check_validator_schema(
        filters_schema_validator, schema_to_validate, is_valid,
):
    if is_valid:
        filters_schema_validator.validate(schema_to_validate)
    else:
        with pytest.raises(jsonschema.ValidationError):
            filters_schema_validator.validate(schema_to_validate)
