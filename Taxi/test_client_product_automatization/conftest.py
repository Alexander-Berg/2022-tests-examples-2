# pylint: disable=redefined-outer-name

# it is for fix TypeError: type 'pandas._libs.tslibs.c_timestamp._Timestamp'
# is not dynamically allocated but its base type 'FakeDatetime' is
# dynamically allocated
import pandas  # noqa: F401

import client_product_automatization.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'client_product_automatization.generated.service.pytest_plugins',
]
