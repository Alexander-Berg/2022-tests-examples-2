from mouse import Mouse, Has
from mouse.exception import ErPluginNotFound


def test_unknown_plugin(tap):
    with tap.plan(1):
        # pylint: disable=unused-variable
        with tap.raises(ErPluginNotFound, 'Unknown plugin exception'):
            class Foo(Mouse):
                key = Has(str, unknown=True)




