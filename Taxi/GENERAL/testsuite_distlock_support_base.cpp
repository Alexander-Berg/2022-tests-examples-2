#include "testsuite_distlock_support_base.hpp"

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>

namespace driver_status::workers {

TestsuiteDistlockSupportBase::TestsuiteDistlockSupportBase(
    const components::ComponentConfig& config,
    const components::ComponentContext& context, const std::string& name)
    : storages::postgres::DistLockComponentBase(config, context),
      testsuite_tasks_(
          context.FindComponent<testsuite_tasks::TestsuiteTasksComponent>()),
      name_(name) {}

const std::string& TestsuiteDistlockSupportBase::Name() const { return name_; }

void TestsuiteDistlockSupportBase::StartWorker() {
  if (testsuite_tasks_.IsEnabled()) {
    testsuite_tasks_.RegisterTask(name_ + ".testsuite", [this] { DoWork(); });
  } else {
    AutostartDistLock();
  }
}

void TestsuiteDistlockSupportBase::StopWorker() { StopDistLock(); }

}  // namespace driver_status::workers
