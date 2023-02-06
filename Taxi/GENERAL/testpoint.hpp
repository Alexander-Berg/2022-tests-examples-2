#pragma once

#include <agl/core/variant.hpp>
#include <event_handling/processing-ng-action.hpp>

#include <string>

namespace processing::event_handling {

class ProcessingNgTestpointAction : public ProcessingNgAction {
 public:
  ProcessingNgTestpointAction(
      const formats::yaml::Value&, const ProcessingNgDeps&,
      const ::agl::core::variant::YamlParser::Deps& parser_deps);

 private:
  void PerformImpl(::agl::core::ExecuterState&) const override;

  void GetDependenciesImpl(::agl::core::variant::Dependencies&) const override;

  std::string tp_name_;
  ::agl::core::Variant extra_data_;
};

using ProcessingNgTestpointActions =
    ProcessingNgActions<ProcessingNgTestpointAction>;

}  // namespace processing::event_handling
