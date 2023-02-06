#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taximeter_polling_delays.hpp>

TEST(TestTaximeterPollingDelays, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& taximeter_polling_delays =
      config.Get<config::TaximeterPollingDelays>();
  ASSERT_EQ(900u, taximeter_polling_delays.Get("/driver/rating/item"));
}
