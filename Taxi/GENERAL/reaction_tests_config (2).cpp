#include "reaction_tests_config.hpp"

namespace config {

ReactionTests::ReactionTests(const config::DocsMap& docs_map)
    : reaction_tests_enabled("REACTION_TESTS_ENABLED", docs_map),
      reaction_tests_write_to_db_enabled("REACTION_TESTS_WRITE_TO_DB_ENABLED",
                                         docs_map),
      reaction_tests_max_calc_interval_minutes(
          "REACTION_TESTS_MAX_CALC_INTERVAL_MINUTES", docs_map),
      reaction_tests_offline_status_threshold_minutes(
          "REACTION_TESTS_OFFLINE_STATUS_THRESHOLD_MINUTES", docs_map),
      reaction_tests_enabled_by_city(ParseBoolValueBasedMap(
          docs_map.Get("REACTION_TESTS_ENABLED_BY_CITY"))),
      reaction_tests_rest_minutes(ParseMinutesValueBasedMap(
          docs_map.Get("REACTION_TESTS_REST_MINUTES"))),
      reaction_tests_max_work_after_long_rest_minutes(ParseMinutesValueBasedMap(
          docs_map.Get("REACTION_TESTS_MAX_WORK_AFTER_LONG_REST_MINUTES"))),
      reaction_tests_max_work_after_test_minutes(ParseMinutesValueBasedMap(
          docs_map.Get("REACTION_TESTS_MAX_WORK_AFTER_TEST_MINUTES"))) {}

}  // namespace config
