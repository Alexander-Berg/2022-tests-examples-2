#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "reaction_tests_config.hpp"

TEST(TestReactionTestsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::ReactionTests& reaction_tests_config =
      config.Get<config::ReactionTests>();
  ASSERT_EQ(reaction_tests_config.reaction_tests_show_to_driver, false);
  ASSERT_EQ(reaction_tests_config.gopher_error_limit, 50);
  ASSERT_EQ(reaction_tests_config.gopher_square_delay_ms, 500);
  ASSERT_EQ(reaction_tests_config.gopher_square_duration_step_ms, 250);
  ASSERT_EQ(reaction_tests_config.gopher_square_initial_duration_ms, 2000);
  ASSERT_EQ(reaction_tests_config.gopher_square_minimal_duration_ms, 500);
  ASSERT_EQ(reaction_tests_config.gopher_squares_per_same_duration, 10);
  ASSERT_EQ(reaction_tests_config.gopher_time_limit_ms, 60000);
  ASSERT_EQ(reaction_tests_config.schulte_error_limit_per_table, 10);
  ASSERT_EQ(reaction_tests_config.schulte_restart_limit, 15);
  ASSERT_EQ(reaction_tests_config.schulte_table_count, 5);
  ASSERT_EQ(reaction_tests_config.schulte_time_limit_per_table_ms, 30);
  ASSERT_EQ(reaction_tests_config.schulte_result_table_count_limit, 5);
  ASSERT_EQ(reaction_tests_config.schulte_result_average_limit_ms.Get(),
            std::chrono::milliseconds(50000));
}
