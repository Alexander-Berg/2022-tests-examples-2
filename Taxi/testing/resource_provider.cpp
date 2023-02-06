#include "resource_provider.hpp"

#include <userver/formats/parse/common_containers.hpp>

#include <js-pipeline/compilation/conventions.hpp>

namespace js_pipeline::testing {

ResourceProvider::ResourceProvider(std::string test_name,
                                   std::string testcase_name)
    : test_name_(std::move(test_name)),
      testcase_name_(std::move(testcase_name)) {}

resource_management::Instances ResourceProvider::GetData(
    const resource_management::ResourceRequestByField& request,
    resource_management::Cache*) const {
  formats::json::ValueBuilder requests_json;

  for (const auto& [field_name, args] : request) {
    formats::json::ValueBuilder request_json;

    request_json["name"] = args.name;
    request_json["args"] = args.args;

    requests_json[field_name] = std::move(request_json);
  }

  return js::TypeCast<formats::json::Value>(
             js::CallGlobal(
                 js::FromContext<v8::Function>(
                     compilation::conventions::testing::kGetMockedResources),
                 /*__resources_request__=*/
                 js::New(requests_json.ExtractValue()),
                 /*__test__=*/js::New(GetTestName()),
                 /*__testcase__=*/js::New(GetTestcaseName())))
      .As<resource_management::Instances>();
}

}  // namespace js_pipeline::testing
