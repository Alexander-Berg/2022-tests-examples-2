import dataclasses
import typing

from . import consts

SELECT_SQL = """
SELECT
    order_id,
    service,
    currency,
    complement_payment_type,
    complement_payment_id,
    complement_amount,
    originator,
    business_type,
    business_specification,
    api_version,
    is_transparent_payment
FROM eats_payments.orders WHERE order_id = %s
;
"""


UPSERT_SQL = """
INSERT INTO eats_payments.orders (
    order_id,
    service,
    currency,
    complement_payment_type,
    complement_payment_id,
    complement_amount,
    originator,
    business_type,
    business_specification,
    api_version,
    is_transparent_payment
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT(order_id)
DO UPDATE SET
    order_id = EXCLUDED.order_id,
    service = EXCLUDED.service,
    currency = EXCLUDED.currency,
    complement_payment_type = EXCLUDED.complement_payment_type,
    complement_payment_id = EXCLUDED.complement_payment_id,
    complement_amount = EXCLUDED.complement_amount,
    originator = EXCLUDED.originator,
    business_type = EXCLUDED.business_type,
    business_specification = EXCLUDED.business_specification,
    api_version = EXCLUDED.api_version,
    is_transparent_payment = EXCLUDED.is_transparent_payment
"""


@dataclasses.dataclass
class DBOrder:
    pgsql: typing.Any
    order_id: str
    service: str = consts.DEFAULT_SERVICE
    currency: str = 'RUB'
    complement_payment_type: typing.Optional[str] = None
    complement_payment_id: typing.Optional[str] = None
    complement_amount: typing.Optional[str] = None
    originator: typing.Optional[str] = consts.DEFAULT_ORIGINATOR
    business_type: typing.Optional[str] = None
    business_specification: typing.Optional[list] = None
    api_version: int = 1
    is_transparent_payment: bool = False

    def _cursor_pg(self):
        return self.pgsql['eats_payments'].cursor()

    @classmethod
    def fetch(cls, pgsql, order_id):
        order = DBOrder(pgsql=pgsql, order_id=order_id)
        order.refresh()
        return order

    def refresh(self):
        cursor = self._cursor_pg()
        cursor.execute(SELECT_SQL, [self.order_id])
        result = cursor.fetchone()

        assert result

        (
            order_id,
            service,
            currency,
            complement_payment_type,
            complement_payment_id,
            complement_amount,
            originator,
            business_type,
            business_specification,
            api_version,
            is_transparent_payment,
        ) = result

        self.order_id = order_id
        self.service = service
        self.currency = currency
        self.complement_payment_type = complement_payment_type
        self.complement_payment_id = complement_payment_id
        self.complement_amount = complement_amount
        self.originator = originator
        self.business_type = business_type
        self.business_specification = business_specification
        self.api_version = api_version
        self.is_transparent_payment = is_transparent_payment

    def upsert(self):
        cursor = self._cursor_pg()
        cursor.execute(
            UPSERT_SQL,
            [
                self.order_id,
                self.service,
                self.currency,
                self.complement_payment_type,
                self.complement_payment_id,
                self.complement_amount,
                self.originator,
                self.business_type,
                self.business_specification,
                self.api_version,
                self.is_transparent_payment,
            ],
        )
