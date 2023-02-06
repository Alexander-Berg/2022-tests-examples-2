#include <components/testing_checker.hpp>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/storage/component.hpp>
#include "userver/components/loggable_component_base.hpp"
#include "userver/logging/log.hpp"

namespace eats_performer_statistics::components {

TestingChecker::TestingChecker(const ::components::ComponentConfig& config,
                               const ::components::ComponentContext& context)
    : ::components::LoggableComponentBase(config, context),
      is_testing_(config["is_testing"].As<bool>()) {}

bool TestingChecker::IsTesting() const { return is_testing_; }

}  // namespace eats_performer_statistics::components
