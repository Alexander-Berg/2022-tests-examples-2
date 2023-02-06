#include <event_handling/processing-ng-action/testpoint.hpp>

#include <models/processing_events.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/core/variant/io/json.hpp>
#include <agl/core/yaml-helpers.hpp>
#include <agl/operators/agl-task.hpp>
#include <agl/operators/event/agl-event.hpp>
#include <userver/formats/json.hpp>
#include <userver/formats/yaml.hpp>
#include <userver/testsuite/testpoint.hpp>

namespace processing::event_handling {

ProcessingNgTestpointAction::ProcessingNgTestpointAction(
    const formats::yaml::Value& config, const ProcessingNgDeps&,
    const ::agl::core::variant::YamlParser::Deps& agl_parser_deps)
    : ProcessingNgAction(config, agl_parser_deps),
      tp_name_(config["testpoint-name"].As<std::string>()) {
  const ::agl::core::OperatedFields& fields =
      ::agl::core::GetOperatedFields(config);
  const auto it = fields.find("extra-data");
  if (it != fields.cend()) {
    extra_data_ =
        ::agl::core::variant::GetOperatorAndParse(it->second, agl_parser_deps);
  }
}

void ProcessingNgTestpointAction::PerformImpl(
    ::agl::core::ExecuterState& executer_state) const {
  auto payload_builder = [this, &executer_state] {
    formats::json::ValueBuilder result_builder;
    formats::json::ValueBuilder builder;

    auto event =
        executer_state
            .OptionalBinding<processing::agl::operators::event::AglEvent>();
    if (event) {
      result_builder["event_id"] = event->event_id_;
      result_builder["created"] = event->created_;
      result_builder["tag"] = event->tag_;
      if (event->payload_.IsAny()) {
        result_builder["update_metadata"] = event->payload_.AsJson();
      }
      builder["event"] = result_builder;
    }

    auto task =
        executer_state
            .OptionalBinding<processing::agl::operators::task::AglTask>();
    if (task) {
      result_builder["item_id"] = task->item_id_;
      result_builder["created"] = task->created_;
      if (task->payload_.IsAny()) {
        result_builder["update_metadata"] = task->payload_.AsJson();
      }
      builder["task"] = result_builder;
    }

    ::agl::core::Variant extra_data = extra_data_.Evaluate(executer_state);
    builder["extra-data"] = ::agl::core::variant::io::EncodeJson(extra_data);

    return builder.ExtractValue();
  };

  auto callback = [](const formats::json::Value& doc) {
    if (doc.IsObject()) {
      std::optional<std::string> simulated_error =
          doc["simulated-error"].As<std::optional<std::string>>(std::nullopt);
      if (simulated_error)
        throw std::runtime_error("simulated error: " + *simulated_error);
    }
  };

  TESTPOINT_CALLBACK(tp_name_, payload_builder(), callback);
}

void ProcessingNgTestpointAction::GetDependenciesImpl(
    ::agl::core::variant::Dependencies& out) const {
  extra_data_.GetDependencies(out);
}

}  // namespace processing::event_handling
