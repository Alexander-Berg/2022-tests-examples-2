import datetime
import typing


class ScroogeWrapperDummy:
    def __init__(self, tables: dict) -> None:
        self.tables = tables

    async def mia_payments(
            self,
            start_dt: datetime.datetime,
            finish_dt: datetime.datetime,
            masked_pan: str,
            rrn: str,
            approval_code: str,
            service_ids: typing.List[int],
            amount: typing.Optional[float] = None,
    ) -> typing.List[dict]:
        matched_payments = []
        for payment in self.tables.get('payments', []):
            conditions = [
                payment.get('payment_dt') >= start_dt.timestamp(),
                payment.get('payment_dt') <= finish_dt.timestamp(),
                payment.get('masked_pan') == masked_pan
                if masked_pan
                else True,
                payment.get('rrn') == rrn if rrn else True,
                payment.get('approval_code') == approval_code
                if approval_code
                else True,
                payment.get('service_id') in service_ids,
                payment.get('amount') == str(amount) if amount else True,
            ]
            print(payment, rrn, approval_code)
            print(conditions)
            if all(conditions):
                matched_payments.append(payment)
        return matched_payments
