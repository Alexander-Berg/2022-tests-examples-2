import collections
import copy


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
        >>> false_case(field1='another')
        TestCase(field1='another', field2=False, field3=None, field4='other')

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
            for key, value in default_values.items():
                if key not in kwargs:
                    kwargs[key] = value
            return case_getter(cls.params, default_value, **kwargs)

    return TestCase


class VarHook:
    def __init__(self, variables):
        self.variables = variables

    def __call__(self, obj):
        if '$var' in obj:
            varname = obj['$var']
            if varname in self.variables:
                return self.variables[varname]
            if '$default' in obj:
                return obj['$default']
            raise RuntimeError('Unknown variable name %s' % (varname,))
        return obj
