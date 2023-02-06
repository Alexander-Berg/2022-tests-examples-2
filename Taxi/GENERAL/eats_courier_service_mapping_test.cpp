#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/eats_courier_service_mapping.hpp>

TEST(EatsCourierServiceMapping, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& eats_courier_service_mapping =
      config.Get<config::EatsCourierServiceMapping>();
  ASSERT_EQ(eats_courier_service_mapping.selfemployed_park_id, std::nullopt);
  ASSERT_EQ(eats_courier_service_mapping.zone_mappings.empty(), true);
}
