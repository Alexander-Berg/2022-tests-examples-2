import pytest
# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from reposition_relocator_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def fill_default_tariff_areas(geoareas, load_json):
    # Be careful, this will overwrite ones added by mark.geoareas
    # TODO(nknv-roman): fix it in https://st.yandex-team.ru/TAXIBACKEND-29345
    geoareas.add_many(load_json('geoareas.json'))
