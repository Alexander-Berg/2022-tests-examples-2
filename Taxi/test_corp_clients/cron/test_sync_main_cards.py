import pytest


from corp_clients.generated.cron import run_cron
from test_corp_clients.web import test_utils


@pytest.mark.now('2022-01-30T10:00:00+00:00')
async def test_sync_main_cards(patch, db, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_bound_payment_methods')
    async def _get_bound_payment_methods(operator_uid, service_id):
        return test_utils.GET_BOUND_PAYMENT_METHODS_RESP

    await run_cron.main(['corp_clients.crontasks.sync_main_cards', '-t', '0'])

    expected = load_json('expected_cards.json')

    cards_after_cron = await db.secondary.corp_cards_main.find().to_list(None)
    for card in cards_after_cron:
        # check that card_id_3 hasn't been changed by cron
        if card['_id'] != 'card_id_3':
            card.pop('updated')
        assert card == expected[card['_id']]
