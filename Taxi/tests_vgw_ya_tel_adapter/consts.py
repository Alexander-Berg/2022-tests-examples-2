import pytest

SERVICE_NUM_BATCH_LIMIT = 2

AUTH_TOKEN = 'vgw-ya-tel-adapter-auth-token'
AUTH_HEADERS = {'Authorization': f'Basic {AUTH_TOKEN}'}
BAD_AUTH_HEADERS = {'Authorization': 'Basic 12345'}
# ya tool tvmknife unittest service -s 111 -d 111
SELF_TVM_TICKET = (
    '3:serv:CBAQ__________9_IgQIbxBv:VPaGUg_jRf7PLG_3U3znbTqd5gyi'
    'EmLX8KJ1dm-22vkmwDaCN4oFR6AUIsp6K5JKZq3A9CJYrZ6ZrUh5xDivkgJo0'
    'IcVriwC4WI6xwWlFyovb95LtolE-8jeTDSEScLGlwSI1qRH2pSwQddN92Kp9o'
    'XL8kMtDlPKLh7P-La1kfw'
)
TVM_HEADERS = {'X-Ya-Service-Ticket': SELF_TVM_TICKET}


class MockGrpc:
    TVM_TICKET = 'ya_tel_tvm_ticket'
    TEL_TICKET = 'tel_ticket'
    HOST = 'localhost'
    TIMEOUT = 3


def mock_tvm_configs():
    def wrapper(func):
        configs_wrapper = pytest.mark.config(
            TVM_ENABLED=True,
            TVM_RULES=[
                {'src': 'vgw-ya-tel-adapter', 'dst': 'vgw-ya-tel-adapter'},
                {'src': 'vgw-ya-tel-adapter', 'dst': 'ya-tel-platform'},
            ],
            TVM_SERVICES={
                'vgw-ya-tel-adapter': 111,
                'ya-tel-platform': 123,
                'statistics': 101,
                'logbroker': 201,
                'vgw-api': 202,
            },
        )
        tvm2_wrapper = pytest.mark.tvm2_ticket(
            {123: MockGrpc.TVM_TICKET, 111: SELF_TVM_TICKET},
        )
        return tvm2_wrapper(configs_wrapper(func))

    return wrapper
