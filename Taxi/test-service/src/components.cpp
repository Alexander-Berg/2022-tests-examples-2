#include <userver/components/component_list.hpp>

#include <userver/server/handlers/ping.hpp>

#include <handlers/nobuf_external_echo.hpp>

namespace test_service {

void RegisterUserComponents(components::ComponentList& component_list) {
  component_list.Append<server::handlers::Ping>()
      .Append<handlers::NobuffExternalEcho>();
}

}  // namespace test_service
