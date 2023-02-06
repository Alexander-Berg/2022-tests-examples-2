import datetime
import json
import pickle

import pytest

from taxi.util.tcalc import helpers


@pytest.mark.filldb(_fill=False)
def test_tariff_class_serialization(load):
    tariff31 = json.loads(load('tariff31.json'))
    obj = helpers.Tariff(tariff31)

    pickled = pickle.dumps(obj)
    restored = pickle.loads(pickled)

    # Check data was properly pickled and restored
    assert obj.tariff == restored.tariff
    assert obj._intervals == restored._intervals

    # Check that `calc_dict()` method of restored instance works
    now = datetime.datetime.utcnow()
    orig_dct = obj.calc_dict(now, now, [])
    restored_dct = restored.calc_dict(now, now, [])
    assert orig_dct == restored_dct
