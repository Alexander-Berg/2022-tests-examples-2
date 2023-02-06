#include <custom/dependencies.hpp>

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>

namespace custom {

Dependencies::Dependencies(const components::ComponentConfig& /*config*/,
                           const components::ComponentContext& context)
    : ytlib_(context.FindComponent<ytlib::component::YtLib>()) {}

Dependencies::Extra Dependencies::GetExtra() const {
  // Init Extra from private fields
  return {ytlib_};
}

};  // namespace custom
