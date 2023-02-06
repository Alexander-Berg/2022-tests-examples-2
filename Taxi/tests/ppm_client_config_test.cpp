#include <gtest/gtest.h>

#include <clients/config.hpp>
#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(TestPickupPointsManagerClientConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& qos =
      config::GetClientQos<clients::pickup_points_manager::Config>(config,
                                                                   "some_path");
  ASSERT_EQ(qos.attempts, 3);
  ASSERT_EQ(qos.timeout_ms.count(), 200);
}
