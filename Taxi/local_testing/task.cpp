#include "task.hpp"

#include "connection/agent_connection.hpp"
#include "dorblu.pb.h"

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/logging/log.hpp>
#include <userver/testsuite/testpoint.hpp>
#include <userver/testsuite/testsuite_support.hpp>
#include <userver/utils/periodic_task.hpp>

namespace dorblu::local_testing {

PeriodicTaskSample::PeriodicTaskSample(
    const components::ComponentConfig& config,
    const components::ComponentContext& context)
    : LoggableComponentBase(config, context) {
  utils::PeriodicTask::Settings task_settings{
      std::chrono::milliseconds{1000},
      5,
      {utils::PeriodicTask::Flags::kChaotic, utils::PeriodicTask::Flags::kNow}};
  periodic_task_.RegisterInTestsuite(
      context.FindComponent<::components::TestsuiteSupport>()
          .GetPeriodicTaskControl());
  periodic_task_.Start("periodic-task-sample", task_settings, [] {
    LOG_INFO() << "Periodic task started: periodic-task-sample " << kName;
    dorblu::connection::AgentNetworkConnection conn("localhost", 3033,
                                                    std::chrono::seconds(2), 1);
    auto msg = DorBluPB::MainMessage();
    msg.set_group_name("TestService");
    msg.set_version(1);
    msg.set_seconds(30);
    conn.Write(msg);
    TESTPOINT("task::periodic-task-sample", formats::json::Value{});
    auto response = DorBluPB::MainMessage();
    auto result = conn.Read(&response);
    LOG_INFO() << "[Received result] " << result;
    if (result) {
      LOG_INFO() << "[Message] " << response.DebugString();
    }
  });
}

PeriodicTaskSample::~PeriodicTaskSample() { periodic_task_.Stop(); }

}  // namespace dorblu::local_testing
