#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "reaction_tests_config.hpp"

TEST(TestReactionTestsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::ReactionTests& reaction_tests_config =
      config.Get<config::ReactionTests>();
  ASSERT_EQ(reaction_tests_config.reaction_tests_enabled, false);

  ASSERT_EQ(
      reaction_tests_config.reaction_tests_max_calc_interval_minutes.Get(),
      std::chrono::minutes(60));
  ASSERT_EQ(reaction_tests_config
                .reaction_tests_offline_status_threshold_minutes.Get(),
            std::chrono::minutes(30));
  ASSERT_EQ(
      reaction_tests_config.reaction_tests_enabled_by_city.Get("__default__"),
      false);
  ASSERT_EQ(
      reaction_tests_config.reaction_tests_rest_minutes.Get("__default__"),
      std::chrono::minutes(360));
  ASSERT_EQ(
      reaction_tests_config.reaction_tests_max_work_after_long_rest_minutes.Get(
          "__default__"),
      std::chrono::minutes(10));
  ASSERT_EQ(
      reaction_tests_config.reaction_tests_max_work_after_test_minutes.Get(
          "__default__"),
      std::chrono::minutes(300));
}
