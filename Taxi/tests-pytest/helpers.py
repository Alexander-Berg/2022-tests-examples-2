import collections
import copy
import json
import os

from bson import json_util
import jsonschema
import pytest

from django import test as django_test

from taxi.internal.data_manager import loader_utils
from taxi.util import evlog


def bson_object_hook(dct):
    if '$date' in dct:
        dt = json_util.object_hook(dct)
        return dt.replace(tzinfo=None)
    else:
        return json_util.object_hook(dct)


def check_difference(result, expected, description):
    if isinstance(result, list):
        assert len(result) == len(expected), (
            '%s: len(result)=%d != len(expected)=%d' % (
                description, len(result), len(expected)
            )
        )
        for num, (result_el, expected_el) in enumerate(zip(result, expected)):
            check_difference(result_el, expected_el,
                             description='.'.join((description, str(num))))
    elif isinstance(result, dict):
        assert isinstance(expected, dict), (
            '%s: value is not expected to be a dict but a %s' % (
                description, type(expected)
            )
        )

        keys = sorted(result.keys())
        expected_keys = sorted(expected.keys())
        for key in keys:
            assert key in expected_keys, (
                '%s: key=%s not in expected keys: %s' % (
                    description, key, ' '.join(expected_keys)
                )
            )
            check_difference(result[key], expected[key],
                             description='.'.join((description, str(key))))
        assert len(keys) == len(expected_keys), (
            '%s: len(keys)=%d != len(expected_keys)=%d, '
            'extra keys: %s' % (
                description, len(keys), len(expected_keys),
                ' '.join([key for key in expected_keys if key not in keys])
            )
        )
    assert result == expected, (
        '%s: result=%s != expected=%s' % (description, result, expected)
    )


def validate_objects_in_dir(directory, schema, loader=loader_utils.load_yaml):
    for dir_path, _, file_names in os.walk(directory):
        for file_name in file_names:
            if file_name.endswith('.yaml'):
                obj_file_path = os.path.join(dir_path, file_name)
                obj = loader(obj_file_path)
                try:
                    jsonschema.validate(obj, schema)
                except jsonschema.ValidationError as exc:
                    exc.message = 'error in %s\n%s' % (
                        obj_file_path, exc.message
                    )
                    raise


class Param(object):

    def __init__(self, *values, **kwargs):
        self.values = values
        self.id = kwargs['id']

    def replace(self, values):
        self.values = values
        return self

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.items)


def parametrize(argnames, argvalues, indirect=False, scope=None):
    ids = []
    values = []
    for value in argvalues:
        if isinstance(value, Param):
            values.append(value.values)
            ids.append(value.id)
        else:
            values.append(value)
            ids.append(None)
    return pytest.mark.parametrize(argnames, values, indirect=indirect, ids=ids, scope=scope)


def case_getter(case_params, default_value=None, **default_values):
    """This is to define test cases with some default values.

        Usage:

        >>> case = case_getter(
                'field1 field2 field3 field4',
                field4='other'
            )
        >>> case(field1='some_value')  # you don't need to provide all values
        TestCase(field1='some_value', field2=None, field3=None, field4='other')
        >>> false_case = case.partial(field2=False)
        >>> false_case(field1='another value')
        TestCase(field1='another value', field2=False, field3=None, field4='other')

    """

    base_tuple = collections.namedtuple('TestCase', case_params)

    class TestCase(tuple):

        params = ','.join(base_tuple._fields)

        def __new__(cls, *args, **kwargs):
            if args:
                for field, arg in zip(base_tuple._fields, args):
                    kwargs[field] = arg
            for field in base_tuple._fields:
                if field not in kwargs:
                    if field in default_values:
                        kwargs[field] = copy.deepcopy(default_values[field])
                    else:
                        kwargs[field] = default_value
            return base_tuple(**kwargs)

        @classmethod
        def partial(cls, **kwargs):
            for key, value in default_values.iteritems():
                if key not in kwargs:
                    kwargs[key] = value
            return case_getter(cls.params, default_value, **kwargs)

    return TestCase


class TaxiAdminRequest(django_test.RequestFactory):
    """Request class to use when you need to check permissions
        and/or the view is wrapped with log_request decorator
        (request must have time_storage attribute then).
    """

    def __init__(self, login='test_login', superuser=False, groups=None,
                 time_storage=None, permissions=None, **kwargs):
        super(TaxiAdminRequest, self).__init__(**kwargs)
        self._login = login
        self._time_storage = time_storage or evlog.new_time_storage('')
        self._superuser = superuser
        self._groups = groups or []
        self._permissions = permissions

    def request(self, **request):
        request_object = super(TaxiAdminRequest, self).request(**request)
        request_object.login = self._login
        request_object.time_storage = self._time_storage
        request_object.superuser = self._superuser
        request_object.groups = self._groups
        if self._permissions is not None:
            request_object.permissions = self._permissions
        return request_object

    def json(self, url='', data=None, **kwargs):
        return self.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
            **kwargs
        )


def get_user_api_response(personal_phone_id='personal_phone_id1'):
    """Response mock for userapi get_user_phone request"""
    return {
        'id': '1d239d76132553e6899b21ff',
        'phone': '+72222222222',
        'type': 'yandex',
        'stat': {
            'big_first_discounts': 0,
            'complete': 0,
            'complete_card': 0,
            'complete_apple': 0,
            'complete_google': 0
        },
        'is_loyal': False,
        'is_yandex_staff': False,
        'is_taxi_staff': False,
        'personal_phone_id': personal_phone_id,
    }
