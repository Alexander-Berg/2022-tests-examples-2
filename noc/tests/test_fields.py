import itertools
import types

import mock
from mock import patch
from django.test import SimpleTestCase
from parameterized import parameterized

from l3common.tests import cases
from ..fields import Config
from ..forms import VSConfigForm
from ..forms import ConfigForm

BASE_CONFIG = types.MappingProxyType(
    {
        "METHOD": "TUN",
        "ANNOUNCE": True,
        "QUORUM": 1,
        "HYSTERESIS": 0,
        #
        "SCHEDULER": "wrr",
        "MH_FALLBACK": False,
        "MH_PORT": False,
        "OPS": False,
        #
        "CHECK_TYPE": "HTTP_GET",
        "HTTP_PROTOCOL_CHOICES": "1.1",
        "HOST": None,
        "CHECK_URL": "/ping",
        "CONNECT_IP": None,
        "CONNECT_PORT": None,
        #
        "DIGEST": None,
        "STATUS_CODE": 204,
        #
        "CHECK_TIMEOUT": 1,
        "CHECK_RETRY": 1,
        "CHECK_RETRY_TIMEOUT": 1,
        "DELAY_LOOP": 10,
        "DC_FILTER": False,
        #
        "INHIBIT_ON_FAILURE": False,
        "PERSISTENCE_TIMEOUT": None,
        #
        "DYNAMICWEIGHT": False,
        "DYNAMICWEIGHT_RATIO": None,
        "DYNAMICWEIGHT_IN_HEADER": False,
        "DYNAMICWEIGHT_ALLOW_ZERO": False,
        #
        "WEIGHT_LB35": 100,
        "WEIGHT_LB67": 100,
        "WEIGHT_LB242": 100,
    }
)


def make_config(**kwargs):
    return Config(dict(BASE_CONFIG, **kwargs))


INVALID_VALUES = (
    "0",
    "0.0%",
    -1,
    "-1",
    "-100%",
    "-100.0%",
    "1",
    "100.0%",
    "200%",
    -0.5,
    "-0.5",
    "-50%",
    0.5,
    "0.5",
    "abc",
    "abc%",
)


class MockUser:
    @staticmethod
    def get_username():
        return "username"

    @staticmethod
    def has_perm(*_args, **_kwargs):
        return True


class MockObjects:
    def filter(self, *_args, **_kwargs):
        return self

    @staticmethod
    def values_list(*_args, **_kwargs):
        return []


class MockLBObjects(MockObjects):
    pass


class MockVirtualServerObjects(MockObjects):
    def all(self, *_args, **_kwargs):
        return self

    @staticmethod
    def none():
        return []


class VsConfigQuorumTestCase(SimpleTestCase):
    @parameterized.expand(
        itertools.product(
            [10, 0, 1],
            [None, "", 0],
        )
    )
    def test_get_quorum_with_default(self, amount, quorum_value):
        config = make_config(QUORUM=quorum_value)
        self.assertEquals(1, config.get_quorum(amount))

    @parameterized.expand([(2,), (10,)])
    def test_get_quorum_from_value(self, amount):
        config = make_config(QUORUM=3)
        self.assertEquals(3, config.get_quorum(amount))

    @parameterized.expand(
        [
            (10, "15%", 2),
            (100, "15%", 15),
            (15, "100%", 15),
            (123, "34%", 42),
            (45, "1%", 1),
        ]
    )
    def test_get_quorum_from_percents(self, amount, quorum_value, expected):
        config = make_config(QUORUM=quorum_value)
        self.assertEquals(expected, config.get_quorum(amount))

    @parameterized.expand([(value,) for value in INVALID_VALUES + ("0%",)])
    def test_invalid_value(self, quorum_value):
        config = make_config(QUORUM=quorum_value)
        with self.assertRaises(ValueError):
            config.get_quorum(10)

    def test_negative_amount(self):
        config = make_config(QUORUM=123)
        with self.assertRaisesMessage(ValueError, "Amount should not be negative value: -45"):
            config.get_quorum(-45)


class VsConfigHysteresisTestCase(SimpleTestCase):
    @parameterized.expand(
        itertools.product(
            [10, 0, 1],
            [None, "", 0],
        )
    )
    def test_get_hysteresis_with_default(self, amount, hysteresis_value):
        config = make_config(HYSTERESIS=hysteresis_value)
        self.assertEquals(0, config.get_hysteresis(amount))

    @parameterized.expand([(1,), (10,)])
    def test_get_hysteresis_from_value(self, amount):
        config = make_config(HYSTERESIS=2)
        self.assertEquals(2, config.get_hysteresis(amount))

    @parameterized.expand(
        [
            (10, "15%", 1),
            (100, "15%", 15),
            (15, "100%", 15),
            (123, "34%", 41),
            (456, "0%", 0),
            (78, "1%", 0),
        ]
    )
    def test_get_hysteresis_from_percents(self, amount, hysteresis_value, expected):
        config = make_config(HYSTERESIS=hysteresis_value)
        self.assertEquals(expected, config.get_hysteresis(amount))

    @parameterized.expand([(value,) for value in INVALID_VALUES])
    def test_invalid_value(self, hysteresis_value):
        config = make_config(HYSTERESIS=hysteresis_value)
        with self.assertRaises(ValueError):
            config.get_hysteresis(10)

    def test_negative_amount(self):
        config = make_config(HYSTERESIS=123)
        with self.assertRaisesMessage(ValueError, "Amount should not be negative value: -45"):
            config.get_hysteresis(-45)


class VSConfigFormInitialTestCase(SimpleTestCase):
    def test_initial_values(self):
        form = VSConfigForm({})
        form = VSConfigForm(
            dict((f"config-{name}", form.get_initial_for_field(field, name)) for name, field in form.fields.items())
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_initial_values_invalid(self):
        form = VSConfigForm(initial={"QUORUM": "1.0", "HYSTERESIS": "a%"})
        form = VSConfigForm(
            dict((f"config-{name}", form.get_initial_for_field(field, name)) for name, field in form.fields.items())
        )
        self.assertFalse(form.is_valid(), form.errors)


@cases.patching(
    patch("l3mgr.models.LoadBalancer.objects.filter", autospec=True, return_value=MockLBObjects()),
    patch("l3mgr.models.VirtualServer.objects.all", autospec=True, return_value=MockVirtualServerObjects()),
)
class ConfigFormTestCase(SimpleTestCase):
    service_mock = mock.Mock()
    instance_mock = mock.Mock()

    def setUp(self) -> None:
        self.instance_mock._meta.fields = []

    @parameterized.expand(
        [
            ("Initial commit",),
            ("Initial\ncommit",),
            ("Initial\r\ncommit",),
        ]
    )
    def test_success_values(self, comment_value) -> None:
        form = ConfigForm({"comment": comment_value}, user=MockUser(), svc=self.service_mock)
        form.instance = self.instance_mock

        self.assertTrue(form.is_valid(), form.errors)

    @parameterized.expand(
        [
            ("", "This field is required."),
            ("*" * 777, "Ensure this value has at most 512 characters"),
        ]
    )
    def test_wrong_values(self, comment_text, error_text) -> None:
        form = ConfigForm({"comment": comment_text}, user=MockUser(), svc=self.service_mock)
        form.instance = self.instance_mock

        self.assertFalse(form.is_valid(), "Should be comment length errors")

        self.assertEqual(1, len(form.errors), "Should be only comment-related error")
        self.assertIn("comment", form.errors, "Should be comment length errors")
        self.assertIn(error_text, form.errors["comment"][0], "Should be only length format related comment error")
