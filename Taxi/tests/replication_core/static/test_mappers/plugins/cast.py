from replication_core import transform


@transform.castfunction
def _pow3(arg):
    return arg ** 3


CAST = {
    'pow3': _pow3,
}
