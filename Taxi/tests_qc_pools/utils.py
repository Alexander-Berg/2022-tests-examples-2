def make_pass(
        pass_id,
        exam='medcard',
        status='resolved',
        success=True,
        data=None,
        reason=None,
        invite=None,
        parent=None,
):
    result = {
        'id': pass_id,
        'entity_id': f'entity_id_{pass_id}',
        'entity_type': 'driver',
        'exam': exam,
        'modified': '2020-05-12T16:30:00.000Z',
        'status': status.upper(),
        'data': [
            {
                'field': 'surname',
                'value': f'surname{pass_id}',
                'required': True,
            },
            {'field': 'lightbox', 'value': True, 'required': True},
            {'field': 'xxx', 'required': False},
            {'field': 'year', 'value': 2018, 'required': False},
        ],
        'media': [
            {
                'code': 'front',
                'url': f'https:front_{pass_id}.jpg',
                'required': True,
            },
            {
                'code': 'back',
                'url': f'https:back_{pass_id}.jpg',
                'storage': {'type': 'type', 'bucket': 'storage_backet'},
                'required': True,
            },
            {
                'code': 'left',
                'url': f'https:left_{pass_id}.jpg',
                'storage': {'type': 'type', 'id': 'storage_id'},
                'required': True,
            },
            {
                'code': 'right',
                'url': f'https:right_{pass_id}.jpg',
                'storage': {
                    'type': 'type',
                    'id': 'storage_id',
                    'bucket': 'storage_backet',
                },
                'required': True,
            },
        ],
    }

    if result['status'] == 'RESOLVED':
        result['resolution'] = make_resolution(success=success)

    if reason:
        result['reason'] = {'code': reason}
        if invite:
            result['reason']['invite_id'] = invite

    if parent:
        result['parent'] = parent

    return result


def make_media_list(pass_id: str):
    return [
        {
            'code': 'back',
            'url': f'https:back_{pass_id}.jpg',
            'bucket': 'storage_backet',
        },
        {'code': 'front', 'url': f'https:front_{pass_id}.jpg'},
        {
            'code': 'left',
            'url': f'https:left_{pass_id}.jpg',
            'id': 'storage_id',
        },
        {
            'code': 'right',
            'url': f'https:right_{pass_id}.jpg',
            'id': 'storage_id',
            'bucket': 'storage_backet',
        },
    ]


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


def make_right_additional_field(pass_json):
    result = {}
    if 'reason' in pass_json:
        result['reason_code'] = pass_json['reason']['code']
        if 'invite_id' in pass_json['reason']:
            result['invite'] = pass_json['reason']['invite_id']

    if 'parent' in pass_json:
        result['parent_pass'] = pass_json['parent']

    return result


def make_right_data(pass_json):
    result = {
        data['field']: data['value']
        for data in pass_json['data']
        if 'value' in data
    }
    return result
