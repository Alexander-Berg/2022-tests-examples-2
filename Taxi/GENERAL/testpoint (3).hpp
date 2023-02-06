#pragma once

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/server/handlers/http_handler_base.hpp>

namespace samples {
namespace handlers {

class Testpoint : public server::handlers::HttpHandlerBase {
 public:
  // `kName` must match component name in config.yaml
  static constexpr const char* kName = "handler-testpoint";

  // Component is valid after construction and is able to accept requests
  Testpoint(const components::ComponentConfig&,
            const components::ComponentContext&);

  const std::string& HandlerName() const override;
  std::string HandleRequestThrow(
      const server::http::HttpRequest&,
      server::request::RequestContext&) const override;
};

}  // namespace handlers
}  // namespace samples
