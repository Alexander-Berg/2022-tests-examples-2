#pragma once

#include <smart_devices/tools/updater/ipc/proto/updater_state.pb.h>
#include <smart_devices/tools/updater/lib/updater_config.h>
#include <library/cpp/testing/unittest/registar.h>
#include <util/random/mersenne.h>

#include <mutex>
#include <condition_variable>

namespace IOUpdater {
    class BaseFixture: public NUnitTest::TBaseFixture {
    public:
        BaseFixture();
        virtual ~BaseFixture();
        void pushMessage(proto::UpdaterState message);

        TMersenne<ui64> rng_;
        std::string socketPath_;
        std::string testWorkDir_;
        std::string deviceId_;
        std::vector<IOUpdater::proto::UpdaterState> messages_;
        const IOUpdater::UpdaterConfig defaultUpdaterConfig_;

        std::mutex messagesMutex_;
        std::condition_variable messagesCv_;
    };
} // namespace IOUpdater
