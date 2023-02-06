#include <smart_devices/tools/updater/tests/lib/base_fixture.h>
#include <smart_devices/tools/updater/tests/lib/http_server.h>
#include <smart_devices/tools/updater/tests/lib/utils.h>
#include <smart_devices/tools/updater/ipc/ipc_client.h>
#include <smart_devices/tools/updater/lib/updater.h>
#include <smart_devices/tools/updater/lib/utils.h>

#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/tests_data.h>

#include <fstream>
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

Y_UNIT_TEST_SUITE_F(TestUpdateDownloading, Fixture) {
    Y_UNIT_TEST(testNoRedownloading) {
        mockBackend_.addHandler("/download/ota.zip", [] {
            THttpResponse resp;
            resp.SetHttpCode(HTTP_REQUESTED_RANGE_NOT_SATISFIABLE);
            return resp;
        });

        {
            std::ofstream f(defaultUpdaterConfig_.downloadDir + "/update_" + updateVersion_ + ".zip");
            f << updateData_;
        }

        auto config = defaultUpdaterConfig_;
        config.updateUrl = mockBackend_.address() + "/check_updates?";
        config.updateApplicationTimeout = std::chrono::milliseconds(20);
        config.updateApplicationHardTimeout = std::chrono::milliseconds(20);
        Updater updater(config);

        ensureConnectedUpdaterStart(updater);

        while (!IOUpdater::fileExists(config.downloadDir + "/update_" + updateVersion_ + ".zip_applied")) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        std::ifstream in(config.downloadDir + "/update_" + updateVersion_ + ".zip", std::ios::binary);
        std::ostringstream contents;
        contents << in.rdbuf();
        UNIT_ASSERT_EQUAL(contents.str(), updateData_);

        auto message = std::find_if(messages_.begin(), messages_.end(), [](const IOUpdater::proto::UpdaterState& message) {
            return message.state() == IOUpdater::proto::UpdaterState_State_UPDATING;
        });

        UNIT_ASSERT_UNEQUAL(message, messages_.end());
        UNIT_ASSERT(message->has_update());
        UNIT_ASSERT_EQUAL(message->update().firmware_version(), updateVersion_);
        UNIT_ASSERT_EQUAL(message->update().critical(), isCritical_.load());
    }

    Y_UNIT_TEST(testRedownloadOnCrc32Mismatch) {
        {
            std::ofstream f(defaultUpdaterConfig_.downloadDir + "/update_" + updateVersion_ + ".zip");
            f << updateData_;
            f << "hax0r_script";
        }

        auto config = defaultUpdaterConfig_;
        config.updateUrl = mockBackend_.address() + "/check_updates?";
        config.updateApplicationTimeout = std::chrono::milliseconds(20);
        config.updateApplicationHardTimeout = std::chrono::milliseconds(20);
        Updater updater(config);

        ensureConnectedUpdaterStart(updater);

        while (!IOUpdater::fileExists(config.downloadDir + "/update_" + updateVersion_ + ".zip_applied")) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        std::ifstream in(config.downloadDir + "/update_" + updateVersion_ + ".zip", std::ios::binary);
        std::ostringstream contents;
        contents << in.rdbuf();
        UNIT_ASSERT_EQUAL(contents.str(), updateData_);

        auto message = std::find_if(messages_.begin(), messages_.end(), [](const IOUpdater::proto::UpdaterState& message) {
            return message.state() == IOUpdater::proto::UpdaterState_State_UPDATING;
        });

        UNIT_ASSERT_UNEQUAL(message, messages_.end());
        UNIT_ASSERT(message->has_update());
        UNIT_ASSERT_EQUAL(message->update().firmware_version(), updateVersion_);
        UNIT_ASSERT_EQUAL(message->update().critical(), isCritical_.load());
    }
}
