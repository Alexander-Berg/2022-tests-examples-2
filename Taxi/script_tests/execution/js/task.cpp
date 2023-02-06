#include "task.hpp"

#include <chrono>
#include <optional>
#include <variant>

#include <userver/formats/json.hpp>

#include <defs/definitions/admin.hpp>
#include <defs/internal/admin_script_test_schema.hpp>
#include <defs/internal/postprocess_results.hpp>
#include <models/json_validation_visitor.hpp>
#include <scoring/contexts/json_validation.hpp>
#include <utils/format_script.hpp>
#include <utils/indexed_range.hpp>

#include "names.hpp"
#include "test_runner.hpp"

namespace driver_scoring::admin::script_tests::execution::js {

namespace {

namespace test_schemas = ::defs::internal::admin_script_test_schema;

using Error = ::handlers::TestErrorDescription;

using Errors = std::vector<Error>;

class TestDataVisitor final : public models::ErrorVisitor {
 public:
  void Visit(const std::string& name) override { state_.push_back({name}); }

  void Visit(size_t index) override { state_.push_back({index}); }

  void Leave() override { state_.pop_back(); }

  // ignore `required` for tests except top level once
  void RequiredPropertyNotFound(const std::string& name) override {
    if (state_.size() == 1) {
      CreateError("required field not found: " + name);
    }
  }

  void UnexpectedAdditionalProperty() override {
    CreateError("this property is unexpected");
  }

  void UnexpectedType(std::string error_message) override {
    CreateError(std::move(error_message));
  }

  // Invalidates visitor
  Errors ExtractErrors() { return std::move(errors_); }

  void CreateError(std::string message) {
    errors_.emplace_back();
    errors_.back().name = StateToString();
    errors_.back().description = std::move(message);
  }

 private:
  struct Event {
    std::variant<std::string, size_t> name;

    void AppendToStringBuffer(std::string& buf) const {
      if (name.index() == 0) {
        if (buf.size()) {
          buf += '.';
        }
        buf += std::get<std::string>(name);
      } else if (name.index() == 1) {
        buf += "[";
        buf += std::to_string(std::get<size_t>(name));
        buf += "]";
      }
    }
  };

  std::string StateToString() const {
    std::string res;
    for (const auto& entry : state_) {
      entry.AppendToStringBuffer(res);
    }
    return res;
  }

  std::vector<Event> state_;
  Errors errors_;
};

Result GeneralExceptionResult(const std::string str) {
  Result res{Status::kRuntimeError};
  res.message = str;
  return res;
}

// Little ad hoc function to check that bulk_size can be inferred in one and
// only one way
bool PostprocessResultsBulkSizeIsConsistent(
    const formats::json::Value& input_values) {
  size_t bulk_size = 0;
  if (const auto& given = input_values["order_contexts"]; given.IsArray()) {
    bulk_size = given.GetSize();
  }
  if (const auto& given = input_values["candidates_contexts"];
      given.IsArray()) {
    if (bulk_size != 0 && bulk_size != given.GetSize()) {
      return false;
    }
    bulk_size = given.GetSize();
  }
  return bulk_size > 0;
}

void ValidateTestInput(TestDataVisitor& visitor,
                       ::handlers::ScriptType script_type,
                       const ::handlers::ScriptTest& test) {
  // do not want to ignore required top level fields only
  visitor.Visit("test_input");
  switch (script_type) {
    case ::handlers::ScriptType::kCalculate:
      scoring::contexts::ValidateCalculateTestInput(test.test_input.extra,
                                                    visitor);
      break;
    case ::handlers::ScriptType::kFilter:
      scoring::contexts::ValidateFilterTestInput(test.test_input.extra,
                                                 visitor);
      break;
    case ::handlers::ScriptType::kPostprocessResults:
      scoring::contexts::ValidatePostprocessResultsTestInput(
          test.test_input.extra, visitor);
      if (!PostprocessResultsBulkSizeIsConsistent(test.test_input.extra)) {
        visitor.CreateError("bulk_size cannot be inferred or ambiguous");
      }
      break;
  }
  visitor.Leave();
}

void ValidateTestOutput(TestDataVisitor& visitor,
                        ::handlers::ScriptType script_type,
                        const ::handlers::ScriptTest& test) {
  // do not want to ignore required top level fields only
  visitor.Visit("test_output");
  switch (script_type) {
    case ::handlers::ScriptType::kCalculate:
      scoring::contexts::ValidateCalculateTestOutput(test.test_output.extra,
                                                     visitor);
      break;
    case ::handlers::ScriptType::kFilter:
      scoring::contexts::ValidateFilterTestOutput(test.test_output.extra,
                                                  visitor);
      break;
    case ::handlers::ScriptType::kPostprocessResults:
      scoring::contexts::ValidatePostprocessResultsTestOutput(
          test.test_output.extra, visitor);
      break;
  }
  if (test.test_output.extra.GetSize() == 0) {
    visitor.CreateError("test should use at least one output");
  }
  if (test.test_output.extra.HasMember(kExceptionMessage) &&
      test.test_output.extra.GetSize() != 1) {
    visitor.CreateError("if exception is expected do not expect anything else");
  }
  visitor.Leave();
}

Errors ValidateTest(::handlers::ScriptType script_type,
                    const ::handlers::ScriptTest& test) {
  TestDataVisitor visitor;
  ValidateTestInput(visitor, script_type, test);
  ValidateTestOutput(visitor, script_type, test);
  return visitor.ExtractErrors();
}

}  // namespace

Task::Task(
    std::shared_ptr<Environment> env, std::vector<PromiseType>&& promises,
    std::shared_ptr<scoring::execution::js::ExecutionInfo> execution_info)
    : env_(std::move(env)),
      promises_(std::move(promises)),
      execution_info_(execution_info) {
  const auto& script_typename = handlers::ToString(env_->request.type);
  script_ = utils::FormatScript(kFunctionName, script_typename,
                                env_->request.content);
}

const std::string* Task::GetScript() const { return &script_; }

v8::Local<v8::Value> Task::Execute(
    const ::js::execution::AsyncPublicContext& async_context) const {
  if (promises_.size() &&
      execution_info_->SetStateAndNotify(models::ExecutionState::kStarted,
                                         models::ExecutionState::kNotStarted)) {
    TestRunner test_runner(env_, error_catcher_);
    for (size_t idx = 0; idx < promises_.size(); ++idx) {
      async_context.CancellationPoint();
      Result result;
      auto format_errors =
          ValidateTest(env_->request.type, env_->request.tests[idx]);
      if (format_errors.size()) {
        result = Result{Status::kIncorrectFormat};
        result.invalid_data = std::move(format_errors);
      } else {
        try {
          result = test_runner.Run(env_->request.tests[idx]);
        } catch (const std::exception& exc) {
          result = GeneralExceptionResult(exc.what());
        }
      }
      promises_[idx].set_value(std::move(result));
    }
  }
  return ::js::New(true);
}

}  // namespace driver_scoring::admin::script_tests::execution::js
