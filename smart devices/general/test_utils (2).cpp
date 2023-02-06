#include <smart_devices/platforms/yandexmidi/zigbee/utils.h>

#include <library/cpp/testing/gmock_in_unittest/gmock.h>
#include <library/cpp/testing/unittest/registar.h>

namespace {
    Y_UNIT_TEST_SUITE(TestUtils) {
        static const zigbee::EUI64 eui64{0xDE, 0xAD, 0xBE, 0xEF, 0xCA, 0xFE, 0xBA, 0xBE};

        Y_UNIT_TEST(testSerializeDeserialize) {
            zigbee::NetworkParameters network{
                .panId = 12345,
                .extendedPanId = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08},
                .networkKey = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F},
                .networkKeySequenceNumber = 0,
                .channel = 10};
            auto serialized = serializeNetworkForRemoteStorage(network, {});
            auto deserialized = deserializeNetworkFromRemoteStorage(serialized);
            UNIT_ASSERT_EQUAL(deserialized->first, network);
        }

        Y_UNIT_TEST(testEui64ToEndpointId) {
            UNIT_ASSERT_EQUAL(eui64ToEndpointId(eui64, 1), "iot_zigbee_DEADBEEFCAFEBABE");
            UNIT_ASSERT_EQUAL(eui64ToEndpointId(eui64, 2), "iot_zigbee_DEADBEEFCAFEBABE_2");
            UNIT_ASSERT_EQUAL(eui64ToEndpointId(eui64, 242), "iot_zigbee_DEADBEEFCAFEBABE_242");
        }

        Y_UNIT_TEST(testEndpointIdToEui64) {
            UNIT_ASSERT_EQUAL(endpointIdToEui64("iot_zigbee_DEADBEEFCAFEBABE"), std::make_pair(eui64, uint8_t(1)));
            UNIT_ASSERT_EQUAL(endpointIdToEui64("iot_zigbee_DEADBEEFCAFEBABE_2"), std::make_pair(eui64, uint8_t(2)));
            UNIT_ASSERT_EQUAL(endpointIdToEui64("iot_zigbee_DEADBEEFCAFEBABE_242"), std::make_pair(eui64, uint8_t(242)));
            UNIT_ASSERT_EQUAL(endpointIdToEui64("iot_zigbee_DEADBEEFCAFEBABE_9000"), std::nullopt);
            UNIT_ASSERT_EQUAL(endpointIdToEui64("iot_zigbee_DEADBEEFCAFEBABE#2"), std::nullopt);
            UNIT_ASSERT_EQUAL(endpointIdToEui64("iot_zigbee_DEADBEEF"), std::nullopt);
            UNIT_ASSERT_EQUAL(endpointIdToEui64("iot_zigbee_NOTVALIDEUI64HEX"), std::nullopt);
            UNIT_ASSERT_EQUAL(endpointIdToEui64("DEADBEEFCAFEBABE"), std::nullopt);
        }
    }
} // namespace
