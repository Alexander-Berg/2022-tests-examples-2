import pytest

LAST_CURSOR = 'last_cursor'

SHIFTS_V2_FULL = [
    {
        'store_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'store_external_id': '9321123123',
        'courier_id': (
            '1f01b6133ef847229380315bcaa7a7ec_ad710538487849302ba7d49cd7ae26da'
        ),
        'shift_id': '17584449e1d6419a8e94c6a503229b09000400020001',
        'updated_ts': '2022-03-22T19:00:06+00:00',
        'zone_group_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'started_at': '2022-03-22T12:51:46+00:00',
        'closes_at': '2022-03-22T19:00:05+00:00',
        'paused_at': '2022-03-22T14:08:02+00:00',
        'unpauses_at': '2022-03-22T19:00:05+00:00',
        'status': 'closed',
    },
    {
        'store_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'store_external_id': '9321123123',
        'courier_id': (
            '1f01b6133ef847229380315bcaa7a7ec_ad710538487849302ba7d49cd7ae26da'
        ),
        'shift_id': '0cb4040bc615417d81451798f0e33e54000400020001',
        'updated_ts': '2022-03-22T10:28:05+00:00',
        'zone_group_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'started_at': '2022-03-22T10:19:34+00:00',
        'closes_at': '2022-03-22T10:28:05+00:00',
        'status': 'closed',
    },
    {
        'store_id': '1163750957874358982942ba851f48ed000300020001',
        'store_external_id': '475723',
        'courier_id': (
            '0253f79a86d14b7ab9ac1d5d3017be47_3b8e99dc3fbb94cb7fb3b5685f707965'
        ),
        'shift_id': '2079cb174b254061a4982a331839452f000300020001',
        'updated_ts': '2022-03-23T07:50:32+00:00',
        'zone_group_id': '1163750957874358982942ba851f48ed000300020001',
        'started_at': '2022-03-23T07:50:31+00:00',
        'closes_at': '2022-03-23T12:00:00+00:00',
        'status': 'in_progress',
    },
    {
        'store_id': 'f95b8bec5307401ea4e0e821dded09cb000200010001',
        'store_external_id': '87254',
        'courier_id': (
            '0253f79a86d14b7ab9ac1d5d3017be47_2194bc5f9e6634361c787a6ba424f824'
        ),
        'shift_id': 'c3a6450564b74ee7ac9c7554553b1388000300020001',
        'updated_ts': '2022-03-23T09:00:06+00:00',
        'zone_group_id': 'f95b8bec5307401ea4e0e821dded09cb000200010001',
        'started_at': '2022-03-23T07:58:06+00:00',
        'closes_at': '2022-03-23T09:00:06+00:00',
        'status': 'closed',
    },
    {
        'store_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'store_external_id': '9321123123',
        'courier_id': (
            '1f01b6133ef847229380315bcaa7a7ec_68d3555803b5c8f0b39dd173b434f2af'
        ),
        'shift_id': '3d06a488830d4d1697160a47ff052712000200020001',
        'updated_ts': '2022-03-23T09:24:57+00:00',
        'zone_group_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'started_at': '2022-03-23T09:24:57+00:00',
        'closes_at': '2022-03-23T11:00:00+00:00',
        'status': 'in_progress',
    },
    {
        'store_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'store_external_id': '9321123123',
        'courier_id': (
            '1f01b6133ef847229380315bcaa7a7ec_8d6d75b32f22b258dc0ea758348ca9bc'
        ),
        'shift_id': 'a908e024958448dca8d0beff6702f4a1000400020002',
        'updated_ts': '2022-03-22T15:31:04+00:00',
        'zone_group_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'status': 'closed',
    },
    {
        'store_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'store_external_id': '237482',
        'courier_id': (
            '516d84c45aa34bc6b19ecbb223c956c3_62eb9e90063205a512eebe1444a9ed8f'
        ),
        'shift_id': '7ff7efe553c1460589c6f6fa2a073ecc000300020002',
        'updated_ts': '2022-03-22T09:31:55+00:00',
        'zone_group_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'started_at': '2022-03-22T09:25:01+00:00',
        'closes_at': '2022-03-22T09:31:54+00:00',
        'paused_at': '2022-03-22T09:29:31+00:00',
        'unpauses_at': '2022-03-22T09:30:17+00:00',
        'status': 'closed',
    },
    {
        'store_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'store_external_id': '237482',
        'courier_id': (
            '516d84c45aa34bc6b19ecbb223c956c3_62eb9e90063205a512eebe1444a9ed8f'
        ),
        'shift_id': 'bef7c6512f284141a8ecb73087942ed2000400020002',
        'updated_ts': '2022-03-22T10:15:08+00:00',
        'zone_group_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'started_at': '2022-03-22T09:54:56+00:00',
        'closes_at': '2022-03-22T10:15:07+00:00',
        'status': 'closed',
    },
    {
        'store_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'store_external_id': '9321123123',
        'courier_id': (
            '1f01b6133ef847229380315bcaa7a7ec_2cf2704109f6d298351cb0a037a2fe7c'
        ),
        'shift_id': 'd6b559d518194288a683c052d2d48a62000300020002',
        'updated_ts': '2022-03-22T14:15:08+00:00',
        'zone_group_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'started_at': '2022-03-22T13:10:34+00:00',
        'closes_at': '2022-03-22T14:15:07+00:00',
        'status': 'closed',
    },
    {
        'store_id': 'da4463fdbaa340f7b830e66836f297fa000200010001',
        'store_external_id': '60287',
        'courier_id': (
            '0253f79a86d14b7ab9ac1d5d3017be47_04c8991afb8704b153f92531ec2020cc'
        ),
        'shift_id': '74fc45654ee7466b992ce842a039a5be000500020002',
        'updated_ts': '2022-03-23T08:32:47+00:00',
        'zone_group_id': 'da4463fdbaa340f7b830e66836f297fa000200010001',
        'started_at': '2022-03-23T08:09:17+00:00',
        'closes_at': '2022-03-23T08:32:47+00:00',
        'status': 'closed',
    },
    {
        'store_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'store_external_id': '237482',
        'courier_id': (
            '516d84c45aa34bc6b19ecbb223c956c3_62eb9e90063205a512eebe1444a9ed8f'
        ),
        'shift_id': 'd12785b7680747fc9d4ec0034af9355b000300020002',
        'updated_ts': '2022-03-23T09:11:47+00:00',
        'zone_group_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'started_at': '2022-03-23T09:11:46+00:00',
        'closes_at': '2022-03-23T11:00:00+00:00',
        'status': 'in_progress',
    },
    {
        'store_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'store_external_id': '9321123123',
        'courier_id': (
            '1f01b6133ef847229380315bcaa7a7ec_21ced648830a8efa6470a8e5b3265d47'
        ),
        'shift_id': '535f30657d0b459681b35b3e9a67a050000100020000',
        'updated_ts': '2022-03-22T19:46:04+00:00',
        'zone_group_id': '6f087c7c54154702a9a569b89a53cb10000200020000',
        'status': 'closed',
    },
    {
        'store_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'store_external_id': '237482',
        'courier_id': (
            '516d84c45aa34bc6b19ecbb223c956c3_62eb9e90063205a512eebe1444a9ed8f'
        ),
        'shift_id': 'e8265b8cb66c4200ad473457e1c436ae000100020000',
        'updated_ts': '2022-03-22T09:53:52+00:00',
        'zone_group_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'started_at': '2022-03-22T09:35:47+00:00',
        'closes_at': '2022-03-22T09:53:51+00:00',
        'status': 'closed',
    },
    {
        'store_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'store_external_id': '237482',
        'courier_id': (
            '516d84c45aa34bc6b19ecbb223c956c3_62eb9e90063205a512eebe1444a9ed8f'
        ),
        'shift_id': '55420a4cf82d487a82606fd8f3536b39000300020000',
        'updated_ts': '2022-03-22T10:45:07+00:00',
        'zone_group_id': '3df797a5a84d4f669b4dd04d926cfc04000400020002',
        'started_at': '2022-03-22T10:15:08+00:00',
        'closes_at': '2022-03-22T10:45:07+00:00',
        'status': 'closed',
    },
    {
        'store_id': '1163750957874358982942ba851f48ed000300020001',
        'store_external_id': '475723',
        'courier_id': (
            '0253f79a86d14b7ab9ac1d5d3017be47_b8a8735edcb394e6dc0b1ef18aed8d2e'
        ),
        'shift_id': '39bb365e59dd4d79b538b21853193548000300020000',
        'updated_ts': '2022-03-23T08:50:05+00:00',
        'zone_group_id': '1163750957874358982942ba851f48ed000300020001',
        'started_at': '2022-03-23T07:39:22+00:00',
        'closes_at': '2022-03-23T08:50:05+00:00',
        'status': 'closed',
    },
    {
        'store_id': 'da4463fdbaa340f7b830e66836f297fa000200010001',
        'store_external_id': '60287',
        'courier_id': (
            '0253f79a86d14b7ab9ac1d5d3017be47_7c088c235da44526eeec8bb0e33d8fa3'
        ),
        'shift_id': 'eec216ac38f1432ba214ac69af75570e000200020000',
        'updated_ts': '2022-03-23T09:00:06+00:00',
        'zone_group_id': 'da4463fdbaa340f7b830e66836f297fa000200010001',
        'started_at': '2022-03-23T08:26:49+00:00',
        'closes_at': '2022-03-23T09:00:06+00:00',
        'status': 'closed',
    },
]


@pytest.fixture(autouse=False, name='grocery_wms')
def mock_grocery_wms(mockserver):
    class Context:
        def __init__(self):
            self.shifts = None
            self.shifts_changed = True

        def set_couriers_shifts(self, shifts):
            self.shifts = shifts
            self.shifts_changed = True

    context = Context()

    @mockserver.json_handler(
        '/grocery-wms/api/external/courier_shifts_v2/updates',
    )
    def _mock_wms_shifts_updates_v2(request):
        if (
                request.json['cursor'] == LAST_CURSOR
                and not context.shifts_changed
        ):
            return {'cursor': LAST_CURSOR, 'shifts': []}

        shifts = context.shifts
        if shifts is None:
            shifts = []

        context.shifts_changed = False
        return {'cursor': LAST_CURSOR, 'shifts': shifts}

    return context


@pytest.fixture(autouse=False, name='grocery_wms_full')
def mock_grocery_wms_full(mockserver):
    class Context:
        def __init__(self):
            self.shifts = None

    context = Context()

    @mockserver.json_handler(
        '/grocery-wms/api/external/courier_shifts_v2/updates',
    )
    def _mock_wms_shifts_updates_v2(request):
        if request.json['cursor'] == LAST_CURSOR:
            return {'cursor': LAST_CURSOR, 'shifts': []}

        return {'cursor': LAST_CURSOR, 'shifts': SHIFTS_V2_FULL}

    return context


@pytest.fixture(autouse=False, name='grocery_wms_null')
def mock_grocery_wms_null(mockserver):
    class Context:
        def __init__(self):
            self.shifts = None

    context = Context()

    @mockserver.json_handler(
        '/grocery-wms/api/external/courier_shifts_v2/updates',
    )
    def _mock_wms_shifts_updates_v2(request):
        assert request.json['cursor'] == ''

        if request.json['cursor'] == LAST_CURSOR:
            return {'cursor': LAST_CURSOR, 'shifts': []}

        return {'cursor': None, 'shifts': SHIFTS_V2_FULL}

    return context
