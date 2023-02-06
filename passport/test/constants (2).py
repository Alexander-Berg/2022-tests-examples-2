# -*- coding: utf-8 -*-
from passport.backend.utils.string import smart_bytes


TEST_NAME1 = 'name1'
TEST_HOST1 = 'host1'
TEST_PORT1 = 'port1'
TEST_TOPIC1 = 'topic1'
TEST_NAME2 = 'name2'
TEST_HOST2 = 'host2'
TEST_PORT2 = 'port2'
TEST_TOPIC2 = 'topic2'
TEST_SOURCE_ID_PREFIX = 'source_id_123'
TEST_UUID = 'b5133fe1-379a-4ed2-b4bf-163a152c6971'
TEST_SOURCE_ID = smart_bytes('{}-163a152c6971'.format(TEST_SOURCE_ID_PREFIX))
TEST_CONNECT_TIMEOUT = 0.5
TEST_WRITE_TIMEOUT = 0.6
TEST_PAYLOAD = 'payload-abcdefghijklmnopqrstuvwxyz1234567890'
TEST_PAYLOAD_UNICODE = u'фывфыфыфыфы'
TEST_PAYLOAD_UNICODE_ENCODED = smart_bytes(u'str:фывфыфыфыфы')
TEST_PAYLOAD_ENCODED = smart_bytes('str:{}'.format(TEST_PAYLOAD))
TEST_META = {'key1': 'value1', 'key2': 'value2'}
TEST_SEQ = 15
TEST_CREDENTIALS_CONFIG_OAUTH = {'credentials_type': 'oauth_token'}
TEST_TVM_ALIAS = 'tvm_alias1'
TEST_CREDENTIALS_CONFIG_TVM = {'credentials_type': 'tvm', 'tvm_alias': TEST_TVM_ALIAS}
TEST_OAUTH_TOKEN = 'as9a-nc-ancs9a-9ancs-'
TEST_LOGBROKER_WRITER_CONFIG = {
    'host': TEST_HOST1,
    'port': TEST_PORT1,
    'topic': TEST_TOPIC1,
    'message_class': 'test.Class',
    'source_id_prefix': TEST_SOURCE_ID_PREFIX,
    'credentials_config': TEST_CREDENTIALS_CONFIG_OAUTH,
}
TEST_VERSION = (1, 0, 123456)
TEST_STR_VERSION = '1.0.123456'
