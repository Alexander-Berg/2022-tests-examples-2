#include "tests.hpp"
#include "endpoints.hpp"
#include "path_params.hpp"

#include <agl/core/dynamic_config.hpp>
#include <agl/core/errors.hpp>
#include <agl/core/executer_state.hpp>
#include <agl/core/mock-experiments-client.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/path/json-pointer.hpp>
#include <agl/core/secdist-reader.hpp>
#include <agl/core/stackable-experiments.hpp>
#include <agl/core/variant/io/encoded-string.hpp>
#include <agl/core/variant/io/json.hpp>
#include <agl/sourcing/mock-resource.hpp>
#include <agl/util/json-diff.hpp>
#include <bindings/operator-request/request-binding.hpp>
#include <custom/dependencies.hpp>
#include <models/admin/errors.hpp>
#include <models/admin/resource.hpp>
#include <models/auth_context.hpp>
#include <models/handler_storage.hpp>
#include <models/pa_auth_context.hpp>
#include <models/test-params.hpp>

#include <fmt/format.h>

#include <set>

#include <userver/formats/json/serialize.hpp>
#include <userver/http/common_headers.hpp>
#include <userver/logging/log.hpp>

#include <experiments3/components/experiments3_cache.hpp>
#include <experiments3/models/cache_manager.hpp>

namespace {

namespace admin = api_proxy::models::admin;

std::string MakeExtendedMessage(
    const std::string& msg,
    const std::vector<agl::core::Location>& location_stack) {
  std::string res = msg + ". location stack: ";
  std::for_each(
      location_stack.rbegin(), location_stack.rend(),
      [&res](const agl::core::Location& loc) { res += loc.GetPath() + "; "; });
  return res;
}

void AssertEqual(const agl::core::Variant& result,
                 const agl::core::Variant& expected,
                 const std::string& test_name, const std::string& object_name,
                 std::vector<std::string>& test_errors,
                 agl::core::ExecuterState& executer_state) {
  if (!expected.IsNone() && !expected.Equals(result)) {
    test_errors.push_back(fmt::format(
        "{}: Response {} value doesn't match the expected one:\n"
        "Response: '{}'\n"
        "Expected: '{}'.",
        test_name, object_name,
        agl::core::variant::io::EncodeJsonString(result, executer_state).data,
        agl::core::variant::io::EncodeJsonString(expected, executer_state)
            .data));
  }
}

void AssertEqualDiff(const agl::core::Variant& result,
                     const agl::core::Variant& expected,
                     const std::string& test_name,
                     const std::string& object_name,
                     const std::string& object_prop,
                     std::vector<std::string>& test_errors,
                     agl::core::ExecuterState& executer_state) {
  if (!expected.IsNone() && !expected.Equals(result)) {
    auto req_json = agl::core::variant::io::EncodeJson(result, executer_state);
    auto exp_json =
        agl::core::variant::io::EncodeJson(expected, executer_state);
    const auto& diff = json_diff::HumanReadableDiffValues(exp_json, req_json);
    test_errors.push_back(
        fmt::format("{}: {} {} value doesn't match the expected one:\n"
                    "{}: '{}'\n"
                    "Expected: '{}'\n"
                    "Diff: {}.",
                    test_name, object_name, object_prop, object_name,
                    formats::json::ToString(req_json),
                    formats::json::ToString(exp_json), diff));
  }
}

std::shared_ptr<agl::core::DynamicConfig> MakeTestDynamicConfig(
    const agl::core::Variant& mock_config,
    agl::core::ExecuterState& executer_state,
    std::vector<std::string>& test_errors) {
  if (mock_config.IsNone()) return std::make_shared<agl::core::DynamicConfig>();

  const auto& mock_config_val = mock_config.Evaluate(executer_state);
  if (!mock_config_val.IsMap()) {
    test_errors.push_back("taxi_config is not a Map");
    return {};
  }

  auto result = std::make_shared<agl::core::DynamicConfig>();
  auto taxi_config_map = mock_config_val.AsMap();
  for (const auto& it : taxi_config_map) {
    result->SetConfig(
        it.first, agl::core::variant::io::EncodeJson(
                      *taxi_config_map.GetVariant(it.first), executer_state));
  }

  return result;
}

agl::core::Experiments3CacheResponse MakeExperimentsMock(
    const agl::core::Variant& mock_exp3_values,
    agl::core::ExecuterState& executer_state,
    std::vector<std::string>& test_errors) {
  namespace e3 = ::experiments3::models;
  agl::core::Experiments3CacheResponse mapped_data;

  if (mock_exp3_values.IsNone()) return mapped_data;

  const auto& mock_exp3_val = mock_exp3_values.Evaluate(executer_state);
  if (!mock_exp3_val.IsMap()) {
    test_errors.push_back("'experiments.values' is not an object");
    return mapped_data;
  }

  const auto& mock_exp3_map = mock_exp3_val.AsMap();

  for (const auto& [name, value_store] : mock_exp3_map) {
    agl::core::Variant value(value_store);
    e3::ExperimentResult result{
        name,
        agl::core::variant::io::EncodeJson(value.Evaluate(executer_state)),
        e3::ResultMetaInfo{}};
    mapped_data.emplace(name, std::move(result));
  }

  return mapped_data;
}

::experiments3::models::KwargsMap::Map MakeExperimentsKwargsMock(
    const std::vector<api_proxy::core::ParsedTest::Experiments::Kwarg>&
        parsed_kwargs,
    agl::core::ExecuterState& executer_state,
    std::vector<std::string>& test_errors) {
  ::experiments3::models::KwargsMap::Map mocked_kwargs;
  enum class KwargType { kBool, kInt, kDouble, kString };
  static const std::unordered_map<std::string, KwargType> typemap = {
      {"boolean", KwargType::kBool},
      {"integer", KwargType::kInt},
      {"string", KwargType::kString},
      {"double", KwargType::kDouble},
  };

  for (const auto& kwarg : parsed_kwargs) {
    if (!kwarg.enabled.IsNone()) {
      try {
        auto agl_enabled = kwarg.enabled.Evaluate(executer_state);
        const bool enabled = agl_enabled.AsBool();
        if (!enabled) continue;
      } catch (const std::runtime_error& err) {
        test_errors.push_back(
            fmt::format("test mocks: 'enabled' field for experiment kwarg '{}' "
                        "is expected to be bool",
                        kwarg.key));
        continue;
      }
    }

    auto it = typemap.find(kwarg.type);
    if (it == typemap.end()) {
      test_errors.push_back(fmt::format(
          "test mocks: unexpected experiment kwarg type for '{}'", kwarg.type));
      continue;
    }

    auto agl_value = kwarg.value.Evaluate(executer_state);
    ::experiments3::models::KwargValue value;
    try {
      switch (it->second) {
        case KwargType::kBool:
          value = agl_value.AsBool();
          break;
        case KwargType::kInt:
          value = agl_value.AsInt();
          break;
        case KwargType::kDouble:
          value = agl_value.AsDouble();
          break;
        case KwargType::kString:
          value = agl_value.AsString();
          break;
      }
    } catch (const std::runtime_error& err) {
      test_errors.push_back(
          fmt::format("type mismatch for kwarg mock '{}', type {} expected",
                      kwarg.key, kwarg.type));
      continue;
    }

    auto ret = mocked_kwargs.emplace(kwarg.key, value);
    if (!ret.second) {
      test_errors.push_back(
          fmt::format("duplicate kwarg mock key: {}", kwarg.key));
    }
  }

  return mocked_kwargs;
}

agl::core::Variant::Map EnsureIsMap(agl::core::Variant v,
                                    std::vector<std::string>& test_errors,
                                    const std::string& name) {
  if (v.IsNone()) {
    return agl::core::Variant::Map();
  }
  if (!v.IsMap()) {
    test_errors.push_back(fmt::format("Request {} object is not a Map", name));
    return {};
  }
  return std::move(v.AsMap());
}

server::http::HttpRequest::HeadersMap ExtractHeaders(
    agl::core::Variant v, std::vector<std::string>& test_errors) {
  server::http::HttpRequest::HeadersMap headers;
  for (const auto& [header, variant] :
       EnsureIsMap(std::move(v), test_errors, "headers")) {
    if (const std::string* value = boost::get<std::string>(&variant)) {
      headers[header] = *value;
    } else {
      test_errors.push_back(
          fmt::format("Failed to initialize RequestBinding. "
                      "Header '{}' contains non-string value",
                      header));
    }
  }
  return headers;
}

std::optional<agl::sourcing::MockFail> ParseFail(
    const agl::core::Variant& value) {
  if (value.IsNone()) return std::nullopt;
  const auto str = value.AsString();

  using MockFail = agl::sourcing::MockFail;
  using Name2Enum = std::vector<std::pair<std::string, MockFail>>;
  static const Name2Enum kName2Enum = {
      {"timeout", MockFail::TIMEOUT},
      {"fallbacking", MockFail::FALLBACKING},
      {"tech", MockFail::TECH},
      {"source_validation", MockFail::SOURCE_VALIDATION},
      {"rps-limit-breach", MockFail::RPS_LIMIT_BREACH}};

  static const auto names = [](const Name2Enum& name2enum) {
    std::vector<std::string> names;
    std::transform(name2enum.begin(), name2enum.end(),
                   std::back_inserter(names),
                   [](const auto& item) { return item.first; });
    return names;
  }(kName2Enum);

  const auto it =
      std::find_if(kName2Enum.begin(), kName2Enum.end(),
                   [&str](const auto& elem) { return elem.first == str; });
  if (it == kName2Enum.end()) {
    throw std::runtime_error(
        fmt::format("Unexpected '{}' mock fail. Possible values are: {}", str,
                    fmt::join(names, ", ")));
  }

  return it->second;
}

// TODO: explicitly emphasize at agl::core::Value render stages
std::vector<agl::sourcing::RenderedMockResource> RenderMockResources(
    const std::vector<agl::sourcing::MockResource>& raw_resources,
    agl::core::ExecuterState& executor_state,
    std::vector<std::string>& test_errors) {
  std::vector<agl::sourcing::RenderedMockResource> rendered_resource;

  for (const auto& raw : raw_resources) {
    try {
      rendered_resource.push_back(agl::sourcing::RenderedMockResource{
          raw.id,
          ParseFail(raw.fail.Evaluate(executor_state)),
          {
              raw.response.code.Evaluate(executor_state),
              raw.response.body.Evaluate(executor_state),
              raw.response.content_type.Evaluate(executor_state),
              raw.response.headers.Evaluate(executor_state),
          },
          {raw.expected_request.method,
           raw.expected_request.content_type.Evaluate(executor_state),
           raw.expected_request.url.Evaluate(executor_state),
           raw.expected_request.path_params.Evaluate(executor_state),
           raw.expected_request.body.Evaluate(executor_state),
           raw.expected_request.headers.Evaluate(executor_state),
           raw.expected_request.query.Evaluate(executor_state)},
          {raw.expected_call.count.Evaluate(executor_state),
           raw.expected_call.before.Evaluate(executor_state),
           raw.expected_call.after.Evaluate(executor_state)}});
    } catch (const std::exception& err) {
      test_errors.push_back(
          MakeExtendedMessage(err.what(), executor_state.LocationStack()));
    }
  }

  return rendered_resource;
}

api_proxy::models::PathParams ParseAndValidateUrl(
    const std::string& url_template, const agl::core::Variant& url,
    const agl::core::Variant& expected_path_params,
    agl::core::ExecuterState& executer_state, const std::string& test_name,
    std::vector<std::string>& errors) {
  api_proxy::models::PathParams params;
  params.path = url_template;
  if (url.IsNone()) return params;

  try {
    const auto url_value = url.Evaluate(executer_state).AsString();

    const boost::regex url_regex(
        api_proxy::models::HandlerStorage::CanonizeTemplate(url_template));

    params.path = url_value;
    bool ret = boost::regex_match(params.path, params.path_params, url_regex);
    if (!ret) {
      errors.push_back(fmt::format(
          "Requested url '{}' does not match endpoint url pattern '{}'",
          url_value, url_regex.str()));
    }

    const auto evaluated_pp = expected_path_params.Evaluate(executer_state);
    if (evaluated_pp.IsNone()) {
      return params;
    }

    const auto exp_pp = evaluated_pp.AsMap();
    agl::core::Variant::Map recv_pp;
    for (const auto& param : exp_pp) {
      const std::string& sub_name = param.first;
      const auto& sub_match = params.path_params[sub_name];
      if (sub_match.matched) {
        recv_pp.Set(sub_name, sub_match.str());
      }
    }

    AssertEqualDiff(recv_pp, exp_pp, test_name, "Request", "url path-params",
                    errors, executer_state);
  } catch (const std::exception& err) {
    errors.push_back(
        MakeExtendedMessage(err.what(), executer_state.LocationStack()));
  }

  return params;
}

class MessageCollector {
 public:
  std::vector<std::string>& messages() { return collected_messages_; }

  std::optional<std::string> ToTestStatus() const {
    if (collected_messages_.empty()) return std::nullopt;
    return fmt::format("{}\n", fmt::join(collected_messages_, "\n"));
  }

 private:
  std::vector<std::string> collected_messages_;
};

std::vector<admin::types::Resource> GetDbResources(
    const storages::postgres::ClusterPtr& pg_cluster,
    const std::set<std::string>& filter) {
  std::vector<std::string> res_filter(filter.begin(), filter.end());
  auto resources = admin::resource::ListGivenStable(pg_cluster, res_filter);

  if (filter.size() != resources.size()) {
    std::set<std::string> found_resources;
    for (const auto& res : resources) {
      found_resources.insert(res.id);
    }

    std::vector<std::string> unknown_resources;
    std::set_difference(filter.begin(), filter.end(), found_resources.begin(),
                        found_resources.end(),
                        std::back_inserter(unknown_resources));
    throw std::runtime_error(fmt::format("no such resources: {}",
                                         fmt::join(unknown_resources, ", ")));
  }

  return resources;
}

}  // namespace

namespace api_proxy::models {

std::optional<std::string> RunTest(
    const api_proxy::models::HandlerMatch& handler_match,
    const api_proxy::core::ParsedTest& test_data, const std::string& test_id,
    const std::optional<TestParameters> test_params,
    const ::components::Secdist& secdist,
    const std::vector<admin::types::Resource>& resources) {
  using agl::core::experiments::StorageType;

  std::vector<std::string> messages;
  MessageCollector test_errors;

  const auto& handler = handler_match.GetHandler();

  LOG_INFO() << "Running test: " << test_id;

  agl::core::ExecuterState executer_state;

  if (test_params) {
    executer_state.RegisterBinding(*test_params);
  }

  const auto test_dynamic_config = MakeTestDynamicConfig(
      test_data.taxi_config, executer_state, test_errors.messages());
  if (!test_dynamic_config) return test_errors.ToTestStatus();

  executer_state.RegisterBinding(*test_dynamic_config);

  auto test_exp3_result = MakeExperimentsMock(
      test_data.experiments.values, executer_state, test_errors.messages());
  auto test_conf3_result = MakeExperimentsMock(
      test_data.configs.values, executer_state, test_errors.messages());
  agl::core::StackableExperiments exp3_stack(test_exp3_result,
                                             test_conf3_result, nullptr);
  agl::core::MockExperiments3CacheClient mock_client(test_exp3_result,
                                                     test_conf3_result);
  executer_state.RegisterBinding(exp3_stack);

  const auto headers =
      ExtractHeaders(test_data.request_headers.Evaluate(executer_state),
                     test_errors.messages());
  if (!test_errors.messages().empty()) return test_errors.ToTestStatus();

  api_proxy::models::AuthContext auth_context(headers);
  auth_context.Prepare(handler.auth_schema);
  executer_state.RegisterBinding(auth_context.Get());

  core::variant::RequestBinding request_binding(
      test_data.request_body.Evaluate(executer_state),
      server::http::HttpRequest::HeadersMap(headers),
      EnsureIsMap(test_data.request_query.Evaluate(executer_state),
                  test_errors.messages(), "args"));
  if (!test_errors.messages().empty()) return test_errors.ToTestStatus();
  executer_state.RegisterBinding(request_binding);

  if (!test_data.experiments.expected_consumer.Evaluate(executer_state)
           .IsNone()) {
    std::string experiments_consumer =
        test_data.experiments.expected_consumer.Evaluate(executer_state)
            .AsString();
    LOG_INFO() << "Expected consumer for experiments was set to " +
                      experiments_consumer;
    mock_client.ExpectedConsumer(experiments_consumer,
                                 StorageType::kExperiments);
  }

  if (!test_data.configs.expected_consumer.Evaluate(executer_state).IsNone()) {
    std::string configs_consumer =
        test_data.configs.expected_consumer.Evaluate(executer_state).AsString();
    LOG_INFO() << "Expected consumer for configs was set to " +
                      configs_consumer;
    mock_client.ExpectedConsumer(configs_consumer, StorageType::kConfigs);
  }

  if (test_data.experiments.expected_kwargs) {
    const auto mocked_kwargs =
        MakeExperimentsKwargsMock(test_data.experiments.expected_kwargs.value(),
                                  executer_state, test_errors.messages());
    mock_client.ExpectedKwargs(mocked_kwargs, StorageType::kExperiments);
    mock_client.IgnoredKwargs(std::vector{"user_id", "phone_id", "yandex_uid",
                                          "application", "version"},
                              StorageType::kExperiments);
  }

  if (test_data.configs.expected_kwargs) {
    const auto mocked_kwargs =
        MakeExperimentsKwargsMock(test_data.configs.expected_kwargs.value(),
                                  executer_state, test_errors.messages());
    mock_client.ExpectedKwargs(mocked_kwargs, StorageType::kConfigs);
    mock_client.IgnoredKwargs(std::vector{"user_id", "phone_id", "yandex_uid",
                                          "application", "version"},
                              StorageType::kConfigs);
  }

  const auto resource_mocks = RenderMockResources(
      test_data.mocks, executer_state, test_errors.messages());
  if (!test_errors.messages().empty()) return test_errors.ToTestStatus();

  PathParams path_params =
      ParseAndValidateUrl(handler_match.path_template, test_data.request_url,
                          test_data.expected_path_params, executer_state,
                          test_id, test_errors.messages());
  if (!test_errors.messages().empty()) return test_errors.ToTestStatus();

  std::optional<std::string> expected_exception;
  {
    if (!test_data.expected_exc.Evaluate(executer_state).IsNone()) {
      expected_exception =
          test_data.expected_exc.Evaluate(executer_state).AsString();
    }
  }

  // render secdist
  agl::core::SecdistReader::Uptr secdist_reader;
  agl::core::Variant rendered_secdist_mock =
      test_data.secdist.Evaluate(executer_state);
  if (!rendered_secdist_mock.IsNone()) {
    if (!rendered_secdist_mock.IsMap()) {
      throw std::runtime_error(
          "mocked secdist is not a map, while expecting a map");
    }
    secdist_reader = agl::core::MakeSecdistReader(
        agl::core::variant::io::EncodeJson(rendered_secdist_mock));
  } else {
    secdist_reader = agl::core::MakeSecdistReader(secdist);
  }

  try {
    auto result = handler.executer_.ExecuteTest(
        test_data, test_params, resource_mocks, resources, *test_dynamic_config,
        mock_client, auth_context.Get(), secdist_reader, path_params,
        request_binding);

    if (expected_exception) {
      test_errors.messages().push_back(fmt::format(
          "{}: Expected exception during test execution, got none.", test_id));
    } else {
      auto expected_code = test_data.expected_code.Evaluate(executer_state);
      AssertEqual(result.status_code, expected_code, test_id, "code",
                  test_errors.messages(), executer_state);

      auto expected_body = test_data.expected_body.Evaluate(executer_state);
      AssertEqualDiff(result.body, expected_body, test_id, "Response", "body",
                      test_errors.messages(), executer_state);

      auto expected_content_type =
          test_data.expected_content_type.Evaluate(executer_state);
      AssertEqual(result.content_type, expected_content_type, test_id,
                  "content type", test_errors.messages(), executer_state);

      auto expected_headers =
          test_data.expected_headers.Evaluate(executer_state);
      auto result_headers = result.headers.AsMap();
      // Remove internal headers to simplify comparing in tests
      result_headers.Remove(http::headers::kContentType);
      AssertEqualDiff(result_headers, expected_headers, test_id, "Response",
                      "headers", test_errors.messages(), executer_state);
    }
  } catch (const agl::core::TestError& e) {
    if (expected_exception) {
      AssertEqual(e.what(), *expected_exception, test_id, "exception",
                  test_errors.messages(), executer_state);
    } else {
      test_errors.messages().push_back(
          fmt::format("{}: {}", test_id, e.what()));
    }
  } catch (const std::exception& e) {
    if (expected_exception) {
      AssertEqual(e.what(), *expected_exception, test_id, "exception",
                  test_errors.messages(), executer_state);
    } else {
      test_errors.messages().push_back(fmt::format(
          "{}: Exception during test execution: {}", test_id, e.what()));
    }
  }

  return test_errors.ToTestStatus();
}

std::vector<std::string> RunTests(
    const api_proxy::models::HandlerMatch& handler_match,
    const ::components::Secdist& secdist,
    const storages::postgres::ClusterPtr& pg_cluster) {
  std::vector<std::string> messages;

  const auto& handler = handler_match.GetHandler();
  if (handler.tests_.empty()) {
    LOG_INFO() << "No tests found for handler: "
               << handler_match.path_params.path
               << ", method: " << ToString(handler.method_);
    return {};
  }

  LOG_INFO() << "Running tests for handler: " << handler_match.path_params.path
             << ", method: " << ToString(handler.method_);

  // TODO: launch tests in parallel
  std::vector<admin::types::Resource> resources;
  try {
    resources =
        GetDbResources(pg_cluster, handler.executer_.RequiredResources());
  } catch (const std::exception& err) {
    messages.push_back(fmt::format(
        "Error while loading tests for endpoint '{}', method {}: {}",
        handler_match.path_params.path, handler.method_, err.what()));
    return messages;
  }

  size_t num_tests = 0;

  for (const auto& test_data : handler.tests_) {
    const size_t old_num_tests = num_tests;
    try {
      if (!test_data.parameters.empty()) {
        api_proxy::models::TestParametersFactory params_factory(
            test_data.parameters);
        const size_t num_subtests = params_factory.NumberOfCombinations();
        num_tests += num_subtests;

        for (size_t combo_id = 0; combo_id < num_subtests; ++combo_id) {
          const std::string subtest_id =
              test_data.id + params_factory.SubtestName(combo_id);
          auto error = RunTest(handler_match, test_data, subtest_id,
                               params_factory.MakeParameters(combo_id), secdist,
                               resources);
          if (error) messages.push_back(*error);
        }
      } else {
        num_tests++;
        auto error = RunTest(handler_match, test_data, test_data.id,
                             std::nullopt, secdist, resources);
        if (error) messages.push_back(*error);
      }
    } catch (const std::exception& err) {
      num_tests = old_num_tests + 1;
      messages.push_back(
          fmt::format("{}: Internal error: {}", test_data.id, err.what()));
    }
  }

  LOG_INFO() << "Test run finished. Failed " << messages.size() << "/"
             << num_tests << " tests";
  return messages;
}

void RunEndpointTests(const models::admin::types::Endpoint& endpoint,
                      const ::components::Secdist& secdist,
                      const storages::postgres::ClusterPtr& pg_cluster,
                      const agl::core::OperatorsRegistry& operators_registry,
                      const agl::modules::Manager& modules_manager) {
  static const std::vector<server::http::HttpMethod> kAllHttpMethods = {
      server::http::HttpMethod::kGet, server::http::HttpMethod::kPost,
      server::http::HttpMethod::kDelete, server::http::HttpMethod::kPut,
      server::http::HttpMethod::kPatch};

  std::vector<std::string> messages;
  try {
    const auto& handlers =
        CreateEndpointForTests(endpoint, operators_registry, modules_manager);
    PathParams path_params;
    path_params.path = endpoint.path;
    for (const auto& handler : handlers.handlers) {
      HandlerMatch handler_match(&handler, endpoint.id, endpoint.path,
                                 path_params, 0, std::nullopt);
      std::vector<std::string> errors =
          api_proxy::models::RunTests(handler_match, secdist, pg_cluster);
      std::copy(errors.begin(), errors.end(), std::back_inserter(messages));
    }
  } catch (Endpoints::LoadingFailed& e) {
    throw admin::errors::ValidationFailed(
        e.what(), agl::core::path::ToJsonPointer(e.Where()), e.Endpoint());
  }
  if (!messages.empty()) {
    throw admin::errors::TestsFailed(endpoint.path, std::move(messages));
  }
}

void RunEndpointTests(handlers::EndpointWithoutPathDef&& endpoint,
                      const std::string& id, const std::string& path,
                      const ::components::Secdist& secdist,
                      const storages::postgres::ClusterPtr& pg_cluster,
                      const agl::core::OperatorsRegistry& operators_registry,
                      const agl::modules::Manager& modules_manager) {
  handlers::EndpointDef endpoint_def(
      handlers::EndpointWithoutIdDef(std::move(endpoint),
                                     handlers::EndpointWithoutIdDefA1{path}),
      handlers::EndpointDefA1{id});
  return RunEndpointTests(admin::types::FromHandlerFormat(endpoint_def),
                          secdist, pg_cluster, operators_registry,
                          modules_manager);
}

void RunEndpointTests(const admin::types::EndpointUUID& uuid,
                      const models::admin::types::EndpointCode& code,
                      const ::components::Secdist& secdist,
                      const storages::postgres::ClusterPtr& pg_cluster,
                      const agl::core::OperatorsRegistry& operators_registry,
                      const agl::modules::Manager& modules_manager) {
  models::admin::types::EndpointControl control{0, code.git_commit_hash, true};
  return RunEndpointTests(
      models::admin::types::Endpoint::Make(uuid, 0, code, control), secdist,
      pg_cluster, operators_registry, modules_manager);
}
}  // namespace api_proxy::models
