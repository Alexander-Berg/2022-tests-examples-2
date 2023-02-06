#include "testing.hpp"

#include <userver/utils/uuid4.hpp>

#include <defs/all_definitions.hpp>
#include <handlers/dependencies.hpp>
#include <taxi_config/variables/EDA_DELIVERY_PRICE_TESTS.hpp>

#include <redis/command_control.hpp>
#include <views/internal/v1/cart-delivery-price-surge/post/view.hpp>
#include <views/v1/calc-delivery-price-surge/post/view.hpp>

namespace helpers::testing {

namespace {

using handlers::UserInfo;

const std::vector<std::optional<std::string> UserInfo::*> kRandomizedFields = {
    &UserInfo::user_id, &UserInfo::device_id, &UserInfo::yandex_uid,
    &UserInfo::personal_phone_id};

std::string ToString(const TestResults& test_results) {
  formats::json::ValueBuilder value_builder;
  value_builder["status"] = test_results.status;
  value_builder["responses"] = test_results.responses;
  value_builder["errors"] = test_results.errors;
  return ToString(value_builder.ExtractValue());
}

TestResults Parse(std::string_view value, formats::parse::To<TestResults>) {
  auto json = formats::json::FromString(value);
  TestResults test_results;
  test_results.status = json["status"].As<TestStatus>();
  test_results.responses =
      json["responses"].As<std::vector<formats::json::Value>>();
  test_results.errors = json["errors"].As<std::vector<std::string>>();
  return test_results;
}

std::string MakeTestResultsKey(const std::string& test_id) {
  return fmt::format("test:{}:results", test_id);
}

}  // namespace

TestProcessor::TestProcessor(
    const std::shared_ptr<storages::redis::Client> storage,
    const dynamic_config::Snapshot& config)
    : storage_(storage),
      redis_cc_(redis::GetCommandControl(config)),
      redis_ttl_(
          config[taxi_config::EDA_DELIVERY_PRICE_TESTS].redis_ttl_minutes) {}

void TestProcessor::StartTest(const std::string& test_id) const {
  TestResults test_results{TestStatus::kInProgress, {}, {}};
  const auto status_string = ToString(TestStatus::kInProgress);
  auto redis_request =
      storage_->Set(MakeTestResultsKey(test_id), ToString(test_results),
                    redis_ttl_, redis_cc_);
  redis_request.Get();
}

void TestProcessor::FinishTest(
    const std::string& test_id,
    const std::vector<formats::json::Value>& responses,
    const std::vector<std::string>& errors) const {
  TestResults test_results{TestStatus::kFinished, responses, errors};
  auto redis_request =
      storage_->Set(MakeTestResultsKey(test_id), ToString(test_results),
                    redis_ttl_, redis_cc_);
  redis_request.Get();
}

std::optional<TestResults> TestProcessor::GetTestResults(
    const std::string& test_id) const {
  auto redis_request = storage_->Get(MakeTestResultsKey(test_id), redis_cc_);
  auto opt_redis_value = redis_request.Get();
  if (!opt_redis_value) {
    return std::nullopt;
  }
  return Parse(opt_redis_value.value(), formats::parse::To<TestResults>());
}

template <typename View>
void ExecuteTest(const std::string& test_id, std::size_t requests_count,
                 std::unordered_map<std::string, std::string>&& headers,
                 formats::json::Value&& request_json,
                 handlers::Dependencies&& dependencies) {
  using RequestBody = typename View::RequestBody;
  using Response200 = typename View::Response200;
  using eats_authproxy_backend::AuthContext;
  const auto& config = dependencies.config;
  const auto max_consequent_errors =
      config[taxi_config::EDA_DELIVERY_PRICE_TESTS].max_consequent_errors;
  const helpers::testing::TestProcessor test_processor(
      dependencies.redis_delivery_price, dependencies.config);
  std::vector<formats::json::Value> successful_responses;
  std::vector<std::string> errors;
  eats_authproxy_backend::AuthContext auth_context;
  try {
    eats_authproxy_backend::HttpRequestHeaders auth_headers{
        std::move_iterator(headers.begin()), std::move_iterator(headers.end())};
    auth_context = eats_authproxy_backend::ParseAuthContext(auth_headers);
  } catch (const std::exception& err) {
    auto error = fmt::format("Failed to parse auth headers: {}", err.what());
    LOG_ERROR() << error;
    errors.push_back(std::move(error));
  }
  RequestBody request_body;
  try {
    request_body = request_json.As<RequestBody>();
  } catch (const std::exception& err) {
    auto error = fmt::format("Failed to parse request body: {}", err.what());
    LOG_ERROR() << error;
    errors.push_back(std::move(error));
  }
  if (!errors.empty()) {
    test_processor.FinishTest(test_id, {}, errors);
    return;
  }
  std::size_t consequent_errors = 0;
  while (successful_responses.size() < requests_count &&
         consequent_errors < max_consequent_errors) {
    try {
      auto randomized_request = request_body;
      auto& user_info = randomized_request.user_info;
      for (auto field : kRandomizedFields) {
        auto& opt_value = user_info.*field;
        if (!opt_value.has_value()) {
          opt_value = utils::generators::GenerateUuid();
        }
      }
      auto response_variant =
          View::Handle(std::move(randomized_request), AuthContext{auth_context},
                       dependencies);
      std::visit(
          [&](auto& response) {
            using Response = std::decay_t<decltype(response)>;
            if constexpr (std::is_base_of_v<Response200, Response>) {
              successful_responses.push_back(
                  formats::json::ValueBuilder{std::move(response)}
                      .ExtractValue());
              consequent_errors = 0;
            } else {
              errors.push_back(std::move(response.error));
              ++consequent_errors;
            }
          },
          response_variant);
    } catch (const std::exception& err) {
      LOG_ERROR() << "Failed to process request: " << err.what();
      errors.push_back(err.what());
      ++consequent_errors;
    }
  }
  test_processor.FinishTest(test_id, successful_responses, errors);
}

template void ExecuteTest<handlers::v1_calc_delivery_price_surge::post::View>(
    const std::string& test_id, std::size_t requests_count,
    std::unordered_map<std::string, std::string>&& headers,
    formats::json::Value&& request_json, handlers::Dependencies&& dependencies);

template void
ExecuteTest<handlers::internal_v1_cart_delivery_price_surge::post::View>(
    const std::string& test_id, std::size_t requests_count,
    std::unordered_map<std::string, std::string>&& headers,
    formats::json::Value&& request_json, handlers::Dependencies&& dependencies);

}  // namespace helpers::testing
