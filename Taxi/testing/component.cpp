#include <js-pipeline/testing/component.hpp>

#include <clients/codegen/exception.hpp>

#include <fmt/format.h>
#include <boost/algorithm/string/join.hpp>

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/storage/component.hpp>
#include <userver/utils/algo.hpp>
#include <userver/utils/assert.hpp>

#include <js-pipeline/compilation/component.hpp>
#include <js-pipeline/execution/json_value/history/view.hpp>
#include <js-pipeline/execution/native/stage.hpp>
#include <js-pipeline/fetching/schema/registry.hpp>
#include <js-pipeline/resource_management/request.hpp>
#include <js-pipeline/utils.hpp>

#include "task.hpp"

namespace js_pipeline::testing {

namespace {
const std::chrono::seconds kCacheMaxUnusedTime{5};

using handlers::libraries::js_pipeline::OpaqueObject;
using handlers::libraries::js_pipeline::PipelineTestCaseResult;
using js_pipeline::models::PipelineTestResult;

class TestError : public std::runtime_error {
 public:
  using std::runtime_error::runtime_error;
};

ResourceMetadataMap MakeNonBlocking(ResourceMetadataMap metadata_map) {
  for (auto& [key, metadata] : metadata_map) {
    metadata.is_blocking_fetch = false;
  }
  return metadata_map;
}

const formats::json::Value& GetInputMock(
    const models::PipelineTestRequest& test_request,
    const models::PipelineTest& test, const std::string& mock_id) {
  if (test.input_mocks) {
    if (const auto* input_mock =
            utils::FindOrNullptr(test.input_mocks->extra, mock_id)) {
      return input_mock->extra;
    }
  }
  if (const auto* input_mock =
          utils::FindOrNullptr(test_request.input_mocks.extra, mock_id)) {
    return input_mock->extra;
  }
  throw TestError(fmt::format("Input mock {} not found", mock_id));
}

const formats::json::Value& GetPrefetchedResourceMock(
    const models::PipelineTestRequest& test_request,
    const models::PipelineTest& test, const std::string& resource,
    const std::string& mock_id) {
  if (test.prefetched_resources_mocks) {
    if (const auto* resource_mocks = utils::FindOrNullptr(
            test.prefetched_resources_mocks->extra, resource)) {
      if (const auto* body =
              utils::FindOrNullptr(resource_mocks->extra, mock_id)) {
        return body->extra;
      }
    }
  }
  if (const auto* resource_mocks = utils::FindOrNullptr(
          test_request.prefetched_resources_mocks.extra, resource)) {
    if (const auto* body =
            utils::FindOrNullptr(resource_mocks->extra, mock_id)) {
      return body->extra;
    }
  }
  throw TestError(
      fmt::format("Prefetched resource mock {} not found", mock_id));
}

}  // namespace

Component::Component(const components::ComponentConfig& config,
                     const components::ComponentContext& context)
    : LoggableComponentBase(config, context),
      js_(context.FindComponent<js::execution::Component>()),
      compilation_component_(context.FindComponent<compilation::Component>()),
      resources_(context.FindComponent<resource_management::Component>()),
      taxi_config_component_(
          context.FindComponent<components::DynamicConfig>().GetSource()) {}

Component::~Component() {}

js_pipeline::models::PipelineTestsResults Component::PerformTests(
    js_pipeline::models::PipelineTestRequest&& test_request,
    const std::string& consumer_name) const {
  js_pipeline::models::PipelineTestsResults result{
      /*created=*/utils::datetime::Now(),
      /*tests=*/{},
  };
  auto compiled_pipeline = compilation_component_.CompilePipelineTests(
      test_request.pipeline,
      MakeNonBlocking(resources_.GetResourcesMetadata(consumer_name)),
      test_request);
  for (const auto& test : test_request.tests) {
    result.tests.push_back(
        PerformTest(compiled_pipeline, test_request, test, consumer_name));
  }
  return result;
}

PipelineTestResult Component::PerformTest(
    const compilation::CompiledPipeline& pipeline,
    const models::PipelineTestRequest& test_request,
    const models::PipelineTest& test, const std::string& consumer_name) const {
  auto& consumer_registry = fetching::schema::Registry::Get(consumer_name);
  PipelineTestResult result;
  result.name = test.name;

  auto snapshot = taxi_config_component_.GetSnapshot();
  auto taxi_config = snapshot.Get<taxi_config::js_pipeline::TaxiConfig>();
  auto timeout_ms = taxi_config.js_pipeline_tests_timeout;

  for (const auto& testcase : test.testcases) {
    const auto& input = GetInputMock(test_request, test, testcase.input_mock);
    PipelineTestCaseResult testcase_result;
    testcase_result.name = testcase.name;
    const auto& requested_prefetch = consumer_registry.GetPrefetchedResources();
    resource_management::Instances prefetched_resources;
    std::vector<std::string> absent_prefetched_resources;
    for (const auto& requested : requested_prefetch) {
      auto* mock_id = utils::FindOrNullptr(testcase.prefetched_resources.extra,
                                           requested.name);
      if (!mock_id) {
        absent_prefetched_resources.push_back(requested.name);
        continue;
      }
      prefetched_resources[requested.field] =
          std::make_shared<js::wrappers::JsonLoadJsWrapper>(
              GetPrefetchedResourceMock(test_request, test, requested.name,
                                        *mock_id));
    }
    if (!absent_prefetched_resources.empty()) {
      testcase_result.passed = false;
      testcase_result.error_message = fmt::format(
          "No mock for prefetched resources [{}] in testcase {}",
          boost::join(absent_prefetched_resources, ","), testcase.name);
      result.testcases.push_back(std::move(testcase_result));
      break;
    }

    auto pipeline_body_ptr =
        std::make_shared<compilation::CompiledPipeline::Body>(
            pipeline.GetBody());

    UASSERT_MSG(!pipeline_body_ptr->pre_js_native_section &&
                    !pipeline_body_ptr->post_js_native_section,
                "pre and post-JS native sections shouldn't occur at testing"
                "(should've been ensured at pipeline::Compile)");

    ContextPtr context = std::make_shared<Context>(
        /*resources_provider=*/std::make_unique<testing::ResourceProvider>(
            /*test_name=*/test.name,
            /*testcase_name=*/testcase.name),
        /*logging_processor=*/
        std::make_unique<execution::JsonLogger>(
            pipeline.id, pipeline.name, execution::ResourcesLoggingMode::kNone),
        /*pipeline_body_ptr=*/pipeline_body_ptr,
        /*prefetched_resources=*/std::move(prefetched_resources),
        /*input=*/input,
        /*output_schema=*/consumer_registry.GetOutputSchema());

    try {
      js::execution::TaskPtr task = std::make_unique<Task>(
          context, kCacheMaxUnusedTime, test.name, testcase.name);

      auto channel = js_.Execute<Task::OutputOpt>(std::move(task));

      std::optional<Task::FinalOutput> task_output;

      for (auto output : channel.Iterate(timeout_ms)) {
        if (output) {
          if (channel.IsDone()) {
            task_output = Get<Task::FinalOutput>(*output);
          } else {
            UINVARIANT(false, "unexpected blocking fetch resources request");
          }
        }
      }

      UINVARIANT(task_output, "no task return value");
      testcase_result.passed = true;
      testcase_result.failed_stage_names = task_output->GetFailedStageNames();

    } catch (const std::exception& error) {
      testcase_result.passed = false;
      testcase_result.error_message = error.what();
    }
    if (auto* json_logger = dynamic_cast<execution::JsonLogger*>(
            context->logging_processor.get())) {
      testcase_result.logs.emplace(OpaqueObject{
          context->output.AsHistorical().ToDetailedJson(*json_logger)});
    }
    result.testcases.push_back(std::move(testcase_result));
  }
  return result;
}

}  // namespace js_pipeline::testing
