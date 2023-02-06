"""
Teamcity interactions helpers.
Docs: https://nda.ya.ru/3Thd9Q
"""


def _send_teamcity_message(message_name, value):
    print('##teamcity[%s %s]' % (message_name, value))


# pylint: disable=invalid-name
def send_teamcity_multiattribute_message(message_name, **attributes):
    value = ' '.join(
        '%s=\'%s\'' % (name, escape_teamcity_message_value(value))
        for name, value in attributes.items()
    )
    _send_teamcity_message(message_name, value)


def escape_teamcity_message_value(value):
    """
    Escape string to be correctly interpreted by teamcity.
    Unicode symbols are not supported
    :param value: string message
    :return: escaped value
    """
    return (
        value.replace('|', '||')
        .replace('\n', '|n')
        .replace('\r', '|r')
        .replace('\'', '|\'')
        .replace('[', '|[')
        .replace(']', '|]')
    )


def report_build_problem(description, identity=None):
    name = 'buildProblem'
    if identity is None:
        send_teamcity_multiattribute_message(name, description=description)
    else:
        send_teamcity_multiattribute_message(
            name, description=description, identity=identity,
        )


def report_build_statistic(key, value):
    name = 'buildStatisticValue'
    send_teamcity_multiattribute_message(name, key=key, value=str(value))


def set_parameter(name: str, value: str) -> None:
    message_name = 'setParameter'
    send_teamcity_multiattribute_message(
        message_name, name=name, value=str(value),
    )
