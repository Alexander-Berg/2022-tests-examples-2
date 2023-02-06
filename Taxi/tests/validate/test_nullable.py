from mouse import Mouse, Has
from mouse.exception import ErValidate

def test_nullable(tap):
    with tap.plan(9):
        class Cls(Mouse):
            nullable = Has(int, min=10, required=False)
            required = Has(int, min=10, required=True)



        tap.ok(
            Cls(nullable=None, required=20),
            'ok nullable is None'
        )

        tap.ok(
            Cls(nullable=20, required=20),
            'ok nullable ok, required ok'
        )

        with tap.raises(ErValidate, 'invalid if nullable invalid'):
            Cls(nullable=5, required=20)

        with tap.raises(ErValidate, 'invalid if required invalid'):
            Cls(nullable=20, required=1)

        obj = Cls(nullable=20, required=20)
        tap.ok(obj, 'instance created')

        with tap.raises(ErValidate, 'invalid if nullable invalid'):
            obj.nullable = 2
        tap.eq(obj.nullable, 20, 'obj.nullable')

        obj.nullable = None

        with tap.raises(ErValidate, 'invalid if nullable invalid'):
            obj.nullable = 2
        tap.eq(obj.nullable, None, 'obj.nullable')
