import six
import datetime
import pytest
import requests_mock
import json

from dateutil import parser as dt_parser
from dateutil import tz

from library.python import resource

from sandbox.projects.common import kosher_release
from sandbox.projects.common.kosher_release import private as kosher_release_private
from sandbox.common.types import task as ctt
from sandbox.common import rest


def load_resource_data(resource_id):
    return json.loads(resource.find("{}.json".format(resource_id)))


@pytest.fixture(scope="session")
def fake_base_url():
    return "https://test-url.ru"


@pytest.fixture(scope="session")
def resource__ready__not_released__id():
    return 2278694014


@pytest.fixture(scope="session")
def resource__released_stable__id():
    return 2278667020


@pytest.fixture(scope="session")
def resource__released_testing__id():
    return 2280587119


@pytest.fixture(scope="session")
def resource__ready__not_released(resource__ready__not_released__id):
    return load_resource_data(resource__ready__not_released__id)


@pytest.fixture(scope="session")
def resource__released_stable(resource__released_stable__id):
    return load_resource_data(resource__released_stable__id)


@pytest.fixture(scope="session")
def resource__released_testing(resource__released_testing__id):
    return load_resource_data(resource__released_testing__id)


@pytest.fixture(scope="session")
def sb_client(
    fake_base_url,
    resource__ready__not_released__id,
    resource__ready__not_released,
    resource__released_stable__id,
    resource__released_stable,
    resource__released_testing__id,
    resource__released_testing,
):
    with requests_mock.Mocker() as m:

        for resource_id, resource_data in [
            (resource__ready__not_released__id, resource__ready__not_released),
            (resource__released_stable__id, resource__released_stable),
            (resource__released_testing__id, resource__released_testing),
        ]:
            m.register_uri(
                "GET",
                "{}/resource/{}".format(fake_base_url, resource_id),
                json=resource_data,
                status_code=200,
            )

        yield rest.Client(base_url=fake_base_url)


def test__get_release_attr_name():

    default = kosher_release_private.get_release_attr_name()

    assert isinstance(default, six.string_types)
    assert default.islower()
    assert default.startswith(kosher_release_private.RELEASE_ATTR_NAME_PREFIX)

    assert kosher_release_private.get_release_attr_name(ctt.ReleaseStatus.STABLE) == "k_released_stable"
    assert kosher_release_private.get_release_attr_name(ctt.ReleaseStatus.TESTING) == "k_released_testing"
    assert kosher_release_private.get_release_attr_name(ctt.ReleaseStatus.PRESTABLE) == "k_released_prestable"
    assert kosher_release_private.get_release_attr_name(ctt.ReleaseStatus.UNSTABLE) == "k_released_unstable"


def test__prepare_release_attr_value():

    value = kosher_release_private.prepare_release_attr_value()

    assert isinstance(value, six.string_types)
    assert value.endswith("Z")

    try:
        dt = dt_parser.parse(value)
    except dt_parser.ParserError:
        assert False, (
            "The value constructed by prepare_release_attr_value ({}) is not a valid datetime ISO string".format(
                value,
            )
        )

    assert dt.tzinfo == tz.UTC

    dt = datetime.datetime(
        year=2021,
        month=1,
        day=1,
        hour=1,
        tzinfo=tz.tzoffset("Russia/Moscow", 3)
    )

    dt_utc = dt.astimezone(tz.UTC)

    value = kosher_release_private.prepare_release_attr_value(dt_obj=dt)

    assert isinstance(value, six.string_types)
    assert value.endswith("Z")
    assert value.replace("Z", "+00:00") == dt_utc.isoformat()


def test__has_release_attr(
    sb_client,
    resource__ready__not_released__id,
    resource__released_stable__id,
    resource__released_testing__id,
):

    assert not kosher_release.has_release_attr(
        resource__ready__not_released__id,
        sb_rest_client=sb_client,
    )

    assert not kosher_release.has_release_attr(
        resource__ready__not_released__id,
        stage=ctt.ReleaseStatus.TESTING,
        sb_rest_client=sb_client,
    )

    assert kosher_release.has_release_attr(
        resource__released_stable__id,
        sb_rest_client=sb_client,
    )

    assert not kosher_release.has_release_attr(
        resource__released_stable__id,
        stage=ctt.ReleaseStatus.TESTING,
        sb_rest_client=sb_client,
    )

    assert not kosher_release.has_release_attr(
        resource__released_testing__id,
        sb_rest_client=sb_client,
    )

    assert kosher_release.has_release_attr(
        resource__released_testing__id,
        stage=ctt.ReleaseStatus.TESTING,
        sb_rest_client=sb_client,
    )


def test__get_release_time(
    sb_client,
    resource__ready__not_released,
    resource__released_stable,
    resource__released_testing,
):
    resource__ready__not_released__time_stable = kosher_release.get_release_time(
        resource__ready__not_released["id"],
        sb_rest_client=sb_client,
    )

    resource__released_stable__time_stable = kosher_release.get_release_time(
        resource__released_stable["id"],
        sb_rest_client=sb_client,
    )

    resource__released_testing__time_stable = kosher_release.get_release_time(
        resource__released_testing["id"],
        sb_rest_client=sb_client,
    )

    resource__released_testing__time_testing = kosher_release.get_release_time(
        resource__released_testing["id"],
        ctt.ReleaseStatus.TESTING,
        sb_rest_client=sb_client,
    )

    assert resource__ready__not_released__time_stable is None

    assert resource__released_stable__time_stable is not None
    assert isinstance(resource__released_stable__time_stable, datetime.datetime)
    assert resource__released_stable__time_stable.tzinfo is not None
    assert resource__released_stable__time_stable == dt_parser.parse(
        resource__released_stable["attributes"]["k_released_stable"],
    )

    assert resource__released_testing__time_stable is None
    assert resource__released_testing__time_testing is not None
    assert isinstance(resource__released_testing__time_testing, datetime.datetime)
    assert resource__released_testing__time_testing.tzinfo is not None
    assert resource__released_testing__time_testing == dt_parser.parse(
        resource__released_testing["attributes"]["k_released_testing"],
    )
