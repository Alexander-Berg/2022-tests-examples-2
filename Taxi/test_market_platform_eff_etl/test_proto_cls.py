# coding: utf-8
import base64

import pytest


def test_parse_from_string():
    msg = base64.decodestring(b'CmIiBTQxODQ3KlQ6IDM2NzZmYzg2ODQ0MmVhYjc4NDk5MWI0NWExNGY4N2ViQiAxY2E5MmM2NmI5NGNlOTEyODQ0NWMwMTIyYTVjYTMwZWiG74cFeIn888H07da6swE4hu+HBSrJAQpYqgFVEkUKCiIGCMr0ookGOAMSN9C+0YfQuNGB0YLQuNGC0LXQu9GMINCy0L7Qt9C00YPRhdCwIEhpdGFjaGkgRVAtQTcwMDAgUkVKDAoKIgYIyvSiiQY4AzJtMmsKDxAHIgsIuOvqjwYQkOyJTRCD6ywY0PyWBSo90J7Rh9C40YHRgtC40YLQtdC70Lgg0Lgg0YPQstC70LDQttC90LjRgtC10LvQuCDQstC+0LfQtNGD0YXQsDIQSGl0YWNoaSBFUC1BNzAwMA==')

    try:
        from market_platform_eff_etl.proto.market.idx.datacamp.proto.offer.DataCampOffer_pb2 import Offer
        offer = Offer()
        offer.ParseFromString(msg)
    except Exception as err:
        pytest.fail("Failed to parse message: {}".format(str(err)))
