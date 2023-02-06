import decimal

from taxi import billing
from taxi.stq import async_worker_ng


def money(money_str) -> billing.Money:
    amount_str, currency = money_str.split()
    return billing.Money(decimal.Decimal(amount_str), currency)


def create_task_info(
        task_id='task_id',
        queue='process_doc',
        exec_tries=0,
        reschedule_counter=0,
):
    return async_worker_ng.TaskInfo(
        id=task_id,
        queue=queue,
        exec_tries=exec_tries,
        reschedule_counter=reschedule_counter,
    )
