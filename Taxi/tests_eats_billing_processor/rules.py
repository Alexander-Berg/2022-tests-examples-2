def client_info(
        client_id,
        contract_id='test_contract_id',
        employment=None,
        country_code=None,
        mvp=None,
):
    result = {'id': client_id, 'contract_id': contract_id}
    if employment is not None:
        result['employment'] = employment
    if country_code is not None:
        result['country_code'] = country_code
    if mvp is not None:
        result['mvp'] = mvp
    return result


def simple_commission(
        commission='0',
        acquiring_commission='0',
        fix_commission='0',
        additional_commission=None,
):
    return {
        'commission': commission,
        'acquiring_commission': acquiring_commission,
        'fix_commission': fix_commission,
        'additional_commission': additional_commission,
    }


def make_commission(
        commission_type,
        client_id=None,
        rule_id=None,
        params=None,
        billing_frequency=None,
):
    return {
        'type': commission_type,
        'client_id': client_id,
        'rule_id': rule_id,
        'billing_frequency': billing_frequency,
        'params': params if params is not None else simple_commission(),
    }


def simple_fine(
        fine='0',
        fix_fine='0',
        min_fine='0',
        application_period=None,
        max_fine=None,
        gmv_limit=None,
):
    fine_params = {'fine': fine, 'fix_fine': fix_fine, 'min_fine': min_fine}
    if application_period is not None:
        fine_params['application_period'] = application_period
    if max_fine is not None:
        fine_params['max_fine'] = max_fine
    if gmv_limit is not None:
        fine_params['gmv_limit'] = gmv_limit
    return fine_params


def make_fine(
        business_type,
        delivery_type,
        reason,
        rule_id=None,
        params=None,
        billing_frequency=None,
):
    return {
        'type': f'{business_type}_{delivery_type}_{reason}',
        'rule_id': rule_id,
        'params': params if params is not None else simple_fine(),
        'billing_frequency': billing_frequency,
    }
