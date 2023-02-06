#include <curl/curl.h>

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
    struct Fixture: public virtual QuasarUnitTestFixture {
        using Base = QuasarUnitTestFixture;

        void SetUp(NUnitTest::TTestContext& context) override {
            Base::SetUp(context);

            SetUpInternal();
        }

        void SetUpInternal() {
            /* Use empty default quasarConfig and setup only ACTUALY important stuff to quasarConfig */
            auto& quasarConfig = getDeviceForTests()->configuration()->getMutableConfig(testGuard_);
            quasarConfig.clear();
            quasarConfig["common"]["cryptography"]["devicePublicKeyPath"] = std::string(ArcadiaSourceRoot()) + "/yandex_io/misc/cryptography/public.pem";
            quasarConfig["common"]["cryptography"]["devicePrivateKeyPath"] =
                std::string(ArcadiaSourceRoot()) + "/yandex_io/misc/cryptography/private.pem";
            quasarConfig["updater_gateway"]["minUpdateHour"] = 3;
            quasarConfig["updater_gateway"]["maxUpdateHour"] = 4;
            quasarConfig["updater_gateway"]["updatesExt"] = ".zip";
            quasarConfig["updater_gateway"]["randomWaitLimitSec"] = 3600;
            quasarConfig["updater_gateway"]["updateInfoPath"] = updateInfo_;

            /* allocate port for updater */
            const int updaterPort = getPort();
            quasarConfig["updater_gateway"]["port"] = updaterPort;
            quasarConfig["updatesd"]["port"] = updaterPort;
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

        void TearDown(NUnitTest::TTestContext& context) override {
            TearDownInternal();

            Base::TearDown(context);
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

Y_UNIT_TEST_SUITE(TestDeadlinePassing) {
    Y_UNIT_TEST_F(testCheckUpdaterSendReadyToApplyUpdateMessage, Fixture) {
        SteadyConditionVariable condVar;
        std::mutex testMutex;
        bool hasReadyToApplyUpdate{false};

        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();

        auto updatesdConnector = createIpcConnectorForTests("updatesd");
        updatesdConnector->setMessageHandler([&](const auto& msg) {
            std::lock_guard<std::mutex> guard(testMutex);
            if (msg->has_ready_to_apply_update()) {
                hasReadyToApplyUpdate = true;
                condVar.notify_one();
            }
        });
        updatesdConnector->connectToService();
        updatesdConnector->waitUntilConnected();
        updater_->startUpdateLoop();

        /* Updater should have update to apply, so wait until receive ready_to_apply_update messages */
        std::unique_lock<std::mutex> lock(testMutex);
        condVar.wait(lock, [&]() { return hasReadyToApplyUpdate; });

        UNIT_ASSERT(true);
    }

    Y_UNIT_TEST_F(testUpdaterConfirmOta, Fixture) {
        auto downloadPormise = std::make_shared<std::promise<void>>();
        mockUpdatesEndpoint_.onHandlePayload = [downloadPormise, this](const TestHttpServer::Headers& /* headers */, const std::string& /* payload */,
                                                                       TestHttpServer::HttpConnection& handler) {
            downloadPormise->set_value();
            handler.doReplay(200, "application/zip", updateData_);
        };

        SteadyConditionVariable condVar;
        std::mutex testMutex;
        bool hasReadyToApplyUpdate{false};

        /* Set up very large Soft and Hard timeouts for ota confirmation, so Updater won't visit mockUpdatesEndpoint_
         * without confirm
         */
        updaterConfig_.updateApplicationTimeout = std::chrono::milliseconds(3600000);
        updaterConfig_.updateApplicationHardTimeout = std::chrono::milliseconds(3600000);

        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();

        auto updatesdConnector = createIpcConnectorForTests("updatesd");
        updatesdConnector->setMessageHandler([&](const auto& msg) {
            std::lock_guard<std::mutex> guard(testMutex);
            if (msg->has_ready_to_apply_update()) {
                hasReadyToApplyUpdate = true;
                condVar.notify_one();
            }
        });

        updatesdConnector->connectToService();
        updatesdConnector->waitUntilConnected();
        updater_->startUpdateLoop();

        /* Updater should have update to apply, so wait until receive ready_to_apply_update messages */
        {
            std::unique_lock<std::mutex> lock(testMutex);

            condVar.wait(lock, [&]() { return hasReadyToApplyUpdate; });
        }

        auto downloadFuture = downloadPormise->get_future();
        /* Make sure that Updater do not visit backend to download ota without confirmation */
        auto status = downloadFuture.wait_for(std::chrono::seconds(5));
        UNIT_ASSERT_EQUAL(status, std::future_status::timeout);

        /* Confirm OTA */
        quasar::proto::QuasarMessage message;
        message.mutable_confirm_update_apply();
        updatesdConnector->sendMessage(std::move(message));

        /* Make sure that updatesd will download ota after confirmation */
        downloadFuture.get();
    }

    Y_UNIT_TEST_F(testUpdaterHardDeadline, Fixture) {
        auto downloadPormise = std::make_shared<std::promise<void>>();
        mockUpdatesEndpoint_.onHandlePayload = [downloadPormise, this](const TestHttpServer::Headers& /* headers */, const std::string& /* payload */,
                                                                       TestHttpServer::HttpConnection& handler) {
            downloadPormise->set_value();
            handler.doReplay(200, "application/zip", updateData_);
        };

        // In this test set up  quite big Soft Timeout and run postponesWorker that will send postpone messages
        // in busyloop. Updater should download OTA anyway because HardDeadline should exceed
        updaterConfig_.updateApplicationTimeout = std::chrono::milliseconds(10000);
        updaterConfig_.updateApplicationHardTimeout = std::chrono::milliseconds(35000);
        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();

        SteadyConditionVariable condVar;
        std::mutex testMutex;
        bool hasReadyToApplyUpdate{false};

        auto updatesdConnector = createIpcConnectorForTests("updatesd");
        updatesdConnector->setMessageHandler([&](const auto& msg) {
            std::lock_guard<std::mutex> guard(testMutex);
            if (msg->has_ready_to_apply_update()) {
                hasReadyToApplyUpdate = true;
                condVar.notify_one();
            }
        });
        updatesdConnector->connectToService();
        updatesdConnector->waitUntilConnected();
        updater_->startUpdateLoop();

        std::atomic_bool stopped{false};
        auto postponesWorker = std::thread([&]() {
            // Simple busy loop which always Ping Updater with postpone messages
            while (!stopped) {
                quasar::proto::QuasarMessage message;
                message.mutable_postpone_update_apply();
                updatesdConnector->sendMessage(std::move(message));
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
        });

        Y_DEFER {
            stopped = true;
            postponesWorker.join();
        };

        // Updater should have update to apply, so wait until receive ready_to_apply_update message
        {
            std::unique_lock<std::mutex> lock(testMutex);
            condVar.wait(lock, [&]() { return hasReadyToApplyUpdate; });
        }
        auto downloadFuture = downloadPormise->get_future();
        // Make sure that Updater do not visit backend to download ota without confirmation
        auto status = downloadFuture.wait_for(std::chrono::seconds(20));
        UNIT_ASSERT_EQUAL_C(status, std::future_status::timeout, "Updater visited backend before deadline");

        // Make sure that updatesd will download ota because of Hard timeout
        downloadFuture.get();
    }

    Y_UNIT_TEST_F(testUpdaterSoftDeadline, Fixture) {
        auto downloadPormise = std::make_shared<std::promise<void>>();
        mockUpdatesEndpoint_.onHandlePayload = [downloadPormise, this](const TestHttpServer::Headers& /* headers */, const std::string& /* payload */,
                                                                       TestHttpServer::HttpConnection& handler) {
            downloadPormise->set_value();
            handler.doReplay(200, "application/zip", updateData_);
        };

        // Set up unreachable hard deadline, and small enough soft deadline. Ota should be downloaded after Soft Deadline
        updaterConfig_.updateApplicationTimeout = std::chrono::milliseconds(1000);
        updaterConfig_.updateApplicationHardTimeout = std::chrono::milliseconds(3600000);
        updaterGateway_ = std::make_unique<TestableUpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->startIpc();
        updaterGateway_->waitUntilUpdaterIPCConnected();

        SteadyConditionVariable condVar;
        std::mutex testMutex;
        bool hasReadyToApplyUpdate{false};

        auto updatesdConnector = createIpcConnectorForTests("updatesd");
        updatesdConnector->setMessageHandler([&](const auto& msg) {
            std::lock_guard<std::mutex> guard(testMutex);
            if (msg->has_ready_to_apply_update()) {
                hasReadyToApplyUpdate = true;
                condVar.notify_one();
            }
        });
        updatesdConnector->connectToService();
        updatesdConnector->waitUntilConnected();

        updater_->startUpdateLoop();

        // Updater should have update to apply, so wait until receive ready_to_apply_update messages
        std::unique_lock<std::mutex> lock(testMutex);
        condVar.wait(lock, [&]() { return hasReadyToApplyUpdate; });

        auto downloadFuture = downloadPormise->get_future();

        // Updater should download OTA without any confirmations because Soft Deadline should exceed
        downloadFuture.get();
    }
}
