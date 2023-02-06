#include <js-pipeline/testing/context.hpp>

#include <userver/utils/assert.hpp>

#include <js-pipeline/compilation/conventions.hpp>
#include <js/execution/interface.hpp>

namespace js_pipeline::testing {

Context::Context(std::unique_ptr<const ResourceProvider> resources_provider,
                 execution::LoggerPtr logging_processor,
                 execution::PipelineBodyCPtr pipeline_body_ptr,
                 resource_management::Instances prefetched_resources,
                 formats::json::Value input, models::SchemaCPtr output_schema)
    : Base(*resources_provider, std::move(logging_processor),
           std::move(pipeline_body_ptr), std::move(prefetched_resources),
           /*resource_cache=*/nullptr, std::move(input),
           std::move(output_schema)),
      resources_provider_(std::move(resources_provider)) {
  UASSERT(resources_provider_);
}

v8::Local<v8::Value> Context::AsJsValue() const {
  auto context_js = Base::AsJsValue().As<v8::Object>();

  v8::Local context_v8 = js::GetCurrentContext();
  js::Set(context_v8, context_js, compilation::conventions::testing::kTestCase,
          js::New(resources_provider_->GetTestcaseName()));
  js::Set(context_v8, context_js, compilation::conventions::testing::kTest,
          js::New(resources_provider_->GetTestName()));
  auto resources_by_fields = js::NewObject();
  for (const auto& [field, resource_name] :
       pipeline_body->resource_name_by_field) {
    js::Set(context_v8, resources_by_fields, field, resource_name);
  }
  js::Set(context_v8, context_js,
          compilation::conventions::testing::kResourceNameByField,
          resources_by_fields);
  return context_js;
}

}  // namespace js_pipeline::testing
