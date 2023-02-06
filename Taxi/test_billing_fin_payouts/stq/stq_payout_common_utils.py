import json

from taxi.stq import async_worker_ng

from billing_fin_payouts.models.payments import payment as payment_models
from test_billing_fin_payouts import common_utils


async def check_batches(pool, data_expected, query: str = None):
    query = (
        """
        select batch_id as payout_batch_id,
                type_code,
                status_code,
                client_id,
                contract_id,
                firm_id,
                contract_type,
                currency,
                person_id,
                dry_run,
                amount_w_vat::text as amount_w_vat,
                payment_processor,
                batch_group_key,
                external_ref,
                coalesce(payload, jsonb_build_object()) as payload
            from payouts.payout_batches
    """
        if not query
        else query
    )

    await common_utils.check_pg_expected_results(
        pool=pool, query=query, data_expected=data_expected,
    )


async def check_batches_with_payout_id(pool, data_expected, query: str = None):
    query = (
        """
        select batch_id as payout_batch_id,
                type_code,
                status_code,
                client_id,
                contract_id,
                firm_id,
                contract_type,
                currency,
                person_id,
                dry_run,
                amount_w_vat::text as amount_w_vat,
                payment_processor,
                batch_group_key,
                external_ref,
                coalesce(payload, jsonb_build_object()) as payload,
                payout_id
            from payouts.payout_batches
    """
        if not query
        else query
    )

    await common_utils.check_pg_expected_results(
        pool=pool, query=query, data_expected=data_expected,
    )


async def check_cash_payment_fact(pool, data_expected, query: str = None):
    query = (
        """
        select id as cash_payment_fact_id,
            source_type,
            source_id,
            idempotency_key,
            client_id,
            contract_id,
            operation_type,
            invoice_external_id,
            amount,
            service_id,
            dry_run,
            currency,
            transaction_dt
        from payouts.cash_payment_fact
    """
        if not query
        else query
    )

    await common_utils.check_pg_expected_results(
        pool=pool, query=query, data_expected=data_expected,
    )


async def check_accruals_zero_batch(pool, data_expected):
    query = f"""
    SELECT
        idempotency_key,
        client_id,
        billing_contract_id,
        transaction_type,
        --transaction_dt,
        service_id,
        paysys_type_cc,
        terminalid,
        bill_num,
        partner_currency,
        amount,
        yandex_reward,
        reference_currency,
        reference_amount,
        dry_run
    FROM payouts.accruals
    order by idempotency_key
    """
    if data_expected:
        await common_utils.check_pg_expected_results(
            pool=pool, query=query, data_expected=data_expected,
        )


async def check_batch_change_log(pool, data_expected, query: str = None):
    query = (
        """
        select
            batch_id,
            batch_status_code,
            idempotency_key
        from payouts.batch_change_log
    """
        if not query
        else query
    )

    await common_utils.check_pg_expected_results(
        pool=pool, query=query, data_expected=data_expected,
    )


async def check_data_closed(pool, data_expected, query: str = None):
    query = (
        """
        select payout_batch_id,
            transaction_id,
            branch_type,
            amount_w_vat::text as amount_w_vat,
            amount_w_vat_applied::text as amount_w_vat_applied,
            amount_w_vat_saldo::text as amount_w_vat_saldo,
            netting_sign,
            part_count,
            payload,
            dry_run,
            payment_processor,
            batch_group_key,
            external_ref
        from payouts.data_closed
    """
        if not query
        else query
    )

    await common_utils.check_pg_expected_results(
        pool=pool, query=query, data_expected=data_expected,
    )


async def check_data_open(pool, data_expected, query: str = None):
    query = (
        """
        select  accounting_date,
                amount_w_vat::text as amount_w_vat,
                amount_w_vat_applied::text as amount_w_vat_applied,
                amount_w_vat_saldo::text as amount_w_vat_saldo,
                branch_type,
                client_id,
                contract_id,
                currency,
                firm_id,
                netting_sign,
                part_count,
                payout_batch_id,
                transaction_id,
                payload,
                dry_run,
                payment_processor,
                batch_group_key,
                external_ref
        from payouts.data_open
    """
        if not query
        else query
    )

    await common_utils.check_pg_expected_results(
        pool=pool, query=query, data_expected=data_expected,
    )


async def check_payouts(pool, data_expected):
    query = f"""
        select
            id,
            amount,
            currency,
            source_type,
            source_id,
            payment_type,
            client_id,
            contract_id,
            person_id,
            firm_id,
            payment_processor,
            payload,
            dry_run
        from payments.payouts
    """

    await common_utils.check_pg_expected_results(
        pool=pool, query=query, data_expected=data_expected,
    )


async def check_payout_event_log(pool, data_expected):
    query = f"""
            select
                id,
                payout_id,
                idempotency_key,
                status,
                payment_id
            from payments.payout_event_log
        """
    await common_utils.check_pg_expected_results(
        pool=pool, query=query, data_expected=data_expected,
    )


async def check_payments(pool, data_expected):
    query = f"""
           select
                id,
                amount,
                currency,
                source_type,
                source_id,
                payment_type,
                client_id,
                contract_id,
                person_id,
                firm_id,
                payment_processor,
                dry_run
            from payments.payments
        """
    await common_utils.check_pg_expected_results(
        pool=pool, query=query, data_expected=data_expected,
    )


async def check_payment_event_log(pool, data_expected):
    query = f"""
            select
                id,
                payment_id,
                idempotency_key,
                amount,
                amount_applied,
                external_payment_id,
                status,
                updates
            from payments.payment_event_log
        """
    await common_utils.check_pg_expected_results(
        pool=pool,
        query=query,
        jsonb_fields=['updates'],
        data_expected=data_expected,
    )


async def check_results(pool, data_json):
    await check_batches(pool=pool, data_expected=data_json['payout_batch'])
    await check_batch_change_log(
        pool=pool, data_expected=data_json['batch_change_log'],
    )
    await check_data_closed(pool=pool, data_expected=data_json['data_closed'])
    await check_data_open(pool=pool, data_expected=data_json['data_open'])
    await check_cash_payment_fact(
        pool=pool, data_expected=data_json.get('cash_payment_fact', []),
    )
    await check_accruals_zero_batch(
        pool=pool, data_expected=data_json.get('accruals', []),
    )


async def load_data(pool, interface_list):
    for item in interface_list:
        for table, data in item.items():
            query = f"""
                    INSERT INTO {table}
                    SELECT *
                        FROM json_populate_recordset (
                        NULL::{table},
                        '{json.dumps(data)}'
                        )
                    """
            async with pool.acquire() as conn:
                await conn.execute(query)


def build_task_info(
        dry_run: bool, payment_processor: payment_models.PaymentProcessor,
):
    if dry_run:
        queue = (
            'billing_fin_payouts_process_payouts_oebs_dry'
            if payment_processor == payment_models.PaymentProcessor.OEBS
            else 'billing_fin_payouts_process_payouts_bank_dry'
        )
    else:
        queue = (
            'billing_fin_payouts_process_payouts_oebs_prod'
            if payment_processor == payment_models.PaymentProcessor.OEBS
            else 'billing_fin_payouts_process_payouts_bank_prod'
        )
    return async_worker_ng.TaskInfo(
        id=1, exec_tries=1, reschedule_counter=1, queue=queue,
    )


# print('******* payouts.data_open')
# query = 'select * from payouts.data_open'
# pool = await stq3_context.pg.master_pool
# async with pool.acquire() as conn:
#     rows = await conn.fetch(query)
#     row_list = []
#     row_list.extend(dict(row) for row in rows)
#     print(row_list)
