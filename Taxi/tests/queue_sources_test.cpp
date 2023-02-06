#include <gtest/gtest.h>

#include <components/queue_sources/model.hpp>
#include <components/queue_sources/model_cache.hpp>

namespace umlaas::queue_sources {
TEST(TestQueueSources, EstimateTimeForDriver) {
  const std::vector<cache::PredictionItem> prediction_items{
      {15, 15}, {30, 20}, {60, 17}};

  EXPECT_EQ(EstimateTimeForDriver(5, prediction_items), 5);
  EXPECT_EQ(EstimateTimeForDriver(15, prediction_items), 15);
  EXPECT_EQ(EstimateTimeForDriver(18, prediction_items), 24);
  EXPECT_EQ(EstimateTimeForDriver(20, prediction_items), 30);
  EXPECT_EQ(EstimateTimeForDriver(24, prediction_items), 2430);
}
}  // namespace umlaas::queue_sources
