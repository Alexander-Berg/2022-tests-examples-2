import itertools
import random
import string
import uuid

from dmp_suite.decorators import deprecated
from dmp_suite.table import LayeredLayout
from dmp_suite.greenplum import ExternalGPTable, ExternalGPLayout


@deprecated("See test_dmp_suite/examples/greenplum_test.py")
def external_gp_layout(schema='summary', prefix='test'):
    return ExternalGPLayout('{}'.format(schema), '{}_{}'.format(prefix, uuid.uuid4().hex))


class GreenplumTestTable(ExternalGPTable):
    @deprecated("See test_dmp_suite/examples/greenplum_test.py")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_layout_prefix(cls):
        return 'test'


def random_name(length=5, prefix=''):
    if not length or not length > 0:
        raise ValueError('invalid length')

    return prefix+"".join(
        itertools.chain(
            # в gp первый символ в названии должен быть буквой
            random.choices(string.ascii_lowercase, k=1),
            random.choices(string.ascii_lowercase + string.digits, k=length - 1)
        )
    )


class TestLayout(LayeredLayout):
    def __init__(self, name):
        super().__init__(layer='testing', name=name, prefix_key='test')
