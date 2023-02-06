# -*- coding: utf-8 -*-
from passport.backend.core.builders.base.faker.fake_builder import BaseFakeBuilder
from passport.backend.logbroker_client.account_events.notify import NotifyClient


class FakeNotify(BaseFakeBuilder):
    def __init__(self):
        super(FakeNotify, self).__init__(NotifyClient)

        self.set_notify_response_value = self.set_response_value_without_method
        self.set_notify_response_side_effect = self.set_response_side_effect_without_method
