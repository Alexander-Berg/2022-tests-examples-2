#include <userver/components/component_list.hpp>

#include <userver/server/handlers/ping.hpp>

namespace test_sidecar_without_tvm {

void RegisterUserComponents(components::ComponentList& component_list) {
  component_list.Append<server::handlers::Ping>();
}

}  // namespace test_sidecar_without_tvm
