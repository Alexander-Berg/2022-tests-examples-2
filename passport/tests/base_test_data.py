# -*- coding: utf-8 -*-
from nginx_config_generator.configs import BaseConfig


class Config1(BaseConfig):
    _cert_names = {'localhost': {'production': 'cert1'}}
    _server_names = {'localhost': {'production': ['servername1.yandex.ru', 'm.servername1.yandex.ru']}}
    _slb_ips = {'localhost': {'production': ['10.0.0.1', '10.0.0.2']}}


CONFIG_CLASSES_WITH_PROPERTIES = {
    0: Config1,
}
