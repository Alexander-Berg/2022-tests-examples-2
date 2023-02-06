#include <smart_devices/libs/zigbee/ncp/mock/mock_ncp.h>
#include <smart_devices/libs/zigbee/utils.h>
#include <smart_devices/platforms/yandexmidi/zigbee/utils.h>
#include <smart_devices/platforms/yandexmidi/zigbee/zigbee_capability.h>

#include <yandex_io/interfaces/auth/mock/auth_provider.h>
#include <yandex_io/libs/base/utils.h>
#include <yandex_io/libs/delay_timings_policy/delay_timings_policy.h>
#include <yandex_io/libs/json_utils/json_utils.h>
#include <yandex_io/tests/testlib/null_sdk/null_sdk_interface.h>
#include <yandex_io/tests/testlib/test_callback_queue.h>
#include <yandex_io/tests/testlib/unittest_helper/unit_test_fixture.h>

#include <library/cpp/testing/gmock_in_unittest/gmock.h>
#include <library/cpp/testing/unittest/registar.h>
#include <util/random/entropy.h>
#include <util/random/mersenne.h>
#include <util/stream/file.h>

namespace {

    class TestNcpFactory: public zigbee::INcpFactory {
    public:
        TestNcpFactory(zigbee::INcp* ncp)
            : ncp_(ncp)
        {
        }

        std::unique_ptr<zigbee::INcp> createNcp() const override {
            return std::unique_ptr<zigbee::INcp>(ncp_);
        }

    private:
        zigbee::INcp* ncp_;
    };

    class TestableZigbeeCapability: public ZigbeeCapability {
    public:
        TestableZigbeeCapability(std::shared_ptr<YandexIO::SDKInterface> sdk,
                                 std::weak_ptr<zigbee::IZigbeeEvents> events,
                                 const std::shared_ptr<YandexIO::IDevice>& device,
                                 std::unique_ptr<zigbee::INcpFactory> ncpFactory,
                                 std::unique_ptr<quasar::ICallbackQueue> queue,
                                 std::shared_ptr<quasar::IAuthProvider> authProvider,
                                 std::shared_ptr<quasar::IBackoffRetries> networkRestoreBackoffer)
            : ZigbeeCapability(sdk, events, device, std::move(ncpFactory), std::move(queue), authProvider, networkRestoreBackoffer)
                  {};

        std::shared_ptr<zigbee::Network> getNetwork() const {
            return network_;
        }
    };

    class MockZigbeeEvents: public zigbee::IZigbeeEvents {
    public:
        MOCK_METHOD(void, onDiscoveryStarted, (), (override));
        MOCK_METHOD(void, onDiscoveryFinished, (), (override));
    };

    class Fixture: public QuasarUnitTestFixture {
        using Base = QuasarUnitTestFixture;

        static std::string getUniqueTestWorkdir() {
            TMersenne<ui64> rng(Seed());
            std::string result = GetWorkPath() + "/" + std::to_string(rng.GenRand64());
            Mkdir(result.c_str(), MODE0777);
            return result;
        }

        std::string testDir;
        std::unique_ptr<quasar::TestCallbackQueue> queuePtr;

    public:
        quasar::TestCallbackQueue& queue;
        // This is a necessary evil, so that we won't have to change interface of a ncp factory to return shared_ptrs
        zigbee::MockNcp* ncp;
        std::shared_ptr<YandexIO::NullSDKInterface> sdk;
        std::shared_ptr<TestableZigbeeCapability> zc;
        std::shared_ptr<MockZigbeeEvents> eventHandler;
        std::shared_ptr<quasar::mock::AuthProvider> ap;
        zigbee::NetworkParameters network_;
        std::shared_ptr<quasar::IBackoffRetries> backoffer_;

        Fixture()
            : queuePtr(std::move(std::make_unique<quasar::TestCallbackQueue>()))
            , queue(*queuePtr)
                  {};

        void SetUp(NUnitTest::TTestContext& context) override {
            Base::SetUp(context);
            testDir = Fixture::getUniqueTestWorkdir();

            YandexIO::Configuration::TestGuard testGuard_;
            auto& config = getDeviceForTests()->configuration()->getMutableConfig(testGuard_);
            config["zigbee"]["networkFileName"] = testDir + "/network.dat";

            network_ = ZigbeeCapability::createNewNetworkParams();
            {
                TFsPath networkFilePath(getDeviceForTests()->configuration()->getFullConfig()["zigbee"]["networkFileName"].asString());

                networkFilePath.Parent().MkDirs();

                TFile networkFile(networkFilePath, CreateNew | WrOnly);

                auto proto = network_.toProto();
                const auto serialized = proto.SerializeAsString();

                networkFile.Write(serialized.Data(), serialized.Size());
            }

            eventHandler = std::make_shared<MockZigbeeEvents>();
            backoffer_ = std::make_shared<quasar::BackoffRetriesWithRandomPolicy>();
            ncp = new zigbee::MockNcp();
            sdk = std::make_shared<YandexIO::NullSDKInterface>();
            ap = std::make_shared<quasar::mock::AuthProvider>();
            zc = std::make_shared<TestableZigbeeCapability>(
                sdk,
                eventHandler,
                getDeviceForTests(),
                std::make_unique<TestNcpFactory>(ncp),
                std::move(queuePtr),
                ap,
                std::make_shared<quasar::BackoffRetriesWithRandomPolicy>());
        };

        void discoverNode(const zigbee::ZigbeeNode& nodeInfo) {
            const auto discoveryStartPayload = quasar::parseJson(R"({"protocols" : ["Zigbee"]})");
            YandexIO::Directive::Data data("iot_start_discovery_directive", "undefined", discoveryStartPayload);
            data.setContext("", "requestId", "", "");
            auto discoveryStartDirective = std::make_shared<YandexIO::Directive>(std::move(data));
            zc->handleDirective(discoveryStartDirective);

            auto node = zc->getNetwork()->addNode(nodeInfo);
            zc->onNodeJoined(node);
            queue.pumpDelayedCallback();
            queue.pumpDelayedCallback();
            queue.pumpDelayedCallback();

            Json::Value discoveryFinishPayload;
            discoveryFinishPayload["accepted_ids"].append(eui64ToEndpointId(nodeInfo.eui64, 1));
            const auto discoveryFinishDirective = std::make_shared<YandexIO::Directive>(YandexIO::Directive::Data("iot_finish_discovery_directive", "undefined", discoveryFinishPayload));
            zc->handleDirective(discoveryFinishDirective);
        }
    };

    Y_UNIT_TEST_SUITE_F(testZigbeeCapability, Fixture) {
        Y_UNIT_TEST(TestDeviceRemoval) {
            const zigbee::EUI64 eui64{0xAF, 0xFF, 0x56, 0x37, 0x48, 0x19, 0x23, 0x45};

            zc->start();
            zc->onSDKState(YandexIO::SDKState{.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURED});

            const zigbee::ZigbeeNode nodeInfo = {
                .nodeId = 0,
                .eui64 = eui64,
                .capability = 0,
            };

            discoverNode(nodeInfo);

            Json::Value payload;
            payload["device_ids"].append(eui64ToEndpointId(eui64, 1));
            const auto directive = std::make_shared<YandexIO::Directive>(YandexIO::Directive::Data("iot_forget_devices_directive", "undefined", payload));
            EXPECT_CALL(*ncp, requestLeave);
            zc->handleDirective(directive);
            ASSERT_TRUE(zc->getNetwork()->getNodes().empty());

            auto networkFromFs = zigbee::loadNetwork(getDeviceForTests()->configuration()->getFullConfig()["zigbee"]["networkFileName"].asString());
            ASSERT_TRUE(networkFromFs->first.nodes.empty());
        }

        Y_UNIT_TEST(TestDiscoveryCancelling) {
            const zigbee::EUI64 eui64{0xAF, 0xFF, 0x56, 0x37, 0x48, 0x19, 0x23, 0x45};

            zc->start();
            zc->onSDKState(YandexIO::SDKState{.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURED});

            Json::Value payload;
            payload["protocols"] = Json::arrayValue;
            payload["protocols"].append("Zigbee");
            YandexIO::Directive::Data data("iot_start_discovery_directive", "undefined", payload);
            data.setContext("asrText", "requestId", "parentRequestId", "displayedText");
            auto discoveryStartDirective = std::make_shared<YandexIO::Directive>(std::move(data));
            zc->handleDirective(discoveryStartDirective);
            ASSERT_TRUE(zc->getNetwork()->getNodes().empty());
            ASSERT_EQ(sdk->getEndpointStorage()->findEndpointById(eui64ToEndpointId(eui64, 1)), nullptr);

            const zigbee::ZigbeeNode nodeInfo = {
                .nodeId = 1,
                .eui64 = eui64,
                .capability = 0,
            };

            auto node = zc->getNetwork() -> addNode(nodeInfo);
            zc->onNodeJoined(node);

            const auto discoveryCancelDirective = std::make_shared<YandexIO::Directive>(YandexIO::Directive::Data("iot_cancel_discovery_directive", "undefined"));
            EXPECT_CALL(*ncp, requestLeave);
            EXPECT_CALL(*eventHandler, onDiscoveryFinished);
            zc->handleDirective(discoveryCancelDirective);
            ASSERT_TRUE(zc->getNetwork()->getNodes().empty());
            ASSERT_EQ(sdk->getEndpointStorage()->findEndpointById(eui64ToEndpointId(eui64, 1)), nullptr);
        }

        Y_UNIT_TEST(TestNetworkLoadingFromServer) {
            {
                TFsPath networkFilePath(getDeviceForTests()->configuration()->getFullConfig()["zigbee"]["networkFileName"].asString());

                networkFilePath.DeleteIfExists();
            }
            auto network = ZigbeeCapability::createNewNetworkParams();
            const auto serializedNetwork = serializeNetworkForRemoteStorage(network, {});

            const auto payload = quasar::parseJson(R"({"networks" : {"zigbee_network_base64": ")" + quasar::base64Encode(serializedNetwork.c_str(), serializedNetwork.length()) + "\"}}");
            const auto networkLoadDirective = std::make_shared<YandexIO::Directive>(YandexIO::Directive::Data("iot_restore_networks_directive", "undefined", payload));

            EXPECT_CALL(*ncp, formNetwork(network));
            zc->start();
            zc->onSDKState(YandexIO::SDKState{.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURED});
            queue.pumpDelayedCallback();
            zc->handleDirective(networkLoadDirective);
        }

        Y_UNIT_TEST(TestNetworkLoadingAfterFactory) {
            auto network = ZigbeeCapability::createNewNetworkParams();
            {
                TFsPath networkFilePath(getDeviceForTests()->configuration()->getFullConfig()["zigbee"]["networkFileName"].asString());

                networkFilePath.Parent().MkDirs();
                networkFilePath.DeleteIfExists();

                TFile networkFile(networkFilePath, CreateNew | WrOnly);

                // We don't have a version in a pre-production version, so we need to clear it
                auto proto = network.toProto();
                proto.clear_version();
                const auto serialized = proto.SerializeAsString();

                networkFile.Write(serialized.Data(), serialized.Size());
            }

            const auto serializedNetwork = serializeNetworkForRemoteStorage(network, {});

            const auto payload = quasar::parseJson("{\"networks\" : {\"zigbee_network_base64\": \"" + quasar::base64Encode(serializedNetwork.c_str(), serializedNetwork.length()) + "\"}}");
            const auto networkLoadDirective = std::make_shared<YandexIO::Directive>(YandexIO::Directive::Data("iot_restore_networks_directive", "undefined", payload));

            EXPECT_CALL(*ncp, formNetwork(network));
            zc->start();
            zc->onSDKState(YandexIO::SDKState{.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURED});
            zc->handleDirective(networkLoadDirective);
            queue.pumpDelayedCallback();
        }

        Y_UNIT_TEST(TestNetworkErasingAfterChangingUser) {

            zc->start();
            ap->setOwner(quasar::AuthInfo2{
                .source = quasar::AuthInfo2::Source::AUTHD,
                .authToken = "token1",
                .passportUid = "uid1",
                .tag = 1600000000,
            });

            zc->onSDKState(YandexIO::SDKState{.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURED});
            auto networkFromFs = zigbee::loadNetwork(getDeviceForTests()->configuration()->getFullConfig()["zigbee"]["networkFileName"].asString());
            ASSERT_EQ(networkFromFs->first, network_);

            ap->setOwner(quasar::AuthInfo2{
                .source = quasar::AuthInfo2::Source::AUTHD,
                .authToken = "token1",
                .passportUid = "uid2",
                .tag = 1600000000,
            });
            EXPECT_CALL(*ncp, formNetwork);
            queue.pumpDelayedCallback();

            const auto payload = quasar::parseJson(R"({"networks" : {"zigbee_network_base64": {}}}")");
            const auto networkLoadDirective = std::make_shared<YandexIO::Directive>(YandexIO::Directive::Data("iot_restore_networks_directive", "undefined", payload));
            zc->handleDirective(networkLoadDirective);

            ASSERT_NE(zc->getNetwork()->dump(), network_);

            networkFromFs = zigbee::loadNetwork(getDeviceForTests()->configuration()->getFullConfig()["zigbee"]["networkFileName"].asString());
            ASSERT_TRUE(networkFromFs);
            ASSERT_NE(networkFromFs->first, network_);
        }

        Y_UNIT_TEST(TestNetworkAfterChangingToSameUser) {
            const auto user = quasar::AuthInfo2{
                .source = quasar::AuthInfo2::Source::AUTHD,
                .authToken = "token1",
                .passportUid = "uid1",
                .tag = 1600000000,
            };

            zc->start();
            ap->setOwner(user);
            zc->onSDKState(YandexIO::SDKState{.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURED});
            auto networkFromFs = zigbee::loadNetwork(getDeviceForTests()->configuration()->getFullConfig()["zigbee"]["networkFileName"].asString());
            ASSERT_EQ(networkFromFs->first, network_);

            ap->setOwner(user);
            EXPECT_CALL(*ncp, formNetwork).Times(0);
            ASSERT_EQ(zc->getNetwork()->dump(), network_);

            networkFromFs = zigbee::loadNetwork(getDeviceForTests()->configuration()->getFullConfig()["zigbee"]["networkFileName"].asString());
            ASSERT_TRUE(networkFromFs);
            ASSERT_EQ(networkFromFs->first, network_);

        }

        // FIXME: Drop this after going to production
        Y_UNIT_TEST(TestNetworkLoadingPreNetworkVersion) {
            auto network = ZigbeeCapability::createNewNetworkParams();
            network.nodes.emplace(zigbee::EUI64(), zigbee::ZigbeeNode());
            {
                TFsPath networkFilePath(getDeviceForTests()->configuration()->getFullConfig()["zigbee"]["networkFileName"].asString());

                networkFilePath.Parent().MkDirs();
                networkFilePath.DeleteIfExists();

                TFile networkFile(networkFilePath, CreateNew | WrOnly);

                // We don't have a version in a pre-production version, so we need to clear it
                auto proto = network.toProto();
                proto.clear_version();
                const auto serialized = network.toProto().SerializeAsString();
                networkFile.Write(serialized.Data(), serialized.Size());
            }

            const auto serializedNetwork = serializeNetworkForRemoteStorage(network, {});

            const auto payload = quasar::parseJson(R"({"networks" : {"zigbee_network_base64": ")" + quasar::base64Encode(serializedNetwork.c_str(), serializedNetwork.length()) + "\"}}");
            const auto networkLoadDirective = std::make_shared<YandexIO::Directive>(YandexIO::Directive::Data("iot_restore_networks_directive", "undefined", payload));

            EXPECT_CALL(*ncp, formNetwork(network));
            zc->start();
            zc->onSDKState(YandexIO::SDKState{.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURED});
            zc->handleDirective(networkLoadDirective);
            ASSERT_FALSE(zc->getNetwork()->getNodes().empty());
        }

    }
} // namespace
