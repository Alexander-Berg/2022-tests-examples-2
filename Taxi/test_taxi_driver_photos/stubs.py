def several_faces():
    return [(500, 500, 1000, 1000), (0, 0, 10, 10)]


def no_faces():
    return []


def face_on_the_edge():
    return [(0, 0, 100, 100)]


def avatars_mds_upload_response():
    return {
        'extra': {'svg': {'path': '/get-driver-photos/603/123/svg'}},
        'group-id': 603,
        'imagename': '123',
        'meta': {
            'crc64': 'C48CAD7438230F01',
            'md5': 'e3654575e1049c081a1b05e50972e18e',
            'modification-time': 1551452529,
            'orig-animated': False,
            'orig-format': 'JPEG',
            'orig-orientation': '',
            'orig-size': {'x': 720, 'y': 1280},
            'orig-size-bytes': 99328,
            'processed_by_computer_vision': False,
            'processed_by_computer_vision_description': (
                'computer vision is disabled'
            ),
            'processing': 'finished',
        },
        'sizes': {
            'orig': {
                'height': 720,
                'path': '/get-driver-photos/603/123/orig',
                'width': 1080,
            },
        },
    }


def driver_position_response():
    return {
        'accuracy': 0,
        'direction': -1.0,
        'lat': 55.747318999999997,
        'lon': 37.597918,
        'source': 'A',
        'speed': -1.0,
        'timestamp': 1575895046,
    }


def driver_categories_response(is_premium):
    return {
        'blacklisted': {'car': False, 'driver': False},
        'chain_free': [],
        'classes': [
            {
                'allowed': not is_premium,
                'class': 'econom',
                'grade': 8,
                'grade_air': 8,
            },
            {
                'allowed': is_premium,
                'class': 'vip',
                'forbidden_reasons': ['class', 'disabled_by_driver'],
                'grade': 8,
                'grade_air': 8,
            },
            {
                'allowed': is_premium,
                'class': 'maybach',
                'forbidden_reasons': ['class', 'disabled_by_driver'],
                'grade': 8,
                'grade_air': 8,
            },
        ],
        'mqc_status': 'can_be_called_by_mqc',
        'newbie': True,
        'payments': {
            'allowed': [
                'cash',
                'card',
                'corp',
                'applepay',
                'googlepay',
                'coupon',
                'personal_wallet',
                'coop_account',
            ],
            'driver_payment_type': 'none',
            'supported': [
                'cash',
                'card',
                'corp',
                'applepay',
                'googlepay',
                'coupon',
                'personal_wallet',
                'coop_account',
            ],
        },
        'point': [37.597918, 55.747318999999997],
        'rate': {'disabled': False},
        'requirements': ['animaltransport', 'conditioner', 'nosmoking'],
        'status_driver': 'verybusy',
        'tags': ['2orders', 'park_test_1', 'individual_entrepreneur'],
        'taximeter_status': 'busy',
    }
