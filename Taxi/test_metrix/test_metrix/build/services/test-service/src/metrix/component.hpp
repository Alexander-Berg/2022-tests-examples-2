#pragma once

#include <metrix/writer.hpp>
#include <userver/components/loggable_component_base.hpp>
#include <userver/components/statistics_storage.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/storage/component.hpp>
#include <userver/formats/json.hpp>
#include <userver/testsuite/component_control.hpp>
#include <userver/utils/scope_guard.hpp>

namespace metrix {

class Component final: public ::components::LoggableComponentBase {
 public:
  static constexpr const char* kName = "metrix";

  Component(const ::components::ComponentConfig& config,
            const ::components::ComponentContext& context);

  Writer& GetWriter();

  ~Component();

 private:
  formats::json::Value CollectMetrics();

  void Invalidate();

 private:
  Writer writer_;

  testsuite::ComponentInvalidatorHolder invalidator_holder_;
  ::utils::statistics::Entry statistics_holder_;
};

}  // namespace metrix
