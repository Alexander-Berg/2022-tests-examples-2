# -*- coding: utf-8 -*-
import json

from passport.backend.logbroker_client.core.test.native_client.protobuf_handler import BaseProtobufHandlerTestCase
from passport.backend.logbroker_client.{{cookiecutter.project_slug_snake}}.handler import (
    {{cookiecutter.project_slug_upper_camel}}Handler,
)


class Test{{cookiecutter.project_slug_upper_camel}}Handler(BaseProtobufHandlerTestCase):
    pass
