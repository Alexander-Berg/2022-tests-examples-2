# -*- coding: utf-8 -*-

from common.morda import DesktopMain, DesktopCom, DesktopComTr
from common.geobase import Regions

mordas_for_domains = [
    DesktopMain(Regions.MOSCOW),
    DesktopMain(Regions.KYIV),
    DesktopMain(Regions.MINSK),
    DesktopMain(Regions.ASTANA),
    DesktopCom(),
    DesktopComTr(),
]
