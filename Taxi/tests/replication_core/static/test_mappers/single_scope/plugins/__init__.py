from replication_core import transform


@transform.castfunction
def pow2(arg):
    return arg ** 2


def _rename_foo(doc):
    yield {
        key if key != 'foo' else 'bar': value for key, value in doc.items()
    }


CAST = {
    'pow2': pow2,
}
PREMAP = {
    'rename_foo': _rename_foo,
}
