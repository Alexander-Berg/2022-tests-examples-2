#include "testpoint.hpp"

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/testsuite/testpoint.hpp>

namespace samples {
namespace handlers {

Testpoint::Testpoint(const components::ComponentConfig& config,
                     const components::ComponentContext& context)
    : server::handlers::HttpHandlerBase(config, context) {}

const std::string& Testpoint::HandlerName() const {
  static const std::string kHandlerName = kName;
  return kHandlerName;
}

std::string Testpoint::HandleRequestThrow(
    const server::http::HttpRequest&, server::request::RequestContext&) const {
  TESTPOINT("sample", [] {
    formats::json::ValueBuilder builder;
    builder["id"] = "id";
    builder["value"] = 123;
    return builder.ExtractValue();
  }());

  return {};
}

}  // namespace handlers
}  // namespace samples
