#pragma once

#include <chrono>

#include <admin/script_tests/environment.hpp>
#include <admin/script_tests/result.hpp>
#include <defs/definitions/admin.hpp>

#include "admin/script_tests/environment.hpp"
#include "error_catcher.hpp"

namespace driver_scoring::admin::script_tests::execution::js {

class TestRunner {
 public:
  TestRunner(std::shared_ptr<Environment> env, ErrorCatcher& error_catcher);

  Result Run(const ::handlers::ScriptTest& test);

 private:
  const ::handlers::ScriptType script_type_;
  engine::TaskProcessor& timer_task_processor_;
  std::chrono::milliseconds timeout_;
  ErrorCatcher& error_catcher_;
};

}  // namespace driver_scoring::admin::script_tests::execution::js
