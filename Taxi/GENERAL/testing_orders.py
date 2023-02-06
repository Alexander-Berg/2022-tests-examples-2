import csv
import datetime
import enum
import os
import typing

import pymysql


class Configuration:
    def __init__(self) -> None:
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.host = os.getenv('DB_HOST')
        self.port = int(os.getenv('DB_PORT'))


class EatsOrderStatus(enum.Enum):
    def __str__(self):
        return str(self.value)

    UNCONFIRMED = 0
    CALL_CENTER_CONFIRMED = 1
    PLACE_CONFIRMED = 2
    READY_FOR_DELIVERY = 3
    DELIVERED = 4
    CANCELLED = 5
    ARRIVED_TO_CUSTOMER = 6
    CUSTOMER_NO_SHOW = 7
    AWAITING_CARD_PAYMENT = 8
    ORDER_TAKEN = 9
    OTHER = 10


def group_results(
        result: typing.Tuple,
        total_column: str,
        created_at_index: int,
        code_index: int,
        processor: typing.Callable,
        days_ago=90,
) -> typing.List:
    grouped: typing.List = []
    start_date = datetime.datetime.now().date()
    duration = datetime.timedelta(days=days_ago)
    for _shift in range(duration.days + 1):
        target_date = start_date - datetime.timedelta(days=_shift)
        grouped.append({'date': target_date, total_column: 0})

    for row in result:
        current_date = row[created_at_index].date()
        reason_code = processor(row[code_index])

        _index = -1
        for i in range(len(grouped)):
            if grouped[i]['date'] == current_date:
                _index = i

        if _index == -1:
            break

        if reason_code in grouped[_index]:
            grouped[_index][reason_code] += 1
        else:
            grouped[_index][reason_code] = 1
        grouped[_index][total_column] += 1
    return grouped


def store_csv(
        result_set: typing.List[typing.Dict], filename: str,
) -> None:
    with open(filename, 'w') as csvfile:
        fieldnames = list(result_set[0].keys())
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, extrasaction='ignore',
        )
        writer.writeheader()
        writer.writerows(result_set)


def main():
    conf = Configuration()

    connection = pymysql.connect(
        host=conf.host,
        user=conf.user,
        password=conf.password,
        database=conf.database,
        port=conf.port,
    )
    cursor = connection.cursor()
    cursor.execute(
        """
        select ocr.name, ocr.code, oc.order_id, oc.created_at
        from order_cancels as oc join order_cancel_reasons as ocr
        on oc.reason_id = ocr.id
        order by oc.created_at desc;
        """
    )
    order_cancels_result = cursor.fetchall()
    grouped = group_results(
        result=order_cancels_result,
        total_column='total_cancels',
        code_index=1,
        created_at_index=3,
        processor=lambda x: x,
    )
    store_csv(grouped, 'order_cancels_result.csv')
    cursor.execute(
        """
        select order_nr, created_at, status
        from orders order by created_at desc;
        """
    )
    orders_result = cursor.fetchall()
    grouped = group_results(
        result=orders_result,
        total_column='total',
        code_index=2,
        created_at_index=1,
        processor=lambda x: EatsOrderStatus(int(x)).name,
    )
    store_csv(grouped, 'orders_result.csv')
    connection.close()


if __name__ == '__main__':
    main()
