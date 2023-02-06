#pragma once

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/source.hpp>
#include <userver/dynamic_config/storage/component.hpp>
#include <userver/engine/task/task_with_result.hpp>
#include <userver/utils/statistics/storage.hpp>

#include <js/execution/component.hpp>

#include <js-pipeline/models/handles.hpp>
#include <js-pipeline/models/pipeline_testing.hpp>
#include <js-pipeline/resource_management/component.hpp>
#include <js-pipeline/types.hpp>

#include <taxi_config/js-pipeline/taxi_config.hpp>

namespace js_pipeline::compilation {
class Component;
struct CompiledPipeline;
}  // namespace js_pipeline::compilation

namespace js_pipeline::testing {

class Component : public components::LoggableComponentBase {
 public:
  static constexpr auto kName = "js-pipeline-testing";

  Component(const components::ComponentConfig&,
            const components::ComponentContext&);
  ~Component();

  template <typename ConsumerTag>
  models::PipelineTestsResults PerformTests(
      models::PipelineTestRequest&& test_request) const {
    return PerformTests(std::move(test_request), ConsumerTag::kName);
  }

  models::PipelineTestsResults PerformTests(
      models::PipelineTestRequest&& test_request,
      const std::string& consumer_name) const;

 private:
  models::PipelineTestResult PerformTest(
      const compilation::CompiledPipeline& pipeline,
      const models::PipelineTestRequest& test_request,
      const models::PipelineTest& test, const std::string& consumer_name) const;

  const js::execution::Component& js_;
  const compilation::Component& compilation_component_;
  const resource_management::Component& resources_;
  const dynamic_config::Source taxi_config_component_;
};

}  // namespace js_pipeline::testing
