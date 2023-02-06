#pragma once

#include <userver/server/handlers/http_handler_json_base.hpp>

#include "components/system_info_holder/system_info_holder.hpp"

namespace callcenter_queues::components {

class SystemInfoHolderTestHandler final
    : public server::handlers::HttpHandlerJsonBase {
 public:
  SystemInfoHolderTestHandler(
      const ::components::ComponentConfig& config,
      const ::components::ComponentContext& component_context);

  static constexpr const char* kName = "system-info-holder-test-handler";

  const std::string& HandlerName() const override;

  formats::json::Value HandleRequestJsonThrow(
      const server::http::HttpRequest& request,
      const formats::json::Value& request_body,
      server::request::RequestContext& context) const override;

 private:
  SystemInfoHolder& component_;
  bool enabled_;
};

}  // namespace callcenter_queues::components
