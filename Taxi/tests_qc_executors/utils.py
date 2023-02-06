def make_pass(
        pass_id,
        exam='dkk',
        entity_type='driver',
        status='resolved',
        success=True,
        data=None,
        with_data=True,
        media=None,
):
    result = {
        'id': pass_id,
        'entity_id': f'entity_{pass_id}',
        'entity_type': entity_type,
        'exam': exam,
        'modified': '2020-05-12T16:30:00.000Z',
        'status': status.upper(),
        'media': media or [],
    }

    if data is not None:
        result['data'] = data

    if media is not None:
        result['media'] = media
    elif with_data:
        result['data'] = [
            {'field': 'car_id', 'value': f'car_{pass_id}'},
            {
                'field': 'surname',
                'value': f'surname{pass_id}',
                'required': True,
            },
        ]

    if result['status'] == 'RESOLVED':
        result['resolution'] = make_resolution(success=success)

    return result


def make_resolution(success: bool):
    resolution = {
        'resolved': '2020-05-12T16:30:00.000Z',
        'identity': {'yandex_team': {'yandex_login': 'assessor'}},
    }

    if success:
        resolution['status'] = 'SUCCESS'
    else:
        resolution['status'] = 'FAIL'
        resolution['reason'] = dict(code='block', keys=['text_bad_photo'])

    return resolution


def make_vehicle_item(entity_id, has_data=True, _data=None):
    result = {'park_id_car_id': entity_id}
    if has_data:
        if _data:
            data = _data
        else:
            data = {
                'park_id': 'park_id',
                'car_id': 'car_id',
                'color': 'blue',
                'number': 'A134BC163',
                'number_normalized': 'A134BC163',
                'model': 'Vesta',
                'brand': 'Lada',
                'vin': '123456789',
                'year': '2020',
                'mileage': 321,
            }
        result['data'] = data
    return result


def make_blocks_item(entity_id, entities=None):
    result = {
        'entity_id': entity_id,
        'entities': (
            [
                {
                    'data': {
                        'blocks': {
                            'dkk': ['orders_off'],
                            'dkvu': ['orders_off'],
                            'identity': ['orders_off'],
                            'medmask': ['medmask_off'],
                            'vaccination': ['vaccination_off'],
                        },
                        'id': entity_id,
                        'type': 'driver',
                    },
                    'object_id': '60f55072e4f24cbf49e1bb10',
                    'revision': '0_1629376175_3',
                },
            ]
            if not entities
            else entities
        ),
    }
    return result
