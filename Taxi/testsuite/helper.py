import vh3


@vh3.decorator.operation(owner="lexsher")
def test() -> vh3.Text[str]:
    return 'Hello World'


def test_operations():
    # TODO: replace this trivial example with actually useful tests
    test()
