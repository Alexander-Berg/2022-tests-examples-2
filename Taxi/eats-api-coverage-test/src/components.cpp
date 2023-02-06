#include <userver/components/component_list.hpp>

#include <userver/server/handlers/ping.hpp>

namespace eats_api_coverage_test {

void RegisterUserComponents(components::ComponentList& component_list) {
  component_list.Append<server::handlers::Ping>();
}

}  // namespace eats_api_coverage_test
