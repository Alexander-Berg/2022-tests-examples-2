#include "test.hpp"

#include <cmath>
#include <stdexcept>
#include <string>
#include <utility>

#include <fastcgi2/request.h>
#include <json/json.h>
#include <v8.h>

#include <common/factories/rule_factory.hpp>
#include <common/rules/rule_id.hpp>
#include <component_util/named_component.hpp>
#include <components/v8.hpp>
#include <config/antifraud_config.hpp>
#include <config/config_component.hpp>
#include <handler_util/base.hpp>
#include <handler_util/errors.hpp>
#include <httpclient/headers.hpp>
#include <js/isolate_wrapper.hpp>
#include <js/utils.hpp>
#include <mongo/mongo.hpp>
#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>

namespace antifraud::handlers::rules {
namespace {

class PrepareTestsFailed : public std::runtime_error {
 public:
  using runtime_error::runtime_error;
};

class TestFailed : public std::runtime_error {
 public:
  using runtime_error::runtime_error;
};

class UnexpectedRuleResult : public std::runtime_error {
 public:
  using runtime_error::runtime_error;
};

class InvalidExpectedResultType : public std::logic_error {
 public:
  using logic_error::logic_error;
};

struct Rule {
  int type;
  std::string src;
};

Rule FetchRule(const Json::Value& json, const std::string& name) {
  const auto rule_json = utils::helpers::FetchObject(json, name);

  return {utils::helpers::FetchMember<int>(rule_json, "type"),
          utils::helpers::FetchMember<std::string>(rule_json, "src")};
}

struct Args {
  Rule rule;
};

Args ParseArgs(const std::string& request_body, const LogExtra& log_extra) {
  // ParseJsonRequest throws http_errors::BadRequest in case of failure
  const auto& request_json =
      utils::helpers::ParseJsonRequest(request_body, log_extra);

  auto args = Args{};
  try {
    args.rule = FetchRule(request_json, "rule");
  } catch (const utils::helpers::JsonParseError& exc) {
    throw http_errors::BadRequest{exc.what()};
  }

  return args;
}

std::string GetRuleFunctionName(int type) {
  using RuleFactory = common::factories::rule_factory::RuleFactory;
  namespace rule_id = common::rules::rule_id;

  const auto throw_not_supported = [type] {
    const auto rule_type_str = std::to_string(type);
    throw http_errors::InternalServerError{"rule with type " + rule_type_str +
                                           " not supported"};
  };

  const auto rule_type = [type]() -> std::optional<rule_id::RuleId> {
    try {
      return rule_id::From(type);
    } catch (const rule_id::BadCast&) {
    }
    return {};
  }();

  if (!rule_type) {
    // for all new types of rules, we consider 'handle' as the default function
    // name
    if (type > rule_id::To<int>(rule_id::RuleId::kPartialDebitStatus)) {
      return "handle";
    }

    throw_not_supported();
  }

  const auto rule_ptr = RuleFactory::Instance().Create(rule_type.value());

  if (!rule_ptr) {
    throw_not_supported();
  }

  return rule_ptr->GetFunctionName();
}

template <typename Type>
Type TypeCast(const v8::Local<v8::Value>& rule_result) {
  try {
    return ::js::TypeCast<Type>(rule_result);
  } catch (const std::runtime_error& exc) {
    throw UnexpectedRuleResult{exc.what()};
  }
}

bool CompareJson(v8::Local<v8::Value> lhs, v8::Local<v8::Value> rhs,
                 const LogExtra& log_extra) {
  auto context = ::js::CheckContext();

  if (lhs->IsObject()) {
    const auto expected_result = ::js::As<v8::Object>(lhs);
    const auto result = ::js::As<v8::Object>(rhs);

    const auto expected_property_names = expected_result->GetOwnPropertyNames();

    if (expected_property_names->Length() !=
        result->GetOwnPropertyNames()->Length()) {
      LOG_DEBUG() << "OBJECT PROPERTY LENGTH MISMATCH: "
                  << expected_property_names->Length()
                  << " != " << result->GetOwnPropertyNames()->Length()
                  << log_extra;

      return false;
    }

    for (int i = 0; i < static_cast<int>(expected_property_names->Length());
         ++i) {
      auto key = ::js::FromMaybe(expected_property_names->Get(context, i));

      LOG_DEBUG() << "TRY TO CMP PROPERTY FOR KEY: "
                  << *v8::String::Utf8Value(key) << log_extra;

      auto expected_value = ::js::FromMaybe(expected_result->Get(context, key));
      auto value = ::js::FromMaybe(result->Get(context, key));

      if (!CompareJson(expected_value, value, log_extra)) {
        return false;
      }
    }

    return true;
  } else if (lhs->IsArray()) {
    const auto expected_result = ::js::As<v8::Array>(lhs);
    const auto result = ::js::As<v8::Array>(rhs);

    if (expected_result->Length() != result->Length()) {
      LOG_DEBUG() << "ARRAY LENGTH MISMATCH: " << expected_result->Length()
                  << " != " << result->Length() << log_extra;

      return false;
    }

    for (int i = 0; i < static_cast<int>(expected_result->Length()); ++i) {
      auto expected_value = ::js::FromMaybe(expected_result->Get(context, i));
      auto value = ::js::FromMaybe(result->Get(context, i));

      if (!CompareJson(expected_value, value, log_extra)) {
        return false;
      }
    }

    return true;
  } else {
    auto isolate = ::js::CheckIsolate();

    LOG_DEBUG() << "TRY OTHER CMP: " << std::string{*v8::String::Utf8Value(lhs)}
                << " (" << ::js::TypeCast<std::string>(lhs->TypeOf(isolate))
                << ") "
                << " == " << std::string{*v8::String::Utf8Value(rhs)} << " ("
                << ::js::TypeCast<std::string>(rhs->TypeOf(isolate)) << ")"
                << log_extra;

    if (::js::TypeCast<std::string>(lhs->TypeOf(isolate)) !=
        ::js::TypeCast<std::string>(rhs->TypeOf(isolate))) {
      return false;
    }

    return std::string{*v8::String::Utf8Value(lhs)} ==
           std::string{*v8::String::Utf8Value(rhs)};
  }
}

class WorkerWithHttpResponse {
 public:
  WorkerWithHttpResponse(std::string& response, const LogExtra& log_extra)
      : response_(response), log_extra_(log_extra) {
    response_json_[kTestPassed] = true;
  }

  ~WorkerWithHttpResponse() {
    if (!response_json_[kTestPassed].asBool() && !tests_results_json_.empty()) {
      response_json_[kTestsResults] = std::move(tests_results_json_);
    }

    response_ = utils::helpers::WriteJson(response_json_);
  }

  template <typename PrepareTests>
  bool DoPrepareTests(PrepareTests prepare_tests) {
    try {
      prepare_tests();
    } catch (const PrepareTestsFailed& exc) {
      LOG_INFO() << exc.what() << log_extra_;
      response_json_[kTestPassed] = false;
      response_json_[kFatalError] = exc.what();
      return false;
    }
    return true;
  }

  template <typename Test>
  void DoTest(const std::string& test_name, Test test) {
    static constexpr auto kName = "name";
    static constexpr auto kPassed = "passed";
    static constexpr auto kError = "error";

    auto test_result = Json::Value{Json::objectValue};
    test_result[kName] = test_name;
    test_result[kPassed] = true;

    try {
      test();
    } catch (const TestFailed& exc) {
      LOG_INFO() << "test " << test_name << " failed: " << exc.what()
                 << log_extra_;
      response_json_[kTestPassed] = false;

      test_result[kPassed] = false;
      test_result[kError] = exc.what();
    }

    tests_results_json_.append(std::move(test_result));
  }

 private:
  static constexpr auto kTestPassed = "tests_passed";
  static constexpr auto kFatalError = "fatal_error";
  static constexpr auto kTestsResults = "tests_results";

  Json::Value response_json_{Json::objectValue};
  Json::Value tests_results_json_{Json::arrayValue};
  std::string& response_;
  const LogExtra& log_extra_;
};

class TestCase {
 public:
  TestCase(const config::AntifraudConfig& config, int type) {
    const auto& rules_test_cases = config.rules_test_cases.Get();
    const auto rule_type_str = std::to_string(type);

    const auto it = rules_test_cases.find(rule_type_str);

    if (it == rules_test_cases.end()) {
      throw http_errors::InternalServerError{
          "there is no test data for rules with type " + rule_type_str};
    }

    test_case_data_ = &it->second;
  }

  [[nodiscard]] const std::string& GetName() const { return name_; }

  [[nodiscard]] v8::Local<v8::Object> GetRuleArgs() const {
    const auto& rule_args_json = test_case_data_->GetRuleArgs().jsonString();
    return ::js::ParseJson(rule_args_json)->ToObject();
  }

  void CheckRuleResult(v8::Local<v8::Value> rule_result,
                       const LogExtra& log_extra) const {
    const auto& DoubleToString = [](double val) -> std::string {
      double i{};
      return std::modf(val, &i) != 0.0 ? std::to_string(val)
                                       : std::to_string(static_cast<int>(i));
    };

    const auto BoolToString = [](bool val) -> std::string {
      return val ? "true" : "false";
    };

    const auto ThrowUnexpectedRuleResult =
        [](const std::string& result, const std::string& expected_result) {
          throw UnexpectedRuleResult{"rule returned " + result + ", but " +
                                     expected_result + " was expected"};
        };

    const auto& expected_result_bson = test_case_data_->GetRuleResult();

    if (utils::mongo::OneOf(expected_result_bson, utils::mongo::kNumber)) {
      const auto& expected_result =
          utils::mongo::ToDouble(expected_result_bson);
      const auto& result = TypeCast<double>(rule_result);

      if (result != expected_result) {
        ThrowUnexpectedRuleResult(DoubleToString(result),
                                  DoubleToString(expected_result));
      }
    } else if (utils::mongo::OneOf(expected_result_bson, utils::mongo::kBool)) {
      const auto& expected_result = utils::mongo::ToBool(expected_result_bson);
      const auto& result = TypeCast<bool>(rule_result);

      if (result != expected_result) {
        ThrowUnexpectedRuleResult(BoolToString(result),
                                  BoolToString(expected_result));
      }
    } else if (expected_result_bson.type() == ::mongo::BSONType::String) {
      const auto& expected_result = expected_result_bson.String();
      const auto& result = TypeCast<std::string>(rule_result);

      if (result != expected_result) {
        ThrowUnexpectedRuleResult("'" + result + "'",
                                  "'" + expected_result + "'");
      }
    } else if (utils::mongo::OneOf(expected_result_bson,
                                   utils::mongo::kDocument)) {
      try {
        const auto expected_result = ::js::As<v8::Object>(::js::ParseJson(
            utils::mongo::ToDocument(expected_result_bson).jsonString()));
        const auto result = ::js::As<v8::Object>(rule_result);

        if (!CompareJson(expected_result, result, log_extra)) {
          throw UnexpectedRuleResult{"unexpected rule result"};
        }
      } catch (const std::exception&) {
        throw UnexpectedRuleResult{"unexpected rule result"};
      }
    } else {
      throw InvalidExpectedResultType{"expected result type is invalid"};
    }
  }

 private:
  const config::AntifraudConfig::RuleTestCase* test_case_data_;
  // TODO: In the bright future this name will be retrieving from
  // TODO: test cases container (mongo collection)
  const std::string name_{"basic_test"};
};

}  // namespace

void TestHandler::onLoad() {
  TVM2Handler::onLoad();

  auto& ctx = *context();

  v8_component_ = &::components::GetComponentRefByName<::components::V8>(
      ctx, ::components::V8::name);
  config_ = &::components::GetComponentRefByName<config::Component>(
      ctx, config::Component::name);
}

void TestHandler::onUnload() {
  config_ = nullptr;
  v8_component_ = nullptr;

  TVM2Handler::onUnload();
}

void TestHandler::HandleRequestThrowTVM2Checked(
    [[maybe_unused]] fastcgi::Request& request,
    ::handlers::BaseContext& context) {
  const auto cfg = config_->Get();
  const auto& antifraud_config = cfg->Get<config::AntifraudConfig>();

  if (antifraud_config.tvm_log_enabled) {
    if (!request.hasHeader(utils::http::headers::kXYaServiceTicket)) {
      LOG_INFO() << "AFS No TVM header: " << request.getUrl()
                 << context.log_extra;
    }
  }

  const auto& GetPreparationFailMessage =
      [](const std::string& preparation_name, const std::string& message) {
        return "failed to " + preparation_name + " js rule: " + message;
      };

  const auto& log_extra = context.log_extra;

  const auto& args = ParseArgs(context.request_body, log_extra);

  const auto rule_type = args.rule.type;
  const auto rule_src = ::js::UseStrict(args.rule.src);
  const auto rule_function_name = GetRuleFunctionName(rule_type);

  auto v8_isolate_wrapper = IsolateWrapper{};
  v8::Isolate::Scope v8_isolate_scope{v8_isolate_wrapper.Isolate()};
  v8::HandleScope v8_handle_scope{v8_isolate_wrapper.Isolate()};
  auto v8_context = v8::Context::New(v8_isolate_wrapper.Isolate());
  auto v8_context_scope = v8::Context::Scope{v8_context};

  auto worker = WorkerWithHttpResponse{context.response, log_extra};

  auto rule_script = v8::Local<v8::Script>{};

  if (!worker.DoPrepareTests([&] {
        try {
          rule_script = ::js::Compile(rule_src);
        } catch (const std::runtime_error& exc) {
          throw PrepareTestsFailed{
              GetPreparationFailMessage("compile", exc.what())};
        }

        try {
          ::js::Run(rule_script);
        } catch (const std::runtime_error& exc) {
          throw PrepareTestsFailed{
              GetPreparationFailMessage("run", exc.what())};
        }
      })) {
    return;
  }

  // This 'for' loop looks ridiculous, but it was made for
  // the bright future's sake - the future, when there will be an ability
  // to have more than one test case.
  // And this 'for' loop will be like this:
  //   const auto& test_cases = GetTestCases(antifraud_config, rule_type);
  //   for (const auto& test_case : test_cases) {
  for (auto test_case_index = 1; test_case_index < 2; ++test_case_index) {
    const auto& test_case = TestCase{antifraud_config, rule_type};

    const auto& test_name = test_case.GetName();
    const auto& rule_args = test_case.GetRuleArgs();

    worker.DoTest(test_name, [&] {
      v8::Local<v8::Value> rule_result = [&rule_function_name, &rule_args] {
        try {
          const auto& rule_function =
              ::js::FromContext<v8::Function>(rule_function_name);
          return ::js::Call(rule_function, rule_args);
        } catch (const std::runtime_error& exc) {
          throw TestFailed{exc.what()};
        }
      }();

      try {
        test_case.CheckRuleResult(rule_result, context.log_extra);
      } catch (const UnexpectedRuleResult& exc) {
        throw TestFailed{exc.what()};
      }
    });
  }
}

}  // namespace antifraud::handlers::rules
