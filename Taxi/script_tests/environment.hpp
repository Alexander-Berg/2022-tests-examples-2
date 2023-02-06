#pragma once

#include <chrono>
#include <defs/definitions/admin.hpp>
#include <handlers/dependencies_fwd.hpp>
#include <js/execution/component.hpp>
#include <userver/dynamic_config/snapshot.hpp>

namespace driver_scoring::admin::script_tests {

struct Environment {
  const ::handlers::ScriptCommitRequest request;
  ::js::execution::Component& js_component;
  std::chrono::milliseconds timeout;
  std::chrono::milliseconds single_test_timeout;
  ::engine::TaskProcessor& timer_task_processor;

  explicit Environment(::handlers::ScriptCommitRequest&& request,
                       handlers::Dependencies&& dependencies);
};

}  // namespace driver_scoring::admin::script_tests
