#pragma once

#include <config/value.hpp>

namespace config {

struct ReactionTests {
  Value<bool> reaction_tests_show_to_driver;
  Value<int> gopher_error_limit;
  Value<int> gopher_square_delay_ms;
  Value<int> gopher_square_duration_step_ms;
  Value<int> gopher_square_initial_duration_ms;
  Value<int> gopher_square_minimal_duration_ms;
  Value<int> gopher_squares_per_same_duration;
  Value<int> gopher_time_limit_ms;
  Value<int> schulte_error_limit_per_table;
  Value<int> schulte_restart_limit;
  Value<int> schulte_table_count;
  Value<int> schulte_time_limit_per_table_ms;

  Value<std::chrono::milliseconds> schulte_result_average_limit_ms;
  Value<int> schulte_result_table_count_limit;

  ReactionTests(const config::DocsMap& docs_map);
};

}  // namespace config
