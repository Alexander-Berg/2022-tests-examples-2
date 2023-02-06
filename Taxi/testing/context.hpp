#pragma once

#include <js-pipeline/execution/task.hpp>

#include "resource_provider.hpp"

namespace js_pipeline::testing {

struct Context : public execution::Context {
  Context(std::unique_ptr<const ResourceProvider> resources_provider,
          execution::LoggerPtr logging_processor,
          execution::PipelineBodyCPtr pipeline_body_ptr,
          resource_management::Instances prefetched_resources,
          formats::json::Value input, models::SchemaCPtr output_schema);

  v8::Local<v8::Value> AsJsValue() const override;

 private:
  using Base = execution::Context;
  std::unique_ptr<const ResourceProvider> resources_provider_;
};

using ContextPtr = std::shared_ptr<Context>;

}  // namespace js_pipeline::testing
