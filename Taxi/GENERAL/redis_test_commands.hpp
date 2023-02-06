#pragma once

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/server/handlers/http_handler_base.hpp>
#include <userver/storages/redis/client.hpp>

namespace samples {
namespace handlers {

class RedisTestCommands : public server::handlers::HttpHandlerBase {
 public:
  // `kName` must match component name in config.yaml
  static constexpr const char* kName = "handler-redis-test-commands";

  // Component is valid after construction and is able to accept requests
  RedisTestCommands(const components::ComponentConfig&,
                    const components::ComponentContext&);

  const std::string& HandlerName() const override;
  std::string HandleRequestThrow(
      const server::http::HttpRequest&,
      server::request::RequestContext&) const override;

 private:
  storages::redis::ClientPtr redis_ptr_;
};

}  // namespace handlers
}  // namespace samples
