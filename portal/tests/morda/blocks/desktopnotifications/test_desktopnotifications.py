# -*- coding: utf-8 -*-
import allure

from common.morda import DesktopMain
from common.geobase import Regions
from common.blocks import existance, fetch_data, check_show


BLOCK = 'DesktopNotifications'


@allure.feature('morda', 'DesktopNotifications')
class TestDesktopNotificationsBig(object):
    def setup_class(cls):
        data = fetch_data(DesktopMain(region=Regions.MOSCOW), [BLOCK])
        cls.block = data.get(BLOCK)

    @allure.story('block exists')
    def test_desktopnotifications_existance(self):
        existance(self.block)

    @allure.story('block show')
    def test_desktopnotifications_show(self):
        check_show(self.block)

    @allure.story('cards')
    def test_desktopnotifications_events(self):
        name_dict = dict()
        for card in self.block.get('cards'):
            name_dict[card.get('name')] = 1

        for name in ('zen', 'login', 'stream', 'district'):
            assert name_dict[name]
