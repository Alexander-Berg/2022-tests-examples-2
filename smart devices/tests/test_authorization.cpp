#include <curl/curl.h>

#include <chrono>
#include <optional>
#include <util/generic/scope.h>

#include <smart_devices/tools/updater/lib/updater.h>
#include <smart_devices/tools/updater/lib/utils.h>
#include <yandex_io/services/updater_gateway/updater_gateway.h>

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
        IOHubWrapper(int port) {
            port_ = server_->init(port);
        }

        int getPort() const {
            return port_;
        }

        void setAllowUpdate(bool allowUpdateAll, bool allowCritical) {
            quasar::proto::QuasarMessage message;
            message.mutable_io_control()->mutable_allow_update()->set_for_all(allowUpdateAll);
            message.mutable_io_control()->mutable_allow_update()->set_for_critical(allowCritical);
            server_->sendToAll(message);
        }

        void setTimezone(const Timezone& timezone) {
            server_->sendToAll(ipc::buildMessage([&timezone](auto& msg) {
                msg.mutable_io_control()->mutable_timezone()->CopyFrom(timezone.toProto());
            }));
        }

        void waitConnection() {
            server_->waitConnections(1);
        }

    private:
        int port_;
        std::shared_ptr<ipc::IServer> server_ = ipc::createIpcServer();
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
            auto& quasarConfig = TestUtils::globalTestDevice()->configuration()->getMutableConfig(testGuard_);
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
            quasarConfig["updater_gateway"]["port"] = getPort();

            ioHub_ = std::make_unique<IOHubWrapper>(getPort());
            quasarConfig["iohub_services"]["port"] = ioHub_->getPort();

            // FIXME: This does not look good
            curl_global_init(CURL_GLOBAL_DEFAULT);
            // initLogging();
            updaterConfig_.workDir = GetWorkPath();
            updaterConfig_.downloadDir = GetWorkPath();
            updaterConfig_.ipcSocketPath = "/tmp/updater.sock";
            updaterConfig_.deviceId = TestUtils::globalTestDevice()->deviceId();
            updaterConfig_.platform = "testDeviceType";
            updaterConfig_.updateInfoPath = getUpdateStatePath();
            updaterConfig_.firmwareBuildTime = 0;
            updaterConfig_.firmwareVersion = testVersion_;
            updaterConfig_.updateRangeDistribution = std::chrono::seconds(0);

            setUpdateVersion("2.3.1.6.406275671.20190402");

            mockUpdatesEndpoint_.onHandlePayload = [=](const TestHttpServer::Headers& header, const std::string& payload,
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

            mockBackend_.onHandlePayload = [&](const TestHttpServer::Headers& header, const std::string& payload,
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

        std::unique_ptr<UpdaterGateway> updaterGateway_;
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

    class TestableUpdater: public IOUpdater::Updater {
    public:
        TestableUpdater(const IOUpdater::UpdaterConfig& config)
            : Updater(config)
            , currentTimestamp(std::chrono::system_clock::time_point())
        {
        }

        std::chrono::system_clock::time_point getCurrentTime() const override {
            return currentTimestamp.load();
        }

        void waitUntilTimezoneReceived(int offsetSec) const {
            YIO_LOG_INFO("Waiting for tzoffset to equate to " << offsetSec);
            while (tzOffset_ != std::chrono::seconds(offsetSec)) {
                std::this_thread::sleep_for(std::chrono::nanoseconds(20));
            }
        }

        std::atomic<std::chrono::system_clock::time_point> currentTimestamp;
    };
} /* anonymous namespace */

Y_UNIT_TEST_SUITE(TestAuthorization) {
    Y_UNIT_TEST_F(testCheckUpdatesNoAuthorizationHeader, Fixture) {
        hasUpdate_ = false;
        updaterGateway_ = std::make_unique<UpdaterGateway>(TestUtils::globalTestDevice(), TestUtils::nullIpcFactory());
        updaterGateway_->start();
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->start();

        auto backendHeader = backendRequestHeaderPromise_.get_future().get();
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.verb, "GET");
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.resource, "/check_updates");

        /* Should not contain authorization header becuase check_updates doesn't require OAuth */
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.headers.count("authorization"), 0);
        /* Only 3 default & 2 signature headers should be set up */
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.headers.size(), 3 + 2);

        UNIT_ASSERT_VALUES_EQUAL(backendHeader.headers.count("accept"), 1);
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.headers.count("host"), 1);
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.headers.count("user-agent"), 1);

        UNIT_ASSERT_VALUES_EQUAL(backendHeader.headers.count("x-quasar-signature"), 1);
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.headers.count("x-quasar-signature-version"), 1);
    }

    Y_UNIT_TEST_F(testCheckUpdatesSignature, Fixture) {
        hasUpdate_ = false;
        updaterGateway_ = std::make_unique<UpdaterGateway>(TestUtils::globalTestDevice(), TestUtils::nullIpcFactory());
        updaterGateway_->start();
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->start();

        auto backendHeader = backendRequestHeaderPromise_.get_future().get();
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.verb, "GET");
        UNIT_ASSERT_VALUES_EQUAL(backendHeader.resource, "/check_updates");

        UNIT_ASSERT_VALUES_EQUAL(backendHeader.getHeader("x-quasar-signature-version"), "2");

        Cryptography cryptography;
        cryptography.loadPublicKey(std::string(ArcadiaSourceRoot()) + "/yandex_io/misc/cryptography/public.pem");

        UNIT_ASSERT(cryptography.checkSignature(backendHeader.query, quasar::base64Decode(urlDecode(backendHeader.getHeader("x-quasar-signature")))));
    }

    Y_UNIT_TEST_F(testDownloadNoAuthorization, Fixture) {
        updaterGateway_ = std::make_unique<UpdaterGateway>(TestUtils::globalTestDevice(), TestUtils::nullIpcFactory());
        updaterGateway_->start();
        updater_ = std::make_unique<Updater>(updaterConfig_);
        updater_->start();

        auto updatesHeader = updatesRequestHeaderPromise_.get_future().get();

        /* Should not contain authorization header becuase check_updates doesn't require OAuth */
        UNIT_ASSERT_VALUES_EQUAL(updatesHeader.headers.count("authorization"), 0);
        /* Only 2 default headers should be set up */
        UNIT_ASSERT_VALUES_EQUAL(updatesHeader.headers.size(), 2);

        /* Check that updater do not set up any unexpected headers */
        UNIT_ASSERT_VALUES_EQUAL(updatesHeader.headers.count("accept"), 1);
        UNIT_ASSERT_VALUES_EQUAL(updatesHeader.headers.count("host"), 1);
    }
}
