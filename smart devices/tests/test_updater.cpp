#include <smart_devices/tools/updater/tests/lib/base_fixture.h>
#include <smart_devices/tools/updater/tests/lib/http_server.h>
#include <smart_devices/tools/updater/tests/lib/utils.h>
#include <smart_devices/tools/updater/ipc/ipc_client.h>
#include <smart_devices/tools/updater/lib/updater.h>
#include <smart_devices/tools/updater/lib/utils.h>

#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/tests_data.h>

#include <utility>

using namespace IOUpdater;

namespace {

    class Fixture: public BaseFixture {
    public:
        Fixture()
            : ipcClient_(socketPath_, [this](IOUpdater::proto::UpdaterState msg) { pushMessage(std::move(msg)); })
        {
            mockBackend_.addHandler("/check_updates", [this]() {
                Json::Value backendResponse;
                backendResponse["hasUpdate"] = true;
                backendResponse["critical"] = isCritical_.load();
                backendResponse["downloadUrl"] = std::string{mockBackend_.address() + "/download/ota.zip"};
                backendResponse["version"] = updateVersion_;
                backendResponse["crc32"] = IOUpdater::getCrc32(updateData_);
                THttpResponse resp;
                resp.SetHttpCode(HTTP_OK);
                Json::FastWriter writer;
                const TString respStr{writer.write(backendResponse)};
                resp.SetContent(respStr, "application/json");
                return resp;
            });

            mockBackend_.addHandler("/download/ota.zip", [this] {
                const auto code = failDownload_.load() ? HTTP_INTERNAL_SERVER_ERROR : HTTP_OK;
                THttpResponse resp;
                resp.SetHttpCode(code);
                resp.SetContent(TString{updateData_}, "application/zip");
                return resp;
            });
        };

    protected:
        std::string updateVersion_{"1234"};
        std::mutex mutex_;
        std::condition_variable cv_;
        IPCClient ipcClient_;
        std::atomic_bool failDownload_{false};
        std::atomic_bool isCritical_{true};
        const std::string updateData_ = "This is an update";
        TestHTTPServer mockBackend_;

    public:
        void sendWithAck(const IOUpdater::proto::UpdaterCommand& command, const std::function<bool()>& ackPred) {
            auto ec = ipcClient_.send(command);
            while (ec) {
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
                ec = ipcClient_.send(command);
            }
            while (ackPred()) {
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
            }
        }

        void ensureConnectedUpdaterStart(IOUpdater::Updater& updater) {
            updater.startIpc();
            while (!ipcClient_.isConnected()) {
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
            }
            updater.startUpdateLoop();
        }
    };

    class TestableUpdater: public IOUpdater::Updater {
    public:
        explicit TestableUpdater(const IOUpdater::UpdaterConfig& config)
            : Updater(config)
            , currentTimestamp(std::chrono::system_clock::time_point())
        {
        }

        std::chrono::system_clock::time_point getCurrentTime() const override {
            return currentTimestamp.load();
        }

        std::atomic<std::chrono::system_clock::time_point> currentTimestamp;
    };

} /* anonymous namespace */

Y_UNIT_TEST_SUITE_F(TestUpdater, Fixture) {
    Y_UNIT_TEST(testTzOffsetDownloadingAndApplication) {
        auto config = defaultUpdaterConfig_;
        config.updateUrl = "update_check_url";
        config.updateApplicationTimeout = std::chrono::milliseconds(20);
        config.updateApplicationHardTimeout = std::chrono::milliseconds(20);

        TestableUpdater updater(config);
        ensureConnectedUpdaterStart(updater);
        UNIT_ASSERT_EQUAL(updater.getTzOffset(), std::chrono::seconds(0));

        std::tm tm = {.tm_sec = 34, .tm_min = 35, .tm_hour = 12, .tm_mday = 14, .tm_mon = 3, .tm_year = 121};

        updater.currentTimestamp = std::chrono::system_clock::from_time_t(timegm(&tm));
        IOUpdater::Update update("Version", "download_url", "type", "urgency", 0xDE);
        update.urgency = "critical";
        UNIT_ASSERT(updater.shouldDownload(update));
        UNIT_ASSERT(updater.shouldApply(update));
        update.urgency = "regular";
        UNIT_ASSERT(!updater.shouldDownload(update));
        UNIT_ASSERT(!updater.shouldApply(update));

        tm = {.tm_sec = 34, .tm_min = 35, .tm_hour = 3, .tm_mday = 14, .tm_mon = 3, .tm_year = 121};
        updater.currentTimestamp = std::chrono::system_clock::from_time_t(timegm(&tm));
        UNIT_ASSERT(updater.shouldDownload(update));
        UNIT_ASSERT(updater.shouldApply(update));
        update.urgency = "critical";
        UNIT_ASSERT(updater.shouldDownload(update));
        UNIT_ASSERT(updater.shouldApply(update));

        update.urgency = "regular";
        tm = {.tm_sec = 34, .tm_min = 35, .tm_hour = 0, .tm_mday = 14, .tm_mon = 3, .tm_year = 121};
        updater.currentTimestamp = std::chrono::system_clock::from_time_t(timegm(&tm));
        UNIT_ASSERT(!updater.shouldDownload(update));
        UNIT_ASSERT(!updater.shouldApply(update));

        constexpr int timezoneOffsetSec = 3 * 60 * 60;
        IOUpdater::proto::UpdaterCommand command;
        command.set_op(IOUpdater::proto::UpdaterCommand_Operation_set_tzoffset);
        command.set_timezone_offset_sec(timezoneOffsetSec);
        sendWithAck(command, [&]() { return updater.getTzOffset() != std::chrono::seconds(timezoneOffsetSec); });
        UNIT_ASSERT_EQUAL(updater.getTzOffset(), std::chrono::seconds(timezoneOffsetSec));
        UNIT_ASSERT(updater.shouldDownload(update));
        UNIT_ASSERT(updater.shouldApply(update));
    }

    Y_UNIT_TEST(testRandomOffsetForLoadSpreading) {
        auto config = defaultUpdaterConfig_;
        config.updateUrl = "update_check_url";
        config.updateApplicationTimeout = std::chrono::milliseconds(20);
        config.updateApplicationHardTimeout = std::chrono::milliseconds(20);
        config.updateRangeDistribution = std::uniform_int_distribution<int>{0, 0};

        TestableUpdater updater(config);
        ensureConnectedUpdaterStart(updater);
        UNIT_ASSERT_EQUAL(updater.getTzOffset(), std::chrono::seconds(0));

        std::tm tm = {.tm_sec = 0, .tm_min = 30, .tm_hour = 3, .tm_mday = 14, .tm_mon = 3, .tm_year = 121};
        updater.currentTimestamp = std::chrono::system_clock::from_time_t(timegm(&tm));
        IOUpdater::Update update("Version", "download_url", "type", "urgency", 0xDE);
        update.urgency = "critical";
        UNIT_ASSERT(updater.shouldDownload(update));
        UNIT_ASSERT(updater.shouldApply(update));
        update.urgency = "regular";
        UNIT_ASSERT(updater.shouldDownload(update));
        UNIT_ASSERT(updater.shouldApply(update));

        config.updateRangeDistribution = std::uniform_int_distribution<int>{45 * 60, 45 * 60};
        TestableUpdater updaterWithOffset(config);
        updaterWithOffset.currentTimestamp = std::chrono::system_clock::from_time_t(timegm(&tm));
        ensureConnectedUpdaterStart(updaterWithOffset);
        UNIT_ASSERT_EQUAL(updaterWithOffset.getTzOffset(), std::chrono::seconds(0));
        update.urgency = "critical";
        UNIT_ASSERT(updaterWithOffset.shouldDownload(update));
        UNIT_ASSERT(updaterWithOffset.shouldApply(update));
        update.urgency = "regular";
        UNIT_ASSERT(!updaterWithOffset.shouldDownload(update));
        UNIT_ASSERT(!updaterWithOffset.shouldApply(update));

        // We should download and apply update even though the time is past our max limit of 4 am
        tm = {.tm_sec = 0, .tm_min = 30, .tm_hour = 4, .tm_mday = 14, .tm_mon = 3, .tm_year = 121};
        updaterWithOffset.currentTimestamp = std::chrono::system_clock::from_time_t(timegm(&tm));

        update.urgency = "critical";
        UNIT_ASSERT(updaterWithOffset.shouldDownload(update));
        UNIT_ASSERT(updaterWithOffset.shouldApply(update));
        update.urgency = "regular";
        UNIT_ASSERT(updaterWithOffset.shouldDownload(update));
        UNIT_ASSERT(updaterWithOffset.shouldApply(update));
    }

    Y_UNIT_TEST(testStateChanges) {
        std::unique_lock<std::mutex> lk(mutex_);

        auto config = defaultUpdaterConfig_;
        config.updateUrl = mockBackend_.address() + "/check_updates?";
        config.updateApplicationTimeout = std::chrono::milliseconds(20);
        config.updateApplicationHardTimeout = std::chrono::milliseconds(20);
        Updater updater(config);

        ensureConnectedUpdaterStart(updater);

        while (!IOUpdater::fileExists(config.downloadDir + "/update_" + updateVersion_ + ".zip_applied")) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        UNIT_ASSERT(!messages_.empty());

        auto message = std::find_if(messages_.begin(), messages_.end(), [](const IOUpdater::proto::UpdaterState& message) {
            return message.state() == IOUpdater::proto::UpdaterState_State_STARTING;
        });
        UNIT_ASSERT_EQUAL(message->state(), IOUpdater::proto::UpdaterState_State_STARTING);
        UNIT_ASSERT(!message->has_update());

        ++message;
        UNIT_ASSERT_EQUAL(message->state(), IOUpdater::proto::UpdaterState_State_CHECKING_UPDATE);
        UNIT_ASSERT(!message->has_update());

        ++message;
        UNIT_ASSERT_EQUAL(message->state(), IOUpdater::proto::UpdaterState_State_READY_TO_DOWNLOAD);
        UNIT_ASSERT(message->has_update());
        UNIT_ASSERT_EQUAL(message->update().firmware_version(), updateVersion_);
        UNIT_ASSERT_EQUAL(message->update().critical(), isCritical_.load());

        ++message;
        UNIT_ASSERT_EQUAL(message->state(), IOUpdater::proto::UpdaterState_State_DOWNLOADING);
        UNIT_ASSERT(message->has_update());
        UNIT_ASSERT_EQUAL(message->update().firmware_version(), updateVersion_);
        UNIT_ASSERT_EQUAL(message->update().critical(), isCritical_.load());
        UNIT_ASSERT_EQUAL(message->update().download_progress(), 0.0);

        ++message;
        UNIT_ASSERT_EQUAL(message->state(), IOUpdater::proto::UpdaterState_State_DOWNLOADING);
        UNIT_ASSERT(message->has_update());
        UNIT_ASSERT_EQUAL(message->update().firmware_version(), updateVersion_);
        UNIT_ASSERT_EQUAL(message->update().critical(), isCritical_.load());
        UNIT_ASSERT_EQUAL(message->update().download_progress(), 100.0);

        ++message;
        UNIT_ASSERT_EQUAL(message->state(), IOUpdater::proto::UpdaterState_State_DOWNLOADED);
        UNIT_ASSERT(message->has_update());
        UNIT_ASSERT_EQUAL(message->update().firmware_version(), updateVersion_);
        UNIT_ASSERT_EQUAL(message->update().critical(), isCritical_.load());

        ++message;
        UNIT_ASSERT_EQUAL(message->state(), IOUpdater::proto::UpdaterState_State_READY_TO_UPDATE);
        UNIT_ASSERT(message->has_update());
        UNIT_ASSERT_EQUAL(message->update().firmware_version(), updateVersion_);
        UNIT_ASSERT_EQUAL(message->update().critical(), isCritical_.load());

        ++message;
        UNIT_ASSERT_EQUAL(message->state(), IOUpdater::proto::UpdaterState_State_UPDATING);
        UNIT_ASSERT(message->has_update());
        UNIT_ASSERT_EQUAL(message->update().firmware_version(), updateVersion_);
        UNIT_ASSERT_EQUAL(message->update().critical(), isCritical_.load());

        ++message;
        UNIT_ASSERT_EQUAL(message->state(), IOUpdater::proto::UpdaterState_State_IDLE);
        UNIT_ASSERT(message->has_update());
        UNIT_ASSERT_EQUAL(message->update().firmware_version(), updateVersion_);
        UNIT_ASSERT_EQUAL(message->update().critical(), isCritical_.load());
    }

    Y_UNIT_TEST(testHttpCheckUpdateJitter) {
        auto requestTimes = std::make_shared<std::vector<std::chrono::steady_clock::time_point>>();
        std::condition_variable cv;
        std::unique_lock lk(mutex_);
        mockBackend_.addHandler("/check_updates", [this, requestTimes, &cv]() {
            {
                std::scoped_lock lk(mutex_);
                requestTimes->emplace_back(std::chrono::steady_clock::now());
                if (requestTimes->size() >= 3) {
                    cv.notify_all();
                }
            }
            Json::Value backendResponse;
            THttpResponse resp;
            resp.SetHttpCode(HTTP_SERVICE_UNAVAILABLE);
            return resp;
        });

        auto config = defaultUpdaterConfig_;
        config.updateUrl = mockBackend_.address() + "/check_updates";
        config.updateApplicationTimeout = std::chrono::milliseconds(20);
        config.updateApplicationHardTimeout = std::chrono::milliseconds(20);
        config.delayTimingsPolicy = BackoffWithJitterPolicy{std::chrono::milliseconds(5 * 1000), std::chrono::milliseconds(1 * 1000), std::chrono::milliseconds(600 * 1000)};

        TestableUpdater updater(config);
        ensureConnectedUpdaterStart(updater);
        cv.wait(lk, [requestTimes] { return requestTimes->size() >= 3; });
        const auto firstDelay = std::chrono::duration_cast<std::chrono::milliseconds>(requestTimes->at(1) - requestTimes->at(0));
        const auto secondDelay = std::chrono::duration_cast<std::chrono::milliseconds>(requestTimes->at(2) - requestTimes->at(1));

        UNIT_ASSERT_GE(firstDelay, std::chrono::milliseconds(1 * 1000));
        UNIT_ASSERT_GE(secondDelay, std::chrono::milliseconds(1 * 1000));
        // We would like to test for max delay values, but realistically this adds flaps if we're on a heavily loaded server
        // So we're just checking for sanity (no more than 30 seconds)
        UNIT_ASSERT_LE(firstDelay, std::chrono::milliseconds(30 * 1000));
        UNIT_ASSERT_LE(secondDelay, std::chrono::milliseconds(30 * 1000));
        UNIT_ASSERT_UNEQUAL(firstDelay, secondDelay); // This is a jitter check, there's a possibility (approx 1e6) that this check will fail for a
                                                      // working jitter, but breaking it is worse
    }

    Y_UNIT_TEST(testHttpCheckUpdateDelaySwitch) {
        auto requestTimes = std::make_shared<std::vector<std::chrono::steady_clock::time_point>>();
        std::condition_variable cv;
        std::unique_lock lk(mutex_);
        mockBackend_.addHandler("/check_updates", [this, requestTimes, &cv]() {
            {
                std::scoped_lock lk(mutex_);
                requestTimes->emplace_back(std::chrono::steady_clock::now());
                if (requestTimes->size() >= 3) {
                    cv.notify_all();
                }
            }

            THttpResponse resp;
            if (requestTimes->size() > 1) {
                Json::Value backendResponse;
                backendResponse["hasUpdate"] = true;
                backendResponse["critical"] = false;
                backendResponse["downloadUrl"] = std::string{mockBackend_.address() + "/download/ota.zip"};
                backendResponse["version"] = updateVersion_;
                backendResponse["crc32"] = IOUpdater::getCrc32(updateData_);

                resp.SetHttpCode(HTTP_OK);
                Json::FastWriter writer;
                const TString respStr{writer.write(backendResponse)};
                resp.SetContent(respStr, "application/json");
            } else {
                resp.SetHttpCode(HTTP_SERVICE_UNAVAILABLE);
            }
            return resp;
        });

        auto config = defaultUpdaterConfig_;
        config.updateUrl = mockBackend_.address() + "/check_updates?";
        config.updateApplicationTimeout = std::chrono::milliseconds(20);
        config.updateApplicationHardTimeout = std::chrono::milliseconds(20);
        config.delayTimingsPolicy = BackoffWithJitterPolicy{std::chrono::milliseconds(5 * 1000), std::chrono::milliseconds(1 * 1000), std::chrono::milliseconds(600 * 1000)};

        TestableUpdater updater(config);
        ensureConnectedUpdaterStart(updater);
        cv.wait(lk, [requestTimes] { return requestTimes->size() >= 3; });
        const auto firstDelay = requestTimes->at(1) - requestTimes->at(0);
        const auto secondDelay = requestTimes->at(2) - requestTimes->at(1);

        UNIT_ASSERT_GE(std::chrono::duration_cast<std::chrono::milliseconds>(firstDelay), std::chrono::milliseconds(1 * 1000));
        UNIT_ASSERT_GE(std::chrono::duration_cast<std::chrono::milliseconds>(secondDelay), std::chrono::milliseconds(5 * 1000));
        // We would like to test for max delay values, but realistically this adds flaps if we're on a heavily loaded server
        // So we're just checking for sanity (no more than 30 seconds)
        UNIT_ASSERT_LE(std::chrono::duration_cast<std::chrono::milliseconds>(firstDelay), std::chrono::milliseconds(30 * 1000));
        UNIT_ASSERT_LE(std::chrono::duration_cast<std::chrono::milliseconds>(secondDelay), std::chrono::milliseconds(30 * 1000));
    }

} /* suite end */
