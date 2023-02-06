# coding: utf8
from __future__ import absolute_import, division, print_function, unicode_literals

import six
import unittest

from sandbox.projects.release_machine.components.configs.rasp._base import (
    AddParamName, NoneParamValue, PropagateCfgParamsToInners, FinalConfig
)


@six.add_metaclass(AddParamName)
class CfgParamsTestBase(object):
    CONFIG_VAL = NoneParamValue()
    CONFIG_VAL_DEF = NoneParamValue('def value')


@six.add_metaclass(PropagateCfgParamsToInners)
class OuterBase(object):

    class CfgParams(CfgParamsTestBase):
        pass

    CLASS_VAL = CfgParams.CONFIG_VAL

    class Inner(object):
        class CfgParams(CfgParamsTestBase):
            pass

        CLASS_VAL = CfgParams.CONFIG_VAL
        CLASS_VAL_DEF = CfgParams.CONFIG_VAL_DEF
        CLASS_LIST = [1, 'end']
        CLASS_STRING = 'string'
        CLASS_INT = 11

        class InnerInner(object):
            class CfgParams(CfgParamsTestBase):
                pass

            CLASS_VAL = CfgParams.CONFIG_VAL
            CLASS_LIST = [CfgParams.CONFIG_VAL, 'end']


class OuterDerived0(OuterBase, FinalConfig):
    class CfgParams(OuterBase.CfgParams):
        CONFIG_VAL = 'outer inherited value 0'


class OuterDerived1(OuterBase, FinalConfig):
    class CfgParams(OuterBase.CfgParams):
        CONFIG_VAL = 'outer inherited value 1'


class TestBaseMetaclasses(unittest.TestCase):
    def validate_config(self, derived_cfg, expected_value):
        expected_def_value = 'def value'

        assert derived_cfg.CfgParams.CONFIG_VAL == expected_value
        assert derived_cfg.CfgParams.CONFIG_VAL_DEF == expected_def_value
        assert derived_cfg.CLASS_VAL == expected_value
        assert derived_cfg.Inner.CLASS_VAL == expected_value
        assert derived_cfg.Inner.CLASS_VAL_DEF == expected_def_value
        assert derived_cfg.Inner.InnerInner.CLASS_VAL == expected_value

        cfg_class = type(derived_cfg)
        assert cfg_class.Inner.CfgParams.CONFIG_VAL == expected_value
        assert cfg_class.Inner.CfgParams.CONFIG_VAL_DEF == expected_def_value
        assert cfg_class.Inner.CLASS_VAL_DEF == expected_def_value
        assert cfg_class.Inner.CLASS_VAL == expected_value

        inner_cfg = derived_cfg.Inner()
        assert inner_cfg.InnerInner.CfgParams.CONFIG_VAL == expected_value
        assert inner_cfg.InnerInner.CfgParams.CONFIG_VAL_DEF == expected_def_value
        assert inner_cfg.InnerInner.CLASS_VAL == expected_value

    def test_derived_config(self):
        self.validate_config(OuterDerived0(), 'outer inherited value 0')
        self.validate_config(OuterDerived1(), 'outer inherited value 1')
