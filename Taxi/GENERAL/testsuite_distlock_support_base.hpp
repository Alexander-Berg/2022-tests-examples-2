#pragma once

#include <userver/storages/postgres/dist_lock_component_base.hpp>

#include <testsuite-tasks/component.hpp>

namespace driver_status::workers {

class TestsuiteDistlockSupportBase
    : public storages::postgres::DistLockComponentBase {
 public:
  TestsuiteDistlockSupportBase(const components::ComponentConfig& config,
                               const components::ComponentContext& context,
                               const std::string& name);

  const std::string& Name() const;

 protected:
  // to be called in last child ctor only
  void StartWorker();
  // to be called in last child dtor only
  void StopWorker();

 private:
  testsuite_tasks::TestsuiteTasksComponent& testsuite_tasks_;
  const std::string name_;
};

}  // namespace driver_status::workers
