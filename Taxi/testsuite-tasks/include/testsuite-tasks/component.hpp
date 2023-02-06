#pragma once

#include <string>

#include <userver/components/loggable_component_base.hpp>
#include <userver/testsuite/tasks.hpp>
#include <userver/utils/async.hpp>

namespace testsuite_tasks {

using testsuite::TaskAlreadyRunning;
using testsuite::TaskNotFound;

class TestsuiteTasksComponent final
    : public ::components::LoggableComponentBase {
 public:
  static constexpr auto kName = "testsuite-tasks";

  TestsuiteTasksComponent(const ::components::ComponentConfig& config,
                          const ::components::ComponentContext& context)
      : ::components::LoggableComponentBase(config, context),
        testsuite_tasks_(testsuite::GetTestsuiteTasks(context)) {}

  bool IsEnabled() const { return testsuite_tasks_.IsEnabled(); }

  void RegisterTask(const std::string& name,
                    testsuite::TestsuiteTasks::TaskCallback callback) {
    return testsuite_tasks_.RegisterTask(name, callback);
  }
  void UnregisterTask(const std::string& name) {
    testsuite_tasks_.UnregisterTask(name);
  }

 private:
  testsuite::TestsuiteTasks& testsuite_tasks_;
};

}  // namespace testsuite_tasks
