# coding: utf-8
from nile.api.v1 import Record

def record(**kwargs):
    return Record(
        car_number_normalized='AY777E',
        **kwargs
    )
