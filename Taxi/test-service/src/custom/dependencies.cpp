#include <custom/dependencies.hpp>

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>

namespace custom {

Dependencies::Dependencies(const components::ComponentConfig& /*config*/,
                           const components::ComponentContext& /*context*/) {}

Dependencies::Extra Dependencies::GetExtra() const { return {}; }

};  // namespace custom
