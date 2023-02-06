#pragma once

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/components/loggable_component_base.hpp>
#include <userver/utils/periodic_task.hpp>

namespace dorblu::local_testing {

class PeriodicTaskSample : public components::LoggableComponentBase {
 public:
  static constexpr const char* kName = "periodic-task-sample";

  PeriodicTaskSample(const components::ComponentConfig& config,
                     const components::ComponentContext& context);
  ~PeriodicTaskSample();

 private:
  utils::PeriodicTask periodic_task_;
};

}  // namespace dorblu::local_testing
