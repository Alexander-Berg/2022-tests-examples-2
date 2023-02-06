import re

RE_SUB = r'\$\{([^}]+)\}'


class BaseError(Exception):
    """Base class for all exceptions in this module."""


class GetOptionError(BaseError):
    """Raise if the variable is not in the options"""


def substitute_vars(obj, **kwargs):
    return _substitute_dict(obj, kwargs)


def _substitute_list(seq, options):
    return [_substitute_value(value, options) for value in seq]


def _substitute_value(value, options):
    def _get_var_value(matchobj):
        var_name = matchobj.groups()[0]
        var_value = _get_option(options, var_name)
        if not isinstance(var_value, str):
            var_value = str(var_value)
        return var_value

    if isinstance(value, str):
        if value.startswith('$') and not value.startswith('${'):
            value = _get_option(options, value[1:])
        else:
            value = re.sub(RE_SUB, _get_var_value, value)
    elif isinstance(value, dict):
        value = _substitute_dict(value, options)
    elif isinstance(value, list):
        value = _substitute_list(value, options)
    return value


def _substitute_dict(dct, options):
    return {key: _substitute_value(value, options)
            for key, value in dct.items()}


def _get_option(options, option):
    value = options.get(option, None)
    if value is None:
        raise GetOptionError('Variable %s must be in options' % (option,))
    return value
