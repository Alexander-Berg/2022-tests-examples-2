#include <smart_devices/tools/updater/tests/lib/base_fixture.h>
#include <smart_devices/tools/updater/tests/lib/utils.h>
#include <smart_devices/tools/updater/lib/updater.h>
#include <smart_devices/tools/updater/ipc/ipc_client.h>

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/unittest/env.h>
#include <util/random/entropy.h>
#include <util/random/mersenne.h>

#include <utility>

using namespace IOUpdater;

namespace {
    class Fixture: public BaseFixture {
    public:
        Fixture()
            : ipcClient_(socketPath_, [this](IOUpdater::proto::UpdaterState msg) { pushMessage(std::move(msg)); })
                  {};

    protected:
        IPCClient ipcClient_;

    public:
        void ensureConnectedUpdaterStart(IOUpdater::Updater& updater) {
            updater.startIpc();
            while (!ipcClient_.isConnected()) {
                std::this_thread::sleep_for(std::chrono::milliseconds(20));
            }
            updater.startUpdateLoop();
        }

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
    };
} /* anonymous namespace */

Y_UNIT_TEST_SUITE_F(TestUpdaterIPC, Fixture) {
    Y_UNIT_TEST(testSetTzoffset) {
        IOUpdater::Updater updater(defaultUpdaterConfig_);
        ensureConnectedUpdaterStart(updater);
        UNIT_ASSERT_EQUAL(updater.getTzOffset(), std::chrono::seconds(0));
        constexpr int timezoneOffsetSec = 60 * 60 * 12;
        IOUpdater::proto::UpdaterCommand command;
        command.set_op(IOUpdater::proto::UpdaterCommand_Operation_set_tzoffset);
        command.set_timezone_offset_sec(timezoneOffsetSec);
        sendWithAck(command, [&]() { return updater.getTzOffset() == std::chrono::seconds(0); });
        UNIT_ASSERT_EQUAL(updater.getTzOffset(), std::chrono::seconds(timezoneOffsetSec));

        command.set_timezone_offset_sec(-timezoneOffsetSec);
        sendWithAck(command, [&]() { return updater.getTzOffset() == std::chrono::seconds(timezoneOffsetSec); });
        UNIT_ASSERT_EQUAL(updater.getTzOffset(), std::chrono::seconds(-timezoneOffsetSec));
    }

    Y_UNIT_TEST(testSetDeviceIdle) {
        IOUpdater::Updater updater(defaultUpdaterConfig_);
        ensureConnectedUpdaterStart(updater);
        UNIT_ASSERT_EQUAL(updater.getDeviceIdle(), false);
        IOUpdater::proto::UpdaterCommand command;
        command.set_op(IOUpdater::proto::UpdaterCommand_Operation_set_idle);
        command.set_idle_state(true);
        sendWithAck(command, [&]() { return !updater.getDeviceIdle(); });
        UNIT_ASSERT_EQUAL(updater.getDeviceIdle(), true);

        command.set_idle_state(false);
        sendWithAck(command, [&]() { return updater.getDeviceIdle(); });
        UNIT_ASSERT_EQUAL(updater.getDeviceIdle(), false);
    }

} /* suite end */
