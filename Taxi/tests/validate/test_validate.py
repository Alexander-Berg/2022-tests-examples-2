from mouse import Mouse, Has
from mouse.exception import ErValidate, ErNeedSelf

def test_validate(tap):
    with tap.plan(4):
        class Foo(Mouse):
            lon = Has((float, int), validate=lambda x: -180 <= x <= 180)
            lat = Has((float, int), validate=lambda x: -90 <= x <= 90)

        obj = Foo(lon=120, lat=55)
        tap.isa_ok(obj, Foo, 'instance created')

        obj.lon = 180
        obj.lat = -90
        tap.eq((obj.lon, obj.lat), (180, -90), 'lon, lat')

        with tap.raises(ErValidate, 'ErValidate'):
            obj.lon = 188

        with tap.raises(ErValidate, 'ErValidate construct'):
            Foo(lon=188, lat=55)


def test_need_self(tap):
    def _vneed_self(value, self=None, field=None):
        if not self and not field:
            raise ErNeedSelf()
        return value > 10


    with tap.plan(3):
        class Foo(Mouse):
            value = Has(int, validate=_vneed_self)

        obj = Foo(value=11)
        tap.isa_ok(obj, Foo, 'instance created')


        with tap.raises(ErValidate, 'ErValidate'):
            obj.value = 10


        with tap.raises(ErValidate, 'ErValidate constructor'):
            Foo(value=10)
