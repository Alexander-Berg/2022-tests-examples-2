#pragma once

#include <memory>
#include <vector>

#include <userver/engine/condition_variable.hpp>
#include <userver/engine/deadline.hpp>

#include <defs/definitions/admin.hpp>
#include <scoring/execution/js/execution_info.hpp>

#include <admin/script_tests/environment.hpp>
#include <admin/script_tests/result.hpp>

namespace driver_scoring::admin::script_tests::execution::js {

class Context {
 public:
  Context(std::shared_ptr<Environment> env);

  Result GetResult(size_t test_idx);

 private:
  std::vector<FutureType> futures_;
  std::shared_ptr<scoring::execution::js::ExecutionInfo> execution_info_;
  engine::Deadline deadline_{};
};

}  // namespace driver_scoring::admin::script_tests::execution::js
