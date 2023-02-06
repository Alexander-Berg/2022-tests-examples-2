#include <custom/dependencies.hpp>

#include <userver/components/component.hpp>

namespace custom {

Dependencies::Dependencies(const components::ComponentConfig& /*config*/,
                           const components::ComponentContext& /*context*/) {
  // Get components from context via context.FindComponent<T>() and store their
  // contents in private fields
}

Dependencies::Extra Dependencies::GetExtra() const {
  // Init Extra from private fields
  return {};
}

};  // namespace custom
