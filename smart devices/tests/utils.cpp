#include <smart_devices/tools/updater_gateway/tests/utils.h>

#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>
#include <util/random/entropy.h>
#include <util/random/mersenne.h>

#include <memory>
#include <utility>

using namespace quasar;
using namespace IOUpdater;
using namespace YandexIO;

namespace IOUpdater {
    TestableUpdater::TestableUpdater(const IOUpdater::UpdaterConfig& config)
        : Updater(config)
        , currentTimestamp(std::chrono::system_clock::time_point())
    {
    }

    std::chrono::system_clock::time_point TestableUpdater::getCurrentTime() const {
        return currentTimestamp.load();
    }

    void TestableUpdater::waitUntilTimezoneReceived(int offsetSec) const {
        // YIO_LOG_INFO("Waiting for tzoffset to equate to " << offsetSec);
        while (tzOffset_ != std::chrono::seconds(offsetSec)) {
            std::this_thread::sleep_for(std::chrono::nanoseconds(20));
        }
    }

    std::string getSocketPath(const std::string& socketName) {
        TMersenne<ui64> rng(Seed());
        constexpr int maxUnixPathLen = sizeof(((sockaddr_un*)nullptr)->sun_path);
        std::string result = GetRamDrivePath();
        if (result.empty() || result.length() + socketName.length() > maxUnixPathLen) {
            result = GetWorkPath();
            if (result.length() + socketName.length() > maxUnixPathLen) {
                // See https://st.yandex-team.ru/DEVTOOLSSUPPORT-5680
                result = "/tmp/" + std::to_string(rng.GenRand64()) + "/";
                Mkdir(result.c_str(), MODE0777);
            }
        }
        return result + socketName;
    }

    TestableUpdaterGateway::TestableUpdaterGateway(std::shared_ptr<YandexIO::IDevice> device, std::shared_ptr<quasar::ipc::IIpcFactory> ipcFactory,
                                                   std::string ipcSocketPath)
        : UpdaterGateway(std::move(device), std::move(ipcFactory), ipcSocketPath)
    {
    }

    void TestableUpdaterGateway::waitUntilUpdaterIPCConnected() const {
        // YIO_LOG_INFO("Waiting for IPC to become connected");
        while (!updaterIPCClient_.isConnected()) {
            std::this_thread::sleep_for(std::chrono::nanoseconds(20));
        }
    }

    void IOHubWrapper::setAllowUpdate(bool allowUpdateAll, bool allowCritical) {
        quasar::proto::QuasarMessage message;
        message.mutable_io_control()->mutable_allow_update()->set_for_all(allowUpdateAll);
        message.mutable_io_control()->mutable_allow_update()->set_for_critical(allowCritical);
        server_->sendToAll(std::move(message));
    }

    void IOHubWrapper::setTimezone(const Timezone& timezone) {
        server_->sendToAll(ipc::buildMessage([&timezone](auto& msg) {
            msg.mutable_io_control()->mutable_timezone()->CopyFrom(timezone.toProto());
        }));
    }

    void IOHubWrapper::waitConnection() {
        server_->waitConnectionsAtLeast(1);
    }
} // namespace IOUpdater
