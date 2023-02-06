#pragma once

#include <userver/server/handlers/http_handler_json_base.hpp>

#include "components/subcluster_loadness_calculator/subcluster_loadness_calculator.hpp"

namespace callcenter_queues::components {

class SubclusterLoadnessCalculatorTestHandler final
    : public server::handlers::HttpHandlerJsonBase {
 public:
  SubclusterLoadnessCalculatorTestHandler(
      const ::components::ComponentConfig& config,
      const ::components::ComponentContext& component_context);

  static constexpr const char* kName =
      "subcluster-loadness-calculator-test-handler";

  const std::string& HandlerName() const override;

  formats::json::Value HandleRequestJsonThrow(
      const server::http::HttpRequest& request,
      const formats::json::Value& request_body,
      server::request::RequestContext& context) const override;

 private:
  SubclusterLoadnessCalculator& component_;
  bool enabled_;
};

}  // namespace callcenter_queues::components
