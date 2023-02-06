#include <userver/components/component_list.hpp>

#include <userver/server/handlers/ping.hpp>

namespace fts_client_testsuite {

void RegisterUserComponents(components::ComponentList& component_list) {
  component_list.Append<server::handlers::Ping>();
}

}  // namespace fts_client_testsuite
