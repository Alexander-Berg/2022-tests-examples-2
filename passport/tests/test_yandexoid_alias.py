# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ATT
from passport.backend.core.models.alias import YandexoidAlias
from passport.backend.core.undefined import Undefined


TEST_LOGIN = 'test'


class YandexoidAliasTestCase(unittest.TestCase):

    @staticmethod
    def get_bb_data(yastaff_login=TEST_LOGIN):
        return {
            'aliases': {
                str(ATT['yandexoid']): yastaff_login,
            },
        }

    def test_equality(self):
        alias = YandexoidAlias().parse(self.get_bb_data())

        assert Undefined != alias
        assert alias is not None
        assert object() != alias
        assert YandexoidAlias() != alias
