import base64

from django import template
from django.template.defaultfilters import stringfilter

from compendium.models.models import CustomUser

from tests.models import TestLogs
from tests.views import get_user_tests

register = template.Library()


@register.filter
@stringfilter
def encode_base64(value):
    """
    Example:
        encode: "str(base64.b64encode(bytes(value, encoding)), encoding)", 10 -> MTA=
        decode: "str(base64.b64decode(bytes(value, encoding)), encoding)", MTA= -> 10
    """
    encoding = 'utf-8'

    return str(base64.b64encode(bytes(value, encoding)), encoding)


@register.simple_tag(takes_context=True)
def user_not_answered_tests(context):
    """
    Include "user_tests.html" template.
    """

    return get_user_tests(context['request'])


@register.filter
@stringfilter
def question_image_media_url(value):
    """
    Make media URL from image path.
    """

    return 'https://compendium.s3.mds.yandex.net/{}'.format(value)


@register.filter
@stringfilter
def last_test_results_avg(value):
    """
    Args:
        value (str): Agent username.
    """

    result = '–'

    try:
        user = CustomUser.objects.get(username=value)
    except CustomUser.DoesNotExist:
        user = None

    if user:
        result = TestLogs.get_avg_result_by_user(user)

    return result


@register.simple_tag
def get_total_assigned(test, among_agents=None):
    if among_agents is not None:
        return test.total_assigned(among_agents)
    else:
        return test.total_assigned()


@register.simple_tag
def get_total_assigned_answered(test, among_agents=None):
    if among_agents is not None:
        return test.total_assigned_answered(among_agents)
    else:
        return test.total_assigned_answered()


@register.simple_tag
def get_avg_answered(test, among_agents=None):
    if among_agents is not None:
        return test.avg_answered(among_agents)
    else:
        return test.avg_answered()


@register.simple_tag
def get_answered_percent(test, among_agents=None):
    if among_agents is not None:
        return test.answered_percent(among_agents)
    else:
        return test.answered_percent()
