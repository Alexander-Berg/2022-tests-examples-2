# -*- coding: utf-8 -*-
from passport.backend.oauth.core.test.framework import FormTestCase
from passport.backend.oauth.tvm_api.tvm_api.tvm_abc.forms import (
    CreateClientForm,
    EditClientForm,
    PaginationForm,
)


class TestPaginationForm(FormTestCase):
    form = PaginationForm
    invalid_params = [
        (
            {
                'page': 'NaN',
                'page_size': 'NaN',
            },
            {
                'page': ['invalid'],
                'page_size': ['invalid'],
            },
        ),
        (
            {
                'page': '-1',
                'page_size': '0',
            },
            {
                'page': ['invalid'],
                'page_size': ['invalid'],
            },
        ),
        (
            {
                'page': '1',
                'page_size': '101',
            },
            {
                'page_size': ['invalid'],
            },
        ),
    ]
    valid_params = [
        (
            {},
            {
                'page': 1,
                'page_size': 50,
            },
        ),
        (
            {
                'page': '2',
                'page_size': '51',
            },
            {
                'page': 2,
                'page_size': 51,
            },
        ),
    ]


class TestCreateClientForm(FormTestCase):
    form = CreateClientForm
    invalid_params = [
        (
            {},
            {
                'name': ['missing'],
                'abc_service_id': ['missing'],
                'abc_request_id': ['missing'],
            },
        ),
        (
            {
                'name': '',
                'abc_service_id': 'foo',
                'abc_request_id': 'foo',
            },
            {
                'name': ['missing'],
                'abc_service_id': ['invalid'],
                'abc_request_id': ['invalid'],
            },
        ),
    ]
    valid_params = [
        (
            {
                'name': 'test',
                'abc_service_id': '1',
                'abc_request_id': '2',
            },
            {
                'name': 'test',
                'abc_service_id': 1,
                'abc_request_id': 2,
            },
        ),
    ]


class TestEditClientForm(FormTestCase):
    form = EditClientForm
    invalid_params = [
        (
            {},
            {
                'client_id': ['missing'],
                'name': ['missing'],
            },
        ),
        (
            {
                'name': '',
            },
            {
                'client_id': ['missing'],
                'name': ['missing'],
            },
        ),
    ]
    valid_params = [
        (
            {
                'name': 'test',
                'client_id': '2',
            },
            {
                'name': 'test',
                'client_id': 2,
            },
        ),
    ]
