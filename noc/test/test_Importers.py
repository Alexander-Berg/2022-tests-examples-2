from noc.grad.grad.lib.importers import Importers, ImporterTypes, ImporterType


def test_parse_perhost_data():
    res = Importers.parse_perhost_data(
        {
            ImporterType(name="olo", type=ImporterTypes.PERHOST): {"host1": {"some": "data"}},
            ImporterType(name="olo2", type=ImporterTypes.PERHOST): {"host1": {"some": "data"}, "host2": {"no": "on"}},
            ImporterType(name="olo3", type=ImporterTypes.PERHOST): {"all": {"key": "val"}},
        }
    )
    exp = {
        'host1': {'olo': {'some': 'data'}, 'olo2': {'some': 'data'}},
        'host2': {'olo2': {'no': 'on'}},
        'all': {'olo3': {'key': 'val'}},
    }
    assert res == exp
