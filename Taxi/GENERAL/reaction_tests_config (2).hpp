#pragma once

#include <config/value.hpp>

namespace config {

struct ReactionTests {
  Value<bool> reaction_tests_enabled;
  Value<bool> reaction_tests_write_to_db_enabled;
  Value<std::chrono::minutes> reaction_tests_max_calc_interval_minutes;
  Value<std::chrono::minutes> reaction_tests_offline_status_threshold_minutes;
  BasedSettingsMapWithDefault<bool> reaction_tests_enabled_by_city;
  BasedSettingsMapWithDefault<std::chrono::minutes> reaction_tests_rest_minutes;
  BasedSettingsMapWithDefault<std::chrono::minutes>
      reaction_tests_max_work_after_long_rest_minutes;
  BasedSettingsMapWithDefault<std::chrono::minutes>
      reaction_tests_max_work_after_test_minutes;

  ReactionTests(const config::DocsMap& docs_map);
};

}  // namespace config
