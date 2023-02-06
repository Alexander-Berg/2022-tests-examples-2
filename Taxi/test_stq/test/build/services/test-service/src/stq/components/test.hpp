#pragma once

#include <userver/components/loggable_component_base.hpp>
#include <userver/formats/bson.hpp>

#include <handlers/dependencies_fwd.hpp>
#include <stq-dispatcher/components/stq_task_base.hpp>
#include <stq-dispatcher/models/task.hpp>
#include <stq/models/test.hpp>

namespace stq_tasks {
namespace test {

class InvalidArgumentsError: public std::runtime_error {
  using runtime_error::runtime_error;
};

class Test final: public stq_dispatcher::components::StqTaskBase {
 public:
  Test(const components::ComponentConfig& config,
       const components::ComponentContext& context);
  ~Test();
  static constexpr const char* kName = "stq-test";
  bool ParseArgsAsJson() const override;
  void Perform(
      const stq_dispatcher::models::VariantTaskData& task) const override;

 private:
  std::unique_ptr<handlers::DependenciesFactory> deps_factory_;
  Args ParseArgs(const formats::json::Value& args,
                 const formats::json::Value& kwargs) const;
};

}  // namespace test
}  // namespace stq_tasks
