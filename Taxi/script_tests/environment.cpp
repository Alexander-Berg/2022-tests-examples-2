#include "environment.hpp"

#include <handlers/dependencies.hpp>

#include <taxi_config/variables/DRIVER_SCORING_SCRIPT_TESTS.hpp>

namespace driver_scoring::admin::script_tests {

Environment::Environment(::handlers::ScriptCommitRequest&& request,
                         handlers::Dependencies&& dependencies)
    : request{request},
      js_component(dependencies.extra.js_component),
      timeout(dependencies.config[taxi_config::DRIVER_SCORING_SCRIPT_TESTS]
                  .timeout),
      single_test_timeout(
          dependencies.config[taxi_config::DRIVER_SCORING_SCRIPT_TESTS]
              .single_test_timeout),
      timer_task_processor(dependencies.extra.timer_task_processor) {}

}  // namespace driver_scoring::admin::script_tests
