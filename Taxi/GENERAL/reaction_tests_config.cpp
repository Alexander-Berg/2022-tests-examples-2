#include "reaction_tests_config.hpp"

namespace config {

ReactionTests::ReactionTests(const config::DocsMap& docs_map)
    : reaction_tests_show_to_driver("REACTION_TESTS_SHOW_TO_DRIVER", docs_map),
      gopher_error_limit("GOPHER_ERROR_LIMIT", docs_map),
      gopher_square_delay_ms("GOPHER_SQUARE_DELAY_MS", docs_map),
      gopher_square_duration_step_ms("GOPHER_SQUARE_DURATION_STEP_MS",
                                     docs_map),
      gopher_square_initial_duration_ms("GOPHER_SQUARE_INITIAL_DURATION_MS",
                                        docs_map),
      gopher_square_minimal_duration_ms("GOPHER_SQUARE_MINIMAL_DURATION_MS",
                                        docs_map),
      gopher_squares_per_same_duration("GOPHER_SQUARES_PER_SAME_DURATION",
                                       docs_map),
      gopher_time_limit_ms("GOPHER_TIME_LIMIT_MS", docs_map),
      schulte_error_limit_per_table("SCHULTE_ERROR_LIMIT_PER_TABLE", docs_map),
      schulte_restart_limit("SCHULTE_RESTART_LIMIT", docs_map),
      schulte_table_count("SCHULTE_TABLE_COUNT", docs_map),
      schulte_time_limit_per_table_ms("SCHULTE_TIME_LIMIT_PER_TABLE_MS",
                                      docs_map),
      schulte_result_average_limit_ms("SCHULTE_RESULT_AVERAGE_LIMIT_MS",
                                      docs_map),
      schulte_result_table_count_limit("SCHULTE_RESULT_TABLE_COUNT_LIMIT",
                                       docs_map) {}

}  // namespace config
