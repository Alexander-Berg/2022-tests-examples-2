import uuid


def make_pass(entity_id, data=None):
    result = dict(
        id=uuid.uuid4().hex,
        entity_id=entity_id,
        entity_type='vaccination',
        exam='vaccination',
        modified='2020-05-12T16:30:00.000Z',
        status='NEW',
    )

    if data:
        for item in data:
            item['required'] = item.get('required', False)
        result['data'] = data
    return result


def make_vaccination_pass(
        code, last_name, first_name=None, middle_name=None, nirvana_code=None,
):
    data = [{'field': 'last_name', 'value': last_name}]
    if code:
        data.append({'field': 'scan_result_id', 'value': code})
    if first_name:
        data.append({'field': 'first_name', 'value': first_name})
    if middle_name:
        data.append({'field': 'middle_name', 'value': middle_name})
    if nirvana_code:
        data.append(
            {
                'field': 'vaccination_qr_detection.scan_result_id',
                'value': nirvana_code,
            },
        )
    return make_pass('1_1', data=data)
