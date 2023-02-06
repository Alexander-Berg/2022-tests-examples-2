#include "base_fixture.h"

#include "utils.h"

#include <smart_devices/tools/updater/logging/utils.h>

#include <library/cpp/testing/unittest/env.h>
#include <util/random/entropy.h>

IOUpdater::BaseFixture::BaseFixture()
    : rng_(Seed())
    , socketPath_(getSocketPath("/u.sock"))
    , testWorkDir_(getUniqueTestWorkdir())
    , deviceId_(std::to_string(rng_.GenRand64()))
    , defaultUpdaterConfig_{
          .ipcSocketPath = socketPath_,
          .workDir = testWorkDir_,
          .downloadDir = testWorkDir_,
          .deviceId = deviceId_,
          .updateRangeDistribution = std::uniform_int_distribution<int>{0, 0}}
{
    initLogging(spdlog::level::trace);
}

IOUpdater::BaseFixture::~BaseFixture() {
    deinitLogging();
}

void IOUpdater::BaseFixture::pushMessage(IOUpdater::proto::UpdaterState message) {
    UPDATER_LOG_INFO("Message: {}", shortUtf8DebugString(message));
    std::unique_lock lk(messagesMutex_);
    messages_.push_back(std::move(message));
    messagesCv_.notify_all();
};
