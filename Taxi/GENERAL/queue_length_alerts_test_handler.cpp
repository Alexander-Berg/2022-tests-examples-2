#include "queue_length_alerts_test_handler.hpp"

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>

namespace callcenter_stats::components {

QueueLengthAlertsTestHandler::QueueLengthAlertsTestHandler(
    const ::components::ComponentConfig& config,
    const ::components::ComponentContext& component_context)
    : server::handlers::HttpHandlerJsonBase(config, component_context),
      component_(component_context.FindComponent<QueueLengthAlerts>()) {}

const std::string& QueueLengthAlertsTestHandler::HandlerName() const {
  static const std::string kHandlerName = kName;
  return kHandlerName;
}

formats::json::Value QueueLengthAlertsTestHandler::HandleRequestJsonThrow(
    const server::http::HttpRequest& /*request*/,
    const formats::json::Value& /*request_body*/,
    server::request::RequestContext& /*context*/) const {
  // Just run one circle of checking and notifying
  component_.CheckAndNotify();

  return {};
}

}  // namespace callcenter_stats::components
