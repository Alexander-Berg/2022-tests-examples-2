# -*- coding: utf-8 -*-
import unittest


class TestEntryCase(unittest.TestCase):
    def setUp(self, converter_cls, entry_cls, add_fields=None):
        self.uid = 123
        self.user_ip = '127.0.0.1'
        self.fields = dict(uid=self.uid, user_ip=self.user_ip)
        if isinstance(add_fields, dict):
            self.fields.update(add_fields)
        self.converter = converter_cls()
        self.entry = entry_cls(**self.fields)

    def get_new_field_from_log(self, field_name, converter_cls, log_msg,):
        for value, name in zip(log_msg.split(' '), converter_cls.fields):
            if name == field_name:
                return value
        return None
