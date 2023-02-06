# -*- coding: utf-8 -*-
import base64
import random


TEST_CLIENT_ID = 'lb-passport-test'
TEST_CLIENT_ID2 = 'lb-passport-test-2'
TEST_CA_CERT = str(base64.b64encode(bytearray(random.getrandbits(8) for _ in range(2048))))
TEST_CONNECT_TIMEOUT = 0.91
TEST_CREDENTIALS_CONFIG = dict(credentials_type='oauth_token')
TEST_CREDENTIALS_CONFIG2 = dict(credentials_type='tvm', tvm_alias='smth')
TEST_DATA1 = b'test_data1'
TEST_DATA2 = b'test_data2'
TEST_DATA3 = b'test_data3'
TEST_DATA4 = b'test_data4'
TEST_DATA5 = b'test_data5'
TEST_DATA6 = b'test_data6'
TEST_DATA_PORT = 12345
TEST_DATA_PORT2 = 12346
TEST_ENDPOINT1 = 'test.logbroker.yandex.net'
TEST_ENDPOINT2 = 'test2.logbroker.yandex.net'
TEST_FILE = '/var/log/yandex/test-log.log'
TEST_HOST = 'srv1.passport.yandex.net'
TEST_HOST_RE = r'^srv1\.passport\.yandex\.net$'
TEST_LOGTYPE = 'logtype1'
TEST_TIMESTAMP1 = 1600361814062
TEST_TIMESTAMP2 = 1600362561145
TEST_TOPIC1 = 'passport/test1'
TEST_TOPIC2 = 'passport/test2'
TEST_TOPIC3 = 'passport/test3'
TEST_MESSAGE_CLASS = 'MessageClass1'
TEST_PASSPORT_PROTOCOL_VERSION = '1.0'
TEST_SESSION_ID = '12345ab-12212'
