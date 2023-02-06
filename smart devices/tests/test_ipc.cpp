#include <smart_devices/tools/updater/tests/lib/base_fixture.h>
#include <smart_devices/tools/updater/tests/lib/utils.h>
#include <smart_devices/tools/updater/ipc/ipc.h>
#include <smart_devices/tools/updater/ipc/ipc_client.h>

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/unittest/env.h>

#include <utility>

using namespace IOUpdater;

namespace {
    class Fixture: public BaseFixture {
    public:
        Fixture()
            : ipc_(socketPath_, serverMutex_, serverCv_)
            , ipcClient_(socketPath_, [this](IOUpdater::proto::UpdaterState msg) { pushMessage(std::move(msg)); })
                  {};

    protected:
        IPC ipc_;
        IPCClient ipcClient_;
        std::mutex serverMutex_;
        std::condition_variable serverCv_;
    };
} /* anonymous namespace */

Y_UNIT_TEST_SUITE_F(TestUpdaterIPC, Fixture) {
    Y_UNIT_TEST(testSendReceive) {
        // Wait until main() sends data
        std::unique_lock lk(messagesMutex_);
        IOUpdater::proto::UpdaterState state;
        state.set_state(IOUpdater::proto::UpdaterState::UPDATING);
        ipc_.send(state);
        messagesCv_.wait(lk, [this]() { return !messages_.empty(); });
        UNIT_ASSERT_EQUAL(messages_.size(), 1);
        UNIT_ASSERT_EQUAL(messages_[0].state(), IOUpdater::proto::UpdaterState_State_UPDATING);

        // Send commands to server
        {
            IOUpdater::proto::UpdaterCommand command;
            command.set_op(IOUpdater::proto::UpdaterCommand_Operation_set_idle);
            command.set_idle_state(true);
            std::unique_lock serverlk(serverMutex_);
            ipcClient_.send(command);
            serverCv_.wait(serverlk, [this]() { return ipc_.hasCommands(); });
        }
        auto commands = ipc_.popCommands();
        UNIT_ASSERT_EQUAL(commands.size(), 1);
        UNIT_ASSERT_EQUAL(commands[0].op(), IOUpdater::proto::UpdaterCommand_Operation_set_idle);
        UNIT_ASSERT_EQUAL(commands[0].idle_state(), true);

        {
            IOUpdater::proto::UpdaterCommand command;
            command.set_op(IOUpdater::proto::UpdaterCommand_Operation_set_tzoffset);
            command.set_timezone_offset_sec(25000);
            std::unique_lock serverlk(serverMutex_);
            ipcClient_.send(command);
            serverCv_.wait(serverlk, [this]() { return ipc_.hasCommands(); });
        }
        commands = ipc_.popCommands();
        UNIT_ASSERT_EQUAL(commands.size(), 1);
        UNIT_ASSERT_EQUAL(commands[0].op(), IOUpdater::proto::UpdaterCommand_Operation_set_tzoffset);
        UNIT_ASSERT_EQUAL(commands[0].timezone_offset_sec(), 25000);

        /*{
            std::unique_lock serverlk(serverMutex_);
            ipcClient_.send("hahaimhacking");
            serverCv_.wait_for(serverlk, std::chrono::seconds(5), [this]() { return ipc_.hasCommands(); });
        }
        UNIT_ASSERT(!ipc_.hasCommands());*/
    }
} /* suite end */
