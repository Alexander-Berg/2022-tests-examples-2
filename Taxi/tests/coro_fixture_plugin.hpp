#pragma once

#include <userver/utils/async.hpp>

#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace yaga::test {

/// Inheriting and properly initializing this fixture plugin allows
/// user to do initialization and tear down, launch task in RunInCoro.
///
/// Override CoroSetUp() to do initialization in coroutine environment.
/// Override CoroTearDown() to do tear down in coroutine environment (do not
/// forget to call CoroutineFixturePlugin::CoroTearDown() from the override).
class CoroutineFixturePlugin {
 protected:
  /// Launches task asynchronously using this plugin's task processor.
  /// You can use this method to launch some tasks from your fixture
  /// CoroSetUp/CoroTearDown methods.
  /// You will have to cancel this task manually in CoroTearDown though
  template <typename Function, typename... Args>
  auto Async(const std::string& name, Function&& f, Args&&... args) {
    return utils::Async(name, std::forward<Function>(f),
                        std::forward<Args>(args)...);
  };

  /// Launches task asynchronously and manages it automatically. All tasks
  /// launched this way will be cancelled in
  /// CoroutineFixturePlugin::CoroTearDown stage.
  template <typename Function, typename... Args>
  void AsyncForget(const std::string& name, Function&& f, Args&&... args) {
    tasks_.emplace_back(utils::Async(name, std::forward<Function>(f),
                                     std::forward<Args>(args)...));
  };

  /// Launches given function on this task's task processor. This method
  /// returns only when ALL asynchronous tasks launched inside are finished!
  void RunInCoro(std::function<void()> user_cb);

 protected:
  ~CoroutineFixturePlugin() = default;
  virtual void CoroSetUp();
  virtual void CoroTearDown();

  static void PluginSetUpTestSuite() {}
  static void PluginTearDownTestSuite() {}

 private:
  std::vector<engine::Task> tasks_;
  static constexpr const size_t kWorkerThreads = 4;
};

}  // namespace yaga::test
