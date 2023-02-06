#include "test_runner.hpp"

#include <js/execution/interface.hpp>
#include <js/utils.hpp>

#include <defs/internal/admin_script_test_schema.hpp>

#include <models/script.hpp>
#include <scoring/execution/js/postprocess_results_serialization.hpp>
#include <utils/json_contexts.hpp>

#include "names.hpp"

namespace driver_scoring::admin::script_tests::execution::js {

namespace {

namespace test_schemas = ::defs::internal::admin_script_test_schema;

std::string FormatOptionalException(const std::optional<std::string>& got) {
  if (got) {
    return *got;
  }
  return "failed to parse js exception";
}

Result ExceptionMismatchResult(const std::optional<std::string>& got) {
  formats::json::ValueBuilder builder;
  builder[kExceptionMessage] = FormatOptionalException(got);
  Result res{Status::kExpectationFailed};
  res.failed_expectations = {builder.ExtractValue()};
  return res;
}

template <class Output>
Result CreateFailedExpectation(Output output) {
  Result result{Status::kExpectationFailed};
  result.failed_expectations = {
      formats::json::ValueBuilder(std::move(output)).ExtractValue()};
  return result;
}

template <class Output>
Result CreateFailedException(Output output) {
  auto res = CreateFailedExpectation(std::move(output));
  res.message = "expected exception did not happen";
  return res;
}

Result ScriptTimeoutResult() {
  Result result{Status::kTimeout};
  result.message = "script took too long";
  return result;
}

v8::Local<v8::Value> ConstructUndefined() {
  return utils::FrozenLocal(formats::json::ValueBuilder().ExtractValue());
}

::formats::json::Value CreateEmptyScoringResults(
    const std::vector<size_t>& candidates_count) {
  auto arg = ::defs::internal::postprocess_results::ScoringResultsArg{};
  arg.orders.resize(candidates_count.size());
  for (size_t idx = 0; idx < candidates_count.size(); ++idx) {
    arg.orders[idx].candidates.resize(candidates_count[idx]);
    arg.orders[idx].candidates_count = candidates_count[idx];
  }
  return ::formats::json::ValueBuilder(arg).ExtractValue();
}

struct BonusArgs {
  v8::Local<v8::Value> common_context;
  v8::Local<v8::Value> order_context;
  v8::Local<v8::Value> candidate_context;
  v8::Local<v8::Value> trace;

  BonusArgs() {
    common_context = ConstructUndefined();
    order_context = ConstructUndefined();
    candidate_context = ConstructUndefined();
    trace = ConstructUndefined();
  }
};

struct PostprocessResultsArgs {
  v8::Local<v8::Value> common_context;
  v8::Local<v8::Value> order_contexts;
  v8::Local<v8::Value> candidates_contexts;
  v8::Local<v8::Value> traces;
  v8::Local<v8::Value> scoring_results;

  PostprocessResultsArgs() {
    common_context = ConstructUndefined();
    order_contexts = ConstructUndefined();
    candidates_contexts = ConstructUndefined();
    traces = ConstructUndefined();
    scoring_results = ConstructUndefined();
  }
};

PostprocessResultsArgs GetPostprocessResultsTestInput(
    const test_schemas::PostprocessResultsTestInput& input_values) {
  PostprocessResultsArgs args;
  if (const auto& given = input_values.common_context) {
    args.common_context = utils::FrozenLocal(given->extra);
  }
  size_t bulk_size = 0;
  if (const auto& given = input_values.order_contexts) {
    bulk_size = given->size();
    args.order_contexts =
        utils::FrozenLocal(formats::json::ValueBuilder(*given).ExtractValue());
  }
  std::vector<size_t> candidates_count;
  if (const auto& given = input_values.candidates_contexts) {
    bulk_size = given->size();
    candidates_count.reserve(bulk_size);
    for (auto&& entry : *given) {
      candidates_count.push_back(entry.size());
    }
    args.candidates_contexts =
        utils::FrozenLocal(formats::json::ValueBuilder(*given).ExtractValue());
  }
  if (candidates_count.empty()) {
    // user provided order_contexts only
    candidates_count.resize(bulk_size, 0);
  }
  if (const auto& given = input_values.scoring_results) {
    args.scoring_results = utils::MutableLocal(given->extra);
  } else {
    args.scoring_results =
        utils::MutableLocal(CreateEmptyScoringResults(candidates_count));
  }
  args.traces = utils::MutableLocal(
      scoring::execution::js::postprocess_results::CreateTraceArg(bulk_size));
  return args;
}

template <class TestInput>
BonusArgs GetBonusTestInput(const TestInput& input_values) {
  BonusArgs args;
  if (const auto& given = input_values.common_context) {
    args.common_context = utils::FrozenLocal(given->extra);
  }
  if (const auto& given = input_values.order_context) {
    args.order_context = utils::FrozenLocal(given->extra);
  }
  if (const auto& given = input_values.candidate_context) {
    args.candidate_context = utils::FrozenLocal(given->extra);
  }
  args.trace = ::js::NewObject();
  return args;
}

template <class Test>
Result RunBonusTest(const Test& test,
                    engine::TaskProcessor& timer_task_processor,
                    std::chrono::milliseconds timeout,
                    const std::string& function_name) {
  auto args = GetBonusTestInput(test.input_values);
  decltype(test.output_values) output;

  output.return_value = ::js::TypeCast<typename decltype(
      test.output_values.return_value)::value_type>(
      ::js::CallWithTimeout(timer_task_processor, timeout,
                            ::js::FromContext<v8::Function>(function_name),
                            args.common_context, args.order_context,
                            args.candidate_context, args.trace));
  output.trace = {::js::TypeCast<formats::json::Value>(args.trace)};
  if (test.output_values.exception_message) {
    return CreateFailedException(std::move(output));
  }
  bool ok = true;
  // compare fields only when user wants to
  if (test.output_values.return_value &&
      output.return_value != test.output_values.return_value) {
    ok = false;
  } else {
    output.return_value = std::nullopt;
  }
  if (test.output_values.trace && output.trace != test.output_values.trace) {
    ok = false;
  } else {
    output.trace = std::nullopt;
  }
  if (!ok) {
    return CreateFailedExpectation(std::move(output));
  }
  return Result{Status::kOk};
}

Result RunTest(const test_schemas::CalculateTest& test,
               engine::TaskProcessor& timer_task_processor,
               std::chrono::milliseconds timeout) {
  static const std::string function_name =
      models::MergedScript::GetFunctionName(kFunctionName,
                                            models::ScriptType::kCalculate);

  return RunBonusTest(test, timer_task_processor, timeout, function_name);
}

Result RunTest(const test_schemas::FilterTest& test,
               engine::TaskProcessor& timer_task_processor,
               std::chrono::milliseconds timeout) {
  static const std::string function_name =
      models::MergedScript::GetFunctionName(kFunctionName,
                                            models::ScriptType::kFilter);

  return RunBonusTest(test, timer_task_processor, timeout, function_name);
}

Result RunTest(const test_schemas::PostprocessResultsTest& test,
               engine::TaskProcessor& timer_task_processor,
               std::chrono::milliseconds timeout) {
  static const std::string function_name =
      models::MergedScript::GetFunctionName(
          kFunctionName, models::ScriptType::kPostprocessResults);

  auto args = GetPostprocessResultsTestInput(test.input_values);
  ::js::CallWithTimeout(timer_task_processor, timeout,
                        ::js::FromContext<v8::Function>(function_name),
                        args.common_context, args.order_contexts,
                        args.candidates_contexts, args.traces,
                        args.scoring_results);
  test_schemas::PostprocessResultsTestOutput output;
  output.scoring_results = {
      ::js::TypeCast<formats::json::Value>(args.scoring_results)};
  output.traces = Parse(::js::TypeCast<formats::json::Value>(args.traces),
                        formats::parse::To<decltype(output.traces)>());
  if (test.output_values.exception_message) {
    return CreateFailedException(std::move(output));
  }
  bool ok = true;
  // compare only if user wants to
  if (test.output_values.scoring_results &&
      output.scoring_results != test.output_values.scoring_results) {
    ok = false;
  } else {
    output.scoring_results = std::nullopt;
  }
  if (test.output_values.traces && output.traces != test.output_values.traces) {
    ok = false;
  } else {
    output.traces = std::nullopt;
  }
  if (!ok) {
    return CreateFailedExpectation(std::move(output));
  }
  return Result{Status::kOk};
}

template <class ExpectedTest>
Result ParseTestAndRun(const ::handlers::ScriptTest& test,
                       engine::TaskProcessor& timer_task_processor,
                       std::chrono::milliseconds timeout) {
  ExpectedTest parsed;
  parsed.input_values =
      Parse(test.test_input.extra,
            formats::parse::To<decltype(parsed.input_values)>());
  parsed.output_values =
      Parse(test.test_output.extra,
            formats::parse::To<decltype(parsed.output_values)>());
  return RunTest(parsed, timer_task_processor, timeout);
}

}  // namespace

TestRunner::TestRunner(std::shared_ptr<Environment> env,
                       ErrorCatcher& error_catcher)
    : script_type_(env->request.type),
      timer_task_processor_(env->timer_task_processor),
      timeout_(env->single_test_timeout),
      error_catcher_(error_catcher) {}

Result TestRunner::Run(const ::handlers::ScriptTest& test) {
  try {
    // delegate test to specific function but catch exceptions
    switch (script_type_) {
      case ::handlers::ScriptType::kCalculate:
        return ParseTestAndRun<test_schemas::CalculateTest>(
            test, timer_task_processor_, timeout_);
      case ::handlers::ScriptType::kFilter:
        return ParseTestAndRun<test_schemas::FilterTest>(
            test, timer_task_processor_, timeout_);
      case ::handlers::ScriptType::kPostprocessResults:
        return ParseTestAndRun<test_schemas::PostprocessResultsTest>(
            test, timer_task_processor_, timeout_);
    }
  } catch (const ::js::TerminateError&) {
    return ScriptTimeoutResult();
  } catch (const ::js::ExecuteError&) {
    const auto& expected = test.test_output.extra[kExceptionMessage]
                               .As<std::optional<std::string>>();
    if (!expected) {
      throw;
    }
    const auto& got = error_catcher_.PopError();
    if (expected == got) {
      return Result{Status::kOk};
    }
    return ExceptionMismatchResult(got);
  }
}

}  // namespace driver_scoring::admin::script_tests::execution::js
