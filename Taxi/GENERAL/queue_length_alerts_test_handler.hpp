#pragma once

#include <components/queue_length_alerts.hpp>
#include <userver/server/handlers/http_handler_json_base.hpp>

namespace callcenter_stats::components {

class QueueLengthAlertsTestHandler final
    : public server::handlers::HttpHandlerJsonBase {
 public:
  QueueLengthAlertsTestHandler(
      const ::components::ComponentConfig& config,
      const ::components::ComponentContext& component_context);

  static constexpr const char* kName = "queue-length-alerts-test-handler";

  const std::string& HandlerName() const override;

  formats::json::Value HandleRequestJsonThrow(
      const server::http::HttpRequest& request,
      const formats::json::Value& request_body,
      server::request::RequestContext& context) const override;

 private:
  QueueLengthAlerts& component_;
};

}  // namespace callcenter_stats::components
