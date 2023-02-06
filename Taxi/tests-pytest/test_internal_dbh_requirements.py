import humbledb
import pytest

from taxi.internal.dbh import _helpers
from taxi.internal.dbh import _requirements


@pytest.mark.filldb(_fill=False)
def test_common_class_usage():
    # Test requirements inheritance

    class Driver(_helpers.Doc):
        requirements = humbledb.Embed('r')
        requirements.crazy = 'c'
        _helpers.copy_structure(_requirements.Base.obj, requirements)
        _helpers.copy_structure(_requirements.Common.obj, requirements)

    driver = Driver({
        Driver.requirements.key: {
            Driver.requirements.crazy.key: True,
            Driver.requirements.willsmoke.key: True,
        }
    })

    assert driver.requirements.crazy
    assert driver.requirements.willsmoke
    assert not driver.requirements.nosmoking
