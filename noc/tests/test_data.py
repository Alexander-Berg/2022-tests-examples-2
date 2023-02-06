import logging
import os
import unittest
from typing import List, Optional, Callable, Union

from comocutor.devices import (EkinopsDevice, IosDevice, PCDevice, JnxDevice, VrpDevice, CoriantDevice, ADVADevice,
                               ArubaIAPDevice,
                               NokiaSRDevice, RosDevice, CiscoWLCDevice)
from comocutor.streamer import Expr
from data import jnx, ios, bash, ekinops, Data, WriteErrorCommand, vrp, coriant, adva, arubaiap, nokia, ros, cisco_wlc


class AutoTestData(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dev_cls = [
            {"device": EkinopsDevice, "test_data": ekinops},
            {"device": IosDevice, "test_data": ios},
            {"device": JnxDevice, "test_data": jnx},
            {"device": PCDevice, "test_data": bash},
            {"device": VrpDevice, "test_data": vrp},
            {"device": CoriantDevice, "test_data": coriant},
            {"device": ADVADevice, "test_data": adva},
            {"device": ArubaIAPDevice, "test_data": arubaiap},
            {"device": NokiaSRDevice, "test_data": nokia},
            {"device": RosDevice, "test_data": ros},
            {"device": CiscoWLCDevice, "test_data": cisco_wlc}
        ]

    def _test_dev_exprs(self,
                        prompt_exprs: List[Expr],
                        indata: List[Union[bytes, str]],
                        msg: str = "",
                        not_match: bool = False,
                        read_cb: Optional[Callable] = None,
                        full_match: bool = True):
        if read_cb is None:
            read_cb = lambda x: x

        for item in indata:
            if isinstance(item, str):
                item = item.encode()
            item = read_cb(item)
            for prompt_exp in prompt_exprs:
                m = prompt_exp.check(item)
                if not m:
                    continue

                if not_match:
                    self.fail("%s %r matched with %r" % (msg, item, prompt_exprs))

                # TODO: probably some callbacks are excessive, since item was already wrapped in read_cb.
                matched = read_cb(m.group(0))
                if full_match and matched != item:
                    self.fail("partial match: %r != %r expr=%r" % (matched, item, prompt_exprs))
                break
            else:
                if not not_match:
                    self.fail("%s %r not matched with %r" % (msg, item, prompt_exprs))

    def _get_data_instances(self):
        res = {}
        for test_param in self._dev_cls:
            test_data_cls = test_param["test_data"]
            res[test_data_cls] = []
            for attr in dir(test_data_cls):
                data_obj = getattr(test_data_cls, attr)
                if isinstance(data_obj, type) and issubclass(data_obj, Data) and data_obj != Data:
                    res[test_data_cls].append(data_obj)
        return res

    def _extract_error_command(self):
        res = {}
        for test_data_cls, data_classes in self._get_data_instances().items():
            res[test_data_cls] = []
            for data_class in data_classes:
                for item in data_class.session:
                    if isinstance(item, WriteErrorCommand):
                        res[test_data_cls].append(item)
        return res

    def test_command_error_extracted(self):
        error_commands = self._extract_error_command()
        for test_param in self._dev_cls:
            test_data = test_param["test_data"]
            device = test_param["device"]
            # TODO: make data_read_cb as class method and remove unnecessary __new__
            dev = device.__new__(device)
            self._test_dev_exprs([x[0] for x in device.COMMAND_ERROR],
                                 [dev.data_read_cb(bytes(x)) for x in error_commands[test_data]],
                                 msg="cls=%s" % test_data.__name__,
                                 read_cb=dev.data_read_cb,
                                 full_match=False)

    def test_variants(self):
        for var_name, device_regexp_name, not_match, full_match in [
            ("PAGER_VARIANTS", "PAGER", False, True),
            ("NOPROMPT_VARIANTS", "COMMAND_PROMPT", True, True),
            ("LOGIN_PROMPT_VARIANTS", "LOGIN_PROMPT", False, True),
            ("PASSWORD_PROMPT_VARIANTS", "PASSWORD_PROMPT", False, True),
            ("PROMPT_VARIANTS", "COMMAND_PROMPT", False, True),
            ("QUESTION_VARIANTS", "QUESTION", False, False),
            ("MOTD_VARIANTS", "MOTD", False, True),
            ("COMMAND_ERROR_VARIANTS", "COMMAND_ERROR", False, True),
        ]:
            for test_param in self._dev_cls:
                test_data = test_param["test_data"]
                device = test_param["device"]
                dev = device.__new__(device)

                if not hasattr(test_data, var_name):
                    continue

                logging.debug(
                    'test command matched for device "%s" variant "%s" regexp "%s" not_match "%s" full_match "%s"',
                    device, var_name, device_regexp_name, not_match, full_match
                )

                if var_name == "COMMAND_ERROR_VARIANTS":
                    exprs = [x[0] for x in getattr(device, device_regexp_name)]
                else:
                    exprs = getattr(device, device_regexp_name)
                self._test_dev_exprs(exprs,
                                     getattr(test_data, var_name),
                                     msg="cls=%s %s" % (test_data.__name__, var_name),
                                     not_match=not_match,
                                     read_cb=dev.data_read_cb,
                                     full_match=full_match)

    def test_dev_read_cb(self):
        for test_param in self._dev_cls:
            test_data = test_param["test_data"]
            device = test_param["device"]
            dev = device.__new__(device)
            if hasattr(test_data, "DATA_READ_CB_VARIANTS"):
                logging.debug("test data_read_cb in for %s", test_param)
                for test_item in test_data.DATA_READ_CB_VARIANTS:
                    res = dev.data_read_cb(test_item["input"])
                    self.assertEqual(res, test_item["expected"],
                                     "cls=%s" % (test_data.__name__,))


if os.getenv("COMOCUTOR_DEBUG"):
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level,
                    format="%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s() - %(levelname)s - %(message)s")

if __name__ == '__main__':
    unittest.main()
