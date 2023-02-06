#pragma once

#include <smart_devices/tools/updater/lib/updater.h>
#include <smart_devices/tools/updater_gateway/updater_gateway.h>
#include <yandex_io/libs/ipc/i_connector.h>
#include <yandex_io/libs/ipc/i_server.h>
#include <yandex_io/modules/geolocation/interfaces/timezone.h>
#include <yandex_io/tests/testlib/unittest_helper/unit_test_fixture.h>

#include <string>

namespace IOUpdater {
    class TestableUpdater: public IOUpdater::Updater {
    public:
        explicit TestableUpdater(const IOUpdater::UpdaterConfig& config);
        std::chrono::system_clock::time_point getCurrentTime() const override;
        void waitUntilTimezoneReceived(int offsetSec) const;

        std::atomic<std::chrono::system_clock::time_point> currentTimestamp;
    };

    class TestableUpdaterGateway: public quasar::UpdaterGateway {
    public:
        TestableUpdaterGateway(std::shared_ptr<YandexIO::IDevice> device, std::shared_ptr<quasar::ipc::IIpcFactory> ipcFactory,
                               std::string ipcSocketPath);
        void waitUntilUpdaterIPCConnected() const;
    };

    std::string getSocketPath(const std::string& socketName);

    class IOHubWrapper {
    public:
        IOHubWrapper(std::shared_ptr<quasar::ipc::IIpcFactory> ipcFactory)
            : server_(ipcFactory->createIpcServer("iohub_services"))
        {
            server_->listenService();
        };
        void setAllowUpdate(bool allowUpdateAll, bool allowCritical);
        void setTimezone(const YandexIO::Timezone& timezone);
        void waitConnection();

    private:
        std::shared_ptr<quasar::ipc::IServer> server_;
    };

} // namespace IOUpdater
