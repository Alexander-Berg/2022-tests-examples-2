#include <curl/curl.h>

#include <chrono>
#include <optional>

#include <smart_devices/tools/updater/lib/updater.h>
#include <smart_devices/tools/updater/lib/utils.h>
#include <smart_devices/tools/updater/lib/update_status.h>
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
            quasarConfig["common"]["cryptography"]["devicePublicKeyPath"] = std::string(ArcadiaSourceRoot()) + "/yandex_io/misc/cryptography/public.pem";
            quasarConfig["common"]["cryptography"]["devicePrivateKeyPath"] =
                std::string(ArcadiaSourceRoot()) + "/yandex_io/misc/cryptography/private.pem";
            quasarConfig["updatesd"]["minUpdateHour"] = 3;
            quasarConfig["updatesd"]["maxUpdateHour"] = 4;
            quasarConfig["updatesd"]["updatesExt"] = ".zip";
            quasarConfig["updatesd"]["randomWaitLimitSec"] = 3600;
            quasarConfig["updatesd"]["updateInfoPath"] = updateInfo_;

            /* allocate ports */
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

            mockUpdatesEndpoint_.onHandlePayload = [=](const TestHttpServer::Headers& header, const std::string& payload /* payload */,
                                                       TestHttpServer::HttpConnection& handler) {
                YIO_LOG_INFO("Got http payload: " << payload);
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

            UpdateStatus applyStatus(getUpdateStatePath());
            applyStatus.deleteFromDisk();
        }

        void TearDownInternal() {
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
        std::string appliedUpdateFileName_; // test_device_ota_update.sh script just copies update to filename with "_applied" added

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

Y_UNIT_TEST_SUITE(TestUpdaterGateway) {
    Y_UNIT_TEST_F(testUpdaterCriticalUpdate, Fixture) {
        auto updaterGateway = std::make_unique<UpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        auto updater = std::make_unique<IOUpdater::Updater>(updaterConfig_);
        updater->start();

        auto backendHeader = backendRequestHeaderPromise_.get_future().get();
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.verb, "GET");
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.resource, "/check_updates");
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.queryParams.getValue("device_id"), getDeviceForTests()->deviceId());
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.queryParams.getValue("version"), updaterConfig_.firmwareVersion);
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.queryParams.getValue("platform"), updaterConfig_.platform);

        auto updatesHeader = updatesRequestHeaderPromise_.get_future().get();
        UNIT_ASSERT_VALUES_EQUAL(updatesHeader.verb, "GET");
        UNIT_ASSERT_VALUES_EQUAL(updatesHeader.resource,
                                 "/yandexstation/ota/user/f0ed9b20-0220-4b3f-8f17-b8be535d4ded/quasar-2.3.1.6.406275671.20190402.zip");

        /* Wait untill updatesd download content */
        waitUntil([&]() { return (IOUpdater::fileExists(appliedUpdateFileName_) && getFileContent(appliedUpdateFileName_) == updateData_); });

        UNIT_ASSERT_VALUES_EQUAL(getFileContent(appliedUpdateFileName_), updateData_);
    }

    Y_UNIT_TEST_F(testUpdaterNonCriticalUpdate, Fixture) {
        updaterConfig_.delayTimingsPolicy =
            BackoffWithJitterPolicy(std::chrono::milliseconds(100), std::chrono::milliseconds(100), std::chrono::milliseconds(100));

        /* Set up not critical update in response */
        isUpdateCritical_ = false;
        auto updater = std::make_unique<TestableUpdater>(updaterConfig_);
        updater->startIpc();
        auto updaterGateway = std::make_unique<UpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updater->startUpdateLoop();

        ioHub_->waitConnection();
        ioHub_->setTimezone(timezone_);

        updater->waitUntilTimezoneReceived(timezone_.timezoneOffsetSec);

        YIO_LOG_DEBUG("First timestamp setting and check");
        auto nowMidnight = getStartOfDayUTC(std::chrono::system_clock::now());
        updater->currentTimestamp = nowMidnight;

        auto backendHeader = backendRequestHeaderPromise_.get_future().get();
        auto verifyBackendHeader = [&, this](const auto& header) {
            UNIT_ASSERT_VALUES_EQUAL(header.verb, "GET");
            UNIT_ASSERT_VALUES_EQUAL(header.resource, "/check_updates");
            UNIT_ASSERT_VALUES_EQUAL(header.queryParams.getValue("device_id"), getDeviceForTests()->deviceId());
            UNIT_ASSERT_VALUES_EQUAL(backendHeader.queryParams.getValue("version"), updaterConfig_.firmwareVersion);
            UNIT_ASSERT_VALUES_EQUAL(backendHeader.queryParams.getValue("platform"), updaterConfig_.platform);
        };

        verifyBackendHeader(backendHeader);

        auto updatesFuture = updatesRequestHeaderPromise_.get_future();
        UNIT_ASSERT_EQUAL(updatesFuture.wait_for(std::chrono::milliseconds(200)), std::future_status::timeout);

        YIO_LOG_DEBUG("Second timestamp setting and check");
        /* move timestamp by 1 hour ahead, so timestamp still will be not in [minUpdateHour..maxUpdateHour] range, so device won't update yet */
        updater->currentTimestamp = nowMidnight + std::chrono::hours(1) + std::chrono::seconds(-1);
        backendRequestHeaderPromise_ = std::promise<TestHttpServer::Headers>();
        setBackerRequestHeaderPromise_ = true;
        backendHeader = backendRequestHeaderPromise_.get_future().get();
        verifyBackendHeader(backendHeader);

        UNIT_ASSERT_EQUAL(updatesFuture.wait_for(std::chrono::milliseconds(200)), std::future_status::timeout);

        YIO_LOG_DEBUG("Third timestamp setting and check");
        /* move timestamp by 1 more hour ahead, So timestamp still will be in [minUpdateHour..maxUpdateHour] range, so device will update */
        updater->currentTimestamp = nowMidnight + std::chrono::hours(1) + std::chrono::seconds(1);

        auto updatesHeader = updatesFuture.get();
        UNIT_ASSERT_VALUES_EQUAL(updatesHeader.verb, "GET");
        UNIT_ASSERT_VALUES_EQUAL(updatesHeader.resource,
                                 "/yandexstation/ota/user/f0ed9b20-0220-4b3f-8f17-b8be535d4ded/quasar-2.3.1.6.406275671.20190402.zip");

        waitUntil([&]() { return (IOUpdater::fileExists(appliedUpdateFileName_) && getFileContent(appliedUpdateFileName_) == updateData_); });

        UNIT_ASSERT_VALUES_EQUAL(getFileContent(appliedUpdateFileName_), updateData_);
    }

    Y_UNIT_TEST_F(testUpdaterUpdateTimezone, Fixture) {
        auto updaterGateway = std::make_unique<UpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        auto updater = std::make_unique<TestableUpdater>(updaterConfig_);
        updater->start();

        ioHub_->waitConnection();
        ioHub_->setTimezone(timezone_);

        updater->waitUntilTimezoneReceived(timezone_.timezoneOffsetSec);

        std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Wait until message received and nothing fails;

        UNIT_ASSERT(true);
    }

    Y_UNIT_TEST_F(testCheckUpdatesMessageHandle, Fixture) {
        updaterConfig_.delayTimingsPolicy = BackoffWithJitterPolicy(
            std::chrono::milliseconds(60 * 60 * 1000), std::chrono::milliseconds(60 * 60 * 1000), std::chrono::milliseconds(60 * 60 * 1000));
        /* set up not critical update in response */
        isUpdateCritical_ = false;

        auto updaterGateway = std::make_unique<UpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        auto updater = std::make_unique<TestableUpdater>(updaterConfig_);
        updater->start();
        SteadyConditionVariable condVar;
        std::mutex testMutex;
        bool hasNoCritical{false};
        bool hasCritical{false};

        auto updatesdConnector = createIpcConnectorForTests("updatesd");
        updatesdConnector->setMessageHandler([&](const auto& msg) {
            std::lock_guard<std::mutex> guard(testMutex);
            if (msg->has_no_critical_update_found()) {
                hasNoCritical = true;
            } else if (msg->has_start_critical_update()) {
                hasCritical = true;
            }
            condVar.notify_one();
        });
        updatesdConnector->connectToService();
        updatesdConnector->waitUntilConnected();

        /* Wait until Updatesd will check backend and will see that there is no critical update */
        std::unique_lock<std::mutex> lock(testMutex);
        condVar.wait(lock, [&]() { return hasNoCritical; });

        /* Set up critical update so updatesd will receive Critical update in next check */
        isUpdateCritical_ = true;
        /* Send CheckUpdates message, so Updater will visit check_updates backend handler immediately */
        quasar::proto::QuasarMessage message;
        message.mutable_check_updates();
        updatesdConnector->sendMessage(std::move(message));

        condVar.wait(lock, [&]() { return hasCritical; });

        UNIT_ASSERT(true);
    }

    Y_UNIT_TEST_F(testUpdaterVersionWithSlash, Fixture) {
        setUpdateVersion("0.3.1.21.852829949.20201222.yandexmini_2/MP.ENG");

        auto updaterGateway = std::make_unique<UpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        auto updater = std::make_unique<Updater>(updaterConfig_);
        updater->start();

        waitUntil([&]() { return (IOUpdater::fileExists(appliedUpdateFileName_) && getFileContent(appliedUpdateFileName_) == updateData_); });

        UNIT_ASSERT_VALUES_EQUAL(getFileContent(appliedUpdateFileName_), updateData_);
    }

    Y_UNIT_TEST_F(testUpdaterUpdateState, Fixture) {
        updaterConfig_.delayTimingsPolicy =
            BackoffWithJitterPolicy(std::chrono::milliseconds(100), std::chrono::milliseconds(100), std::chrono::milliseconds(100));
        auto updater = std::make_unique<TestableUpdater>(updaterConfig_);
        updater->startIpc();

        std::atomic_bool gotNoneState{false};
        std::atomic_bool gotDownloadingState{false};
        std::atomic_bool gotApplyingState{false};
        std::vector<int> downloadProgress;

        auto updatesdConnector = createIpcConnectorForTests("updatesd");
        updatesdConnector->setMessageHandler([&](const auto& msg) {
            if (msg->has_update_state()) {
                if (msg->update_state().state() == quasar::proto::UpdateState_State::UpdateState_State_NONE) {
                    gotNoneState = true;
                } else if (msg->update_state().state() == quasar::proto::UpdateState_State::UpdateState_State_DOWNLOADING) {
                    gotDownloadingState = true;
                    downloadProgress.push_back(msg->update_state().download_progress());
                } else if (msg->update_state().state() == quasar::proto::UpdateState_State::UpdateState_State_APPLYING) {
                    gotApplyingState = true;
                }
            }
        });

        auto updaterGateway = std::make_unique<UpdaterGateway>(getDeviceForTests(), ipcFactoryForTests(), updaterConfig_.ipcSocketPath);
        updatesdConnector->connectToService();
        /* set up not critical update in response */
        isUpdateCritical_ = false;

        updater->startUpdateLoop();

        ioHub_->waitConnection();
        ioHub_->setTimezone(timezone_);

        updater->waitUntilTimezoneReceived(timezone_.timezoneOffsetSec);

        waitUntil([&gotNoneState]() { return gotNoneState.load(); });

        auto nowMidnight = getStartOfDayUTC(std::chrono::system_clock::now());
        /* Set current timestamp for updater_, so it will start to download update */
        updater->currentTimestamp = nowMidnight + std::chrono::hours(1) + std::chrono::seconds(/*updater_->getRandomWaitSeconds() + */ 1);

        /* Make sure that updatesd start to download OTA */
        waitUntil([&gotDownloadingState]() { return gotDownloadingState.load(); });

        /* Make sure that updatesd start to apply OTA */
        waitUntil([&gotApplyingState]() { return gotApplyingState.load(); });

        /* Make Sure that updatesd send progress [0 .. 100] */
        UNIT_ASSERT(!downloadProgress.empty());
        for (const auto i : downloadProgress) {
            YIO_LOG_INFO("Download progress: " << i);
        }
        for (size_t i = 0; i < downloadProgress.size() - 1; ++i) {
            UNIT_ASSERT_GE(downloadProgress[i + 1], downloadProgress[i]);
        }
        UNIT_ASSERT_VALUES_EQUAL(downloadProgress.back(), 100);
    }
}
