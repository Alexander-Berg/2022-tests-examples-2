#pragma once

#include <memory>

#include <js/execution/interface.hpp>

#include <admin/script_tests/environment.hpp>
#include <admin/script_tests/result.hpp>
#include <scoring/execution/js/execution_info.hpp>

#include "error_catcher.hpp"

namespace driver_scoring::admin::script_tests::execution::js {

class Task final : public ::js::execution::Task {
 public:
  static inline const std::string kName = "script-tests-task";

  Task(std::shared_ptr<Environment> env, std::vector<PromiseType>&& promises,
       std::shared_ptr<scoring::execution::js::ExecutionInfo> execution_info);

  const std::string* GetScript() const override;

  const std::string& GetName() const override { return kName; }

  v8::Local<v8::Value> Execute(
      const ::js::execution::AsyncPublicContext& async_context) const override;

  ::js::execution::ErrorProcessor* GetErrorProcessor() const override {
    return &error_catcher_;
  }

 private:
  std::shared_ptr<Environment> env_;
  mutable std::vector<PromiseType> promises_;
  std::shared_ptr<scoring::execution::js::ExecutionInfo> execution_info_;
  std::string script_;
  mutable ErrorCatcher error_catcher_{};
};

}  // namespace driver_scoring::admin::script_tests::execution::js
