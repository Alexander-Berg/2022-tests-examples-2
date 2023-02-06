import json

import pytest

from taxi_partner_contracts.internal import amocrm_manager


DRIVER_CONFIG = {
    'branding': 453842,
    'car_brand': 453828,
    'car_color': 454650,
    'car_model': 453830,
    'car_number': 453834,
    'car_year': 453832,
    'license_expire_date': 453826,
    'license_issue_date': 453824,
    'license_number': 453822,
    'license_series': 453820,
    'phone': 219657,
}
AMOCRM_CONFIG = {
    'individual_enterprenear_pipline': 807402,
    'individual_enterprenear_source': 445810,
    'not_need_offer_confirmed': ['1009978', '1021412'],
    'partner_pipline': 535210,
    'self_assigns': ['1009976', '1021412', '1022080'],
    'yandex': ['1009978', '1022078'],
}


@pytest.mark.parametrize(
    'driver_config,config,uid,lead_id,error,leads_file',
    [
        (DRIVER_CONFIG, AMOCRM_CONFIG, None, 62972109, None, 'leads_1.json'),
        (
            DRIVER_CONFIG,
            AMOCRM_CONFIG,
            'U62972109',
            None,
            None,
            'leads_1.json',
        ),
        (
            {'phone': 219657},
            AMOCRM_CONFIG,
            'U62972109',
            None,
            None,
            'leads_1.json',
        ),
        (
            {'phone': 219657},
            AMOCRM_CONFIG,
            'U62972109',
            None,
            amocrm_manager.AmocrmNoContact,
            'leads_2.json',
        ),
    ],
)
async def test_amocrm_get_lead(
        stq3_context,
        patch,
        load,
        driver_config,
        config,
        uid,
        lead_id,
        error,
        leads_file,
):
    @patch('taxi.clients.amocrm.AmocrmClient.auth')
    # pylint: disable=unused-variable
    async def auth(*args, **kwargs):
        return [None, None]

    @patch('taxi.clients.amocrm.AmocrmClient.get_leads')
    # pylint: disable=unused-variable
    async def get_leads(*args, **kwargs):
        return json.loads(load(leads_file))

    amocrm = await amocrm_manager.create_amocrm_manager(
        stq3_context, **driver_config, **config,
    )
    if error is not None:
        with pytest.raises(error):
            await amocrm.get_lead(uid, lead_id)
    else:
        await amocrm.get_lead(uid, lead_id)
        assert amocrm.lead.contact_id == 86993632
        assert amocrm.lead.uid == 'U62972109'
