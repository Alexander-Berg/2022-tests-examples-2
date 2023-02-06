#pragma once

#include <tvm2/client_context.hpp>
#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/server/handlers/http_handler_base.hpp>
#include <userver/server/http/http_response_body_stream_fwd.hpp>

namespace test_service {
namespace handlers {

class NobuffExternalEcho : public server::handlers::HttpHandlerBase {
 public:
  // `kName` must match component name in config.yaml
  static constexpr std::string_view kName = "handler-nobuf-external-echo";

  // Component is valid after construction and is able to accept requests
  NobuffExternalEcho(const components::ComponentConfig&,
                     const components::ComponentContext&);

  void HandleStreamRequest(const server::http::HttpRequest&,
                           server::request::RequestContext&,
                           server::http::ResponseBodyStream&&) const override;

 private:
  tvm2::ClientContext& http_client_;
  dynamic_config::Source config_source_;
};

}  // namespace handlers
}  // namespace test_service
