import dataclasses
import decimal
import typing


SELECT_SQL = """
SELECT
    item_id,
    order_id,
    payment_type,
    plus_amount,
    customer_service_type,
    revision_id,
FROM eats_payments.item_payment_type_revision WHERE order_id = %s
;
"""

INSERT_SQL = """
INSERT INTO eats_payments.item_payment_type_revision
(item_id, order_id, payment_type, plus_amount,
customer_service_type, revision_id)
VALUES (%s, %s, %s, %s, %s, %s);
"""


@dataclasses.dataclass
class DBItemPaymentTypePlus:
    pgsql: typing.Any
    item_id: str
    order_id: str
    payment_type: str = 'trust'
    plus_amount: decimal.Decimal = decimal.Decimal(0)
    customer_service_type: str = 'composition_products'
    revision_id: str = 'bca'

    def _cursor_pg(self):
        return self.pgsql['eats_payments'].cursor()

    @classmethod
    def fetch(cls, pgsql, item_id, order_id):
        order = DBItemPaymentTypePlus(
            pgsql=pgsql, item_id=item_id, order_id=order_id,
        )
        order.refresh()
        return order

    def refresh(self):
        cursor = self._cursor_pg()
        cursor.execute(SELECT_SQL, [self.order_id])
        result = cursor.fetchone()

        assert result

        (
            item_id,
            order_id,
            payment_type,
            plus_amount,
            customer_service_type,
            revision_id,
        ) = result

        self.item_id = item_id
        self.order_id = order_id
        self.payment_type = payment_type
        self.plus_amount = plus_amount
        self.customer_service_type = customer_service_type
        self.revision_id = revision_id

    def insert(self):
        cursor = self._cursor_pg()

        cursor.execute(
            INSERT_SQL,
            [
                self.item_id,
                self.order_id,
                self.payment_type,
                self.plus_amount,
                self.customer_service_type,
                self.revision_id,
            ],
        )
