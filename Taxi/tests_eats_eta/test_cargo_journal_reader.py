from . import utils

TASK_NAME = 'cargo-journal-reader'

CORP_CLIENTS = {
    'retail_new',
    utils.EDA_CORP_CLIENT,
    utils.RETAIL_CORP_CLIENT,
    utils.MAGNIT_CORP_CLIENT,
    utils.BELARUS_CORP_CLIENT,
    utils.KAZAKHSTAN_CORP_CLIENT,
}


async def test_cargo_journal_reader_ok(taxi_eats_eta, stq):
    await taxi_eats_eta.run_task(TASK_NAME)
    assert stq.eats_eta_read_cargo_journal.times_called == len(CORP_CLIENTS)
    stq_task_ids = set()
    stq_corp_clients = set()
    for _ in range(len(CORP_CLIENTS)):
        stq_task = stq.eats_eta_read_cargo_journal.next_call()
        stq_task_ids.add(stq_task['id'])
        stq_corp_clients.add(stq_task['kwargs']['corp_client_type'])
    assert stq_task_ids == CORP_CLIENTS
    assert stq_corp_clients == CORP_CLIENTS
