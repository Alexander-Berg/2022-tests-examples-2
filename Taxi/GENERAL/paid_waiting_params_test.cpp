#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/paid_waiting_params.hpp>

TEST(TestPaidWaitingParams, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& paid_waiting_params = config.Get<config::PaidWaitingParams>();
  ASSERT_EQ(500u, paid_waiting_params.radius_to_turn_off);
}
