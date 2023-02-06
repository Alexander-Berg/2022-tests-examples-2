#include <curl/curl.h>

#include <chrono>
#include <optional>
#include <util/generic/scope.h>

#include <smart_devices/tools/updater/lib/updater.h>
#include <smart_devices/tools/updater/lib/utils.h>
#include <smart_devices/tools/updater_gateway/updater_gateway.h>
#include <smart_devices/tools/updater_gateway/tests/utils.h>

#include <yandex_io/libs/base/utils.h>
#include <yandex_io/libs/cryptography/cryptography.h>
#include <yandex_io/libs/device/device.h>
#include <yandex_io/libs/ipc/i_connector.h>
#include <yandex_io/libs/ipc/i_server.h>
#include <yandex_io/libs/json_utils/json_utils.h>
#include <yandex_io/libs/logging/logging.h>
#include <yandex_io/modules/geolocation/interfaces/timezone.h>
#include <yandex_io/tests/testlib/test_http_server.h>
#include <yandex_io/tests/testlib/test_utils.h>
#include <yandex_io/tests/testlib/unittest_helper/unit_test_fixture.h>
#include <yandex_io/tests/testlib/unittest_helper/telemetry_test_fixture.h>

#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>
#include <util/generic/scope.h>
#include <util/random/entropy.h>
#include <util/random/mersenne.h>
#include <util/system/sysstat.h>

#include <chrono>
#include <future>
#include <fstream>
#include <thread>

using namespace quasar;
using namespace quasar::TestUtils;
using namespace IOUpdater;
using namespace YandexIO;

namespace {
    class IOHubWrapper {
    public:
        IOHubWrapper(std::shared_ptr<ipc::IIpcFactory> ipcFactory)
            : server_(ipcFactory->createIpcServer("iohub_services"))
        {
            server_->listenService();
        }

        void setAllowUpdate(bool allowUpdateAll, bool allowCritical) {
            quasar::proto::QuasarMessage message;
            message.mutable_io_control()->mutable_allow_update()->set_for_all(allowUpdateAll);
            message.mutable_io_control()->mutable_allow_update()->set_for_critical(allowCritical);
            server_->sendToAll(std::move(message));
        }

        void setTimezone(const Timezone& timezone) {
            server_->sendToAll(ipc::buildMessage([&timezone](auto& msg) {
                msg.mutable_io_control()->mutable_timezone()->CopyFrom(timezone.toProto());
            }));
        }

        void waitConnection() {
            server_->waitConnectionsAtLeast(1);
        }

    private:
        std::shared_ptr<ipc::IServer> server_;
    };

    struct Fixture: public virtual QuasarUnitTestFixture {
        using Base = QuasarUnitTestFixture;

        void SetUp(NUnitTest::TTestContext& context) override {
            Base::SetUp(context);
            SetUpInternal();
        }

        void TearDown(NUnitTest::TTestContext& context) override {
            TearDownInternal();
            Base::TearDown(context);
        }

        void SetUpInternal() {
            /* Use empty default quasarConfig and setup only ACTUALY important stuff to quasarConfig */
            auto& quasarConfig = getDeviceForTests()->configuration()->getMutableConfig(testGuard_);
            quasarConfig.clear();

            /* allocate port for updater */
            quasarConfig["updatesd"]["port"] = getPort();
            quasarConfig["iohub_services"]["port"] = getPort();

            ioHub_ = std::make_unique<IOHubWrapper>(ipcFactoryForTests());

            // FIXME: This does not look good
            curl_global_init(CURL_GLOBAL_DEFAULT);
            // initLogging();
            updaterConfig_.workDir = GetWorkPath();
            updaterConfig_.downloadDir = GetWorkPath();
            updaterConfig_.ipcSocketPath = getSocketPath("u.sock");
            updaterConfig_.deviceId = getDeviceForTests()->deviceId();
            updaterConfig_.platform = "testDeviceType";
            updaterConfig_.updateInfoPath = getUpdateStatePath();
            updaterConfig_.firmwareBuildTime = 0;
            updaterConfig_.firmwareVersion = testVersion_;
            updaterConfig_.updateApplicationTimeout = std::chrono::milliseconds(20);
            updaterConfig_.updateApplicationHardTimeout = std::chrono::milliseconds(20);
            updaterConfig_.updateRangeDistribution = std::uniform_int_distribution<int>{0, 0};

            setUpdateVersion("2.3.1.6.406275671.20190402");

            mockUpdatesEndpoint_.onHandlePayload = [=](const TestHttpServer::Headers& header, const std::string& /* payload */,
                                                       TestHttpServer::HttpConnection& handler) {
                if (setUpdatesRequestHeaderPromise_) // Prevent future already satisfied error
                {
                    updatesRequestHeaderPromise_.set_value(header);
                    setUpdatesRequestHeaderPromise_ = false;
                }

                handler.doReplay(200, "application/zip", updateData_);
            };

            mockUpdatesEndpoint_.start(getPort());

            mockBackend_.onHandlePayload = [&](const TestHttpServer::Headers& header, const std::string& /* payload */,
                                               TestHttpServer::HttpConnection& handler) {
                if (setBackerRequestHeaderPromise_.exchange(false)) // Prevent future already satisfied error
                {
                    backendRequestHeaderPromise_.set_value(header);
                }
                Json::Value backendResponse;
                backendResponse["hasUpdate"] = hasUpdate_.load();
                backendResponse["critical"] = isUpdateCritical_.load();
                backendResponse["downloadUrl"] = "http://localhost:" + std::to_string(mockUpdatesEndpoint_.port()) +
                                                 "/yandexstation/ota/user/f0ed9b20-0220-4b3f-8f17-b8be535d4ded/quasar-2.3.1.6.406275671.20190402.zip";
                backendResponse["version"] = updateVersion_;
                backendResponse["crc32"] = IOUpdater::getCrc32(updateData_);

                handler.doReplay(200, "application/json", quasar::jsonToString(backendResponse));
            };
            mockBackend_.start(getPort());
            updaterConfig_.updateUrl = "http://localhost:" + std::to_string(mockBackend_.port()) + "/check_updates";

            ioHub_->setTimezone(timezone_);
        }

        void TearDownInternal() {
            updaterGateway_.reset();
            updater_.reset();
            mockBackend_.stop();
            mockUpdatesEndpoint_.stop();
            std::remove(updateFileName_.c_str());
            std::remove(appliedUpdateFileName_.c_str());
            std::remove(updateInfo_.c_str());
        }

        void setUpdateVersion(const std::string& version) {
            updateVersion_ = version;
            updateFileName_ = "update_" + IOUpdater::escapePath(updateVersion_) + ".zip";
            appliedUpdateFileName_ = updaterConfig_.workDir + "/" + updateFileName_ + "_applied";
            std::remove(updateFileName_.c_str());
            std::remove(appliedUpdateFileName_.c_str());
        }

        std::promise<TestHttpServer::Headers> updatesRequestHeaderPromise_;
        std::atomic<bool> setUpdatesRequestHeaderPromise_{true};
        std::unique_ptr<IOHubWrapper> ioHub_;
        TestHttpServer mockUpdatesEndpoint_;

        const std::string updateInfo_ = "./update-info.json";
        const std::string testVersion_ = "__test_version__";
        const char* updateData_ = "This is an update";
        std::string updateVersion_;
        std::string updateFileName_;
        std::string appliedUpdateFileName_; // test_device_ota_update.sh script just coppies update to filename with "_applied" added

        std::promise<TestHttpServer::Headers> backendRequestHeaderPromise_;
        std::atomic<bool> setBackerRequestHeaderPromise_{true};

        static std::string getUpdateStatePath() {
            return GetWorkPath() + "/update-info.json";
        }

        void resetBackendPromise() {
            YIO_LOG_INFO("Resetting backend promise");
            backendRequestHeaderPromise_ = std::promise<TestHttpServer::Headers>();
            setBackerRequestHeaderPromise_ = true;
        }

        void resetUpdatesPromise() {
            YIO_LOG_INFO("Resetting updates promise");
            updatesRequestHeaderPromise_ = std::promise<TestHttpServer::Headers>();
            setUpdatesRequestHeaderPromise_ = true;
        }

        std::atomic_bool hasUpdate_{true};
        std::atomic_bool isUpdateCritical_{true};
        TestHttpServer mockBackend_;

        YandexIO::Configuration::TestGuard testGuard_;

        const Timezone timezone_ = {
            .timezoneName = "Europe/Saratov",
            .timezoneOffsetSec = 2 * 60 * 60};

        std::unique_ptr<TestableUpdaterGateway> updaterGateway_;
        std::unique_ptr<IOUpdater::Updater> updater_;
        IOUpdater::UpdaterConfig updaterConfig_;
    };

    struct FixtureMetrics: public TelemetryTestFixture, public Fixture {
        FixtureMetrics()
            : TelemetryTestFixture() /* Init Yandex::Device with Telemetry for metrics tests */
            , Fixture()              /* Init base test environment */
        {
        }

        void SetUp(NUnitTest::TTestContext& context) override {
            TelemetryTestFixture::SetUp(context);
            Fixture::SetUpInternal();

            updateFileName_ = "update_" + IOUpdater::escapePath(updateVersion_) + ".zip";
            appliedUpdateFileName_ = updaterConfig_.workDir + "/" + updateFileName_ + "_applied";
            ::unlink(appliedUpdateFileName_.c_str());
        }

        void TearDown(NUnitTest::TTestContext& context) override {
            Fixture::TearDownInternal();
            TelemetryTestFixture::TearDown(context);
        }
    };
} /* anonymous namespace */

Y_UNIT_TEST_SUITE(TestUpdaterGatewayMetrics) {
    Y_UNIT_TEST_F(testSendsMetricForDownloadStart, FixtureMetrics) {
        std::vector<std::promise<std::pair<std::string, std::string>>> msgReceived(1);
        uint32_t msgNumber = 0;

        setEventListener([&](const std::string& event, const std::string& eventJson, YandexIO::ITelemetry::Flags /*flags*/) {
            if (msgNumber < msgReceived.size()) {
                msgReceived[msgNumber++].set_value({event, eventJson});
            }
        });

        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();
        updater_->startUpdateLoop();

        waitUntil([&]() { return (IOUpdater::fileExists(appliedUpdateFileName_) && getFileContent(appliedUpdateFileName_) == updateData_); });

        std::vector<std::pair<std::string, std::string>> metricaMessages;
        for (auto& msgPromise : msgReceived) {
            metricaMessages.push_back(msgPromise.get_future().get());
        }

        UNIT_ASSERT_VALUES_EQUAL(metricaMessages.at(0).first, "updateDownloadStart");

        const Json::Value startMessageBody = parseJson(metricaMessages.at(0).second);
        UNIT_ASSERT_VALUES_EQUAL(startMessageBody["toVersion"].asString(), updateVersion_);
        UNIT_ASSERT_VALUES_EQUAL(startMessageBody["fromVersion"].asString(), testVersion_);
    }

    Y_UNIT_TEST_F(testSendsMetricForDownloadComplete, FixtureMetrics) {
        std::vector<std::promise<std::pair<std::string, std::string>>> msgReceived(2);
        uint32_t msgNumber = 0;

        setEventListener([&](const std::string& event, const std::string& eventJson, YandexIO::ITelemetry::Flags /*flags*/) {
            if (msgNumber < msgReceived.size()) {
                msgReceived[msgNumber++].set_value({event, eventJson});
            }
        });

        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();
        updater_->startUpdateLoop();

        waitUntil([&]() { return (IOUpdater::fileExists(appliedUpdateFileName_) && getFileContent(appliedUpdateFileName_) == updateData_); });

        std::vector<std::pair<std::string, std::string>> metricaMessages;
        for (auto& msgPromise : msgReceived) {
            metricaMessages.push_back(msgPromise.get_future().get());
        }

        UNIT_ASSERT_VALUES_EQUAL(metricaMessages.at(1).first, "updateDownloadComplete");

        const Json::Value resumeMessageBody = parseJson(metricaMessages.at(1).second);
        UNIT_ASSERT_VALUES_EQUAL(resumeMessageBody["toVersion"].asString(), updateVersion_);
        UNIT_ASSERT_VALUES_EQUAL(resumeMessageBody["fromVersion"].asString(), testVersion_);
        UNIT_ASSERT(resumeMessageBody.isMember("durationMs"));
        UNIT_ASSERT(resumeMessageBody["durationMs"].asInt64() >= 0);
    }

    Y_UNIT_TEST_F(testSendsMetricForDownloadResume, FixtureMetrics) {
        std::vector<std::promise<std::pair<std::string, std::string>>> msgReceived(1);
        uint32_t msgNumber = 0;
        setEventListener([&](const std::string& event, const std::string& eventJson, YandexIO::ITelemetry::Flags /*flags*/) {
            if (msgNumber < msgReceived.size()) {
                msgReceived[msgNumber++].set_value({event, eventJson});
            }
        });

        const auto updateStorePath = updaterConfig_.downloadDir + "/update_" + updateVersion_ + ".zip";

        // simulate update file left after previous attempt
        std::ofstream storedUpdate(updateStorePath);
        storedUpdate << "Some junk";
        storedUpdate.close();

        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();
        updater_->startUpdateLoop();

        waitUntil([&]() { return (IOUpdater::fileExists(appliedUpdateFileName_) && getFileContent(appliedUpdateFileName_) == updateData_); });

        std::vector<std::pair<std::string, std::string>> metricaMessages;
        for (auto& msgPromise : msgReceived) {
            metricaMessages.push_back(msgPromise.get_future().get());
        }

        UNIT_ASSERT_VALUES_EQUAL(metricaMessages.at(0).first, "updateDownloadResume");

        const Json::Value metricaMessageBody = parseJson(metricaMessages.at(0).second);
        UNIT_ASSERT_VALUES_EQUAL(metricaMessageBody["toVersion"].asString(), updateVersion_);
        UNIT_ASSERT_VALUES_EQUAL(metricaMessageBody["fromVersion"].asString(), testVersion_);
    }

    Y_UNIT_TEST_F(testSendsMetricForDownloadError, FixtureMetrics) {
        std::vector<std::promise<std::pair<std::string, std::string>>> msgReceived(2);
        uint32_t msgNumber = 0;
        setEventListener([&](const std::string& event, const std::string& eventJson, YandexIO::ITelemetry::Flags /*flags*/) {
            if (msgNumber < msgReceived.size()) {
                msgReceived[msgNumber++].set_value({event, eventJson});
            }
        });

        mockUpdatesEndpoint_.onHandlePayload = [=](const TestHttpServer::Headers& /* headers */, const std::string& /* payload */,
                                                   TestHttpServer::HttpConnection& handler) { handler.doError("something something"); };

        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();
        updater_->startUpdateLoop();

        std::vector<std::pair<std::string, std::string>> messages;
        for (auto& msgPromise : msgReceived) {
            messages.push_back(msgPromise.get_future().get());
        }
        auto& metricaMessage = messages.at(1);

        UNIT_ASSERT_VALUES_EQUAL(metricaMessage.first, "updateDownloadError");

        const Json::Value metricaMessageBody = parseJson(metricaMessage.second);
        UNIT_ASSERT_VALUES_EQUAL(metricaMessageBody["toVersion"].asString(), updateVersion_);
        UNIT_ASSERT_VALUES_EQUAL(metricaMessageBody["fromVersion"].asString(), testVersion_);
    }

    Y_UNIT_TEST_F(testSendsMetricForSuccessfulUpdateApply, FixtureMetrics) {
        std::vector<std::promise<std::pair<std::string, std::string>>> msgReceivedBeforeReboot(2);
        std::promise<std::pair<std::string, std::string>> msgReceivedAfterReboot;
        int msgNumber = 0;
        setEventListener([&](const std::string& event, const std::string& eventJson, YandexIO::ITelemetry::Flags /*flags*/) {
            if (msgNumber < 2) {
                msgReceivedBeforeReboot[msgNumber].set_value({event, eventJson});
            } else if (msgNumber == 2) {
                msgReceivedAfterReboot.set_value({event, eventJson});
            }
            msgNumber++;
        });

        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();
        updater_->startUpdateLoop();

        for (auto& msgPromise : msgReceivedBeforeReboot) {
            msgPromise.get_future().get();
        }

        updater_.reset();

        updaterConfig_.firmwareVersion = updateVersion_;

        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();
        updater_->startUpdateLoop();

        auto afterRebootMessage = msgReceivedAfterReboot.get_future().get();

        UNIT_ASSERT_VALUES_EQUAL(afterRebootMessage.first, "updateApplySuccess");

        const Json::Value metricaMessageBody = parseJson(afterRebootMessage.second);
        UNIT_ASSERT_VALUES_EQUAL(metricaMessageBody["toVersion"].asString(), updateVersion_);
        UNIT_ASSERT_VALUES_EQUAL(metricaMessageBody["fromVersion"].asString(), testVersion_);

        setEventListener(nullptr);
    }

    Y_UNIT_TEST_F(testSendsMetricForNotSuccessfulUpdateApply, FixtureMetrics) {
        std::vector<std::promise<std::pair<std::string, std::string>>> msgReceivedBeforeReboot(2);
        std::promise<std::pair<std::string, std::string>> msgReceivedAfterReboot;
        int msgNumber = 0;
        setEventListener([&](const std::string& event, const std::string& eventJson, YandexIO::ITelemetry::Flags /*flags*/) {
            if (msgNumber < 2) {
                msgReceivedBeforeReboot[msgNumber].set_value({event, eventJson});
            } else if (msgNumber == 2) {
                msgReceivedAfterReboot.set_value({event, eventJson});
            }
            msgNumber++;
        });

        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();
        updater_->startUpdateLoop();

        for (auto& msgPromise : msgReceivedBeforeReboot) {
            msgPromise.get_future().get();
        }

        updater_.reset();
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();
        updater_->startUpdateLoop();

        auto afterRebootMessage = msgReceivedAfterReboot.get_future().get();

        UNIT_ASSERT_VALUES_EQUAL(afterRebootMessage.first, "updateApplyFailure");

        const Json::Value metricaMessageBody = parseJson(afterRebootMessage.second);
        UNIT_ASSERT_VALUES_EQUAL(metricaMessageBody["toVersion"].asString(), updateVersion_);
        UNIT_ASSERT_VALUES_EQUAL(metricaMessageBody["fromVersion"].asString(), testVersion_);

        setEventListener(nullptr);
    }

}
