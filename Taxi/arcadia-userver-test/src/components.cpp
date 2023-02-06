#include <userver/components/component_list.hpp>

#include <components/routing/router_component.hpp>
#include <components/stq_agent.hpp>
#include <userver/server/handlers/ping.hpp>

namespace arcadia_userver_test {

void RegisterUserComponents(components::ComponentList& component_list) {
  component_list.Append<server::handlers::Ping>();
  component_list.Append<::clients::routing::Component>();
}

}  // namespace arcadia_userver_test
