# -*- coding: utf-8 -*-
from common import schema
from common.client import VpsClient


def test_schema():
    params = {'vp_ids': 'MordaV2View'}
    client = VpsClient()
    res = client.simple_get(params).send()
    data = res.json()
    schema.validate_schema_by_service(data, 'vps')
