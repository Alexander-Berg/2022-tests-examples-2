# -*- coding: utf-8 -*-

from mock import Mock


def create_response_mock(response):
    response_mock = Mock()
    response_mock.body = response
    response_mock.error = None
    return response_mock
