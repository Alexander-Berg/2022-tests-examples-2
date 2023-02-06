#include "coro_fixture_plugin.hpp"

#include <userver/tracing/span.hpp>
#include <userver/utest/utest.hpp>

#include <atomic>
#include <chrono>
#include <exception>

namespace yaga::test {

void CoroutineFixturePlugin::CoroSetUp() {}

void CoroutineFixturePlugin::CoroTearDown() {
  for (auto& task : tasks_) {
    if (task.IsValid()) {
      task.RequestCancel();
    }
  }
  for (auto& task : tasks_) {
    try {
      task.WaitFor(utest::kMaxTestWaitTime);
    } catch (engine::WaitInterruptedException&) {
    } catch (std::exception& e) {
      FAIL() << e.what();
    }
  }
}

void CoroutineFixturePlugin::RunInCoro(std::function<void()> user_cb) {
  auto f = [this, user_cb = std::move(user_cb)]() {
    this->CoroSetUp();
    user_cb();
    this->CoroTearDown();
  };
  ::RunInCoro(std::move(f), kWorkerThreads);
}

}  // namespace yaga::test
