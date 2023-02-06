#pragma once

#include <userver/server/handlers/http_handler_json_base.hpp>

#include <logbroker-consumer/component.hpp>

namespace logbroker_consumer {

class TestsLogbrokerMessages final
    : public server::handlers::HttpHandlerJsonBase {
 public:
  TestsLogbrokerMessages(const components::ComponentConfig& config,
                         const components::ComponentContext& component_context);

  static constexpr const char* kName = "tests-logbroker-messages";

  const std::string& HandlerName() const override;

  formats::json::Value HandleRequestJsonThrow(
      const server::http::HttpRequest& request,
      const formats::json::Value& request_body,
      server::request::RequestContext& context) const override;

  Component& FindConsumerComponent(const components::ComponentConfig&,
                                   const components::ComponentContext&);

 private:
  Component& component_;
};

}  // namespace logbroker_consumer
