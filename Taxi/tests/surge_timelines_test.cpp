#include <gtest/gtest.h>

#include <grocery-surge-client-stuff/models/surge_timelines.hpp>

namespace tests {

using grocery_shared::DeliveryType;

TEST(SurgeTimelines, LookUpTimeline) {
  grocery_surge_client_stuff::models::SurgeTimelines timelines;
  for (auto [ts, value] : std::vector<std::tuple<int, double>>{
           {100, 0.1}, {110, 0.1}, {120, 0.3}, {130, 0.4}}) {
    timelines.Insert(
        grocery_shared::LegacyDepotId{"1"},
        grocery_surge_client_stuff::models::SurgeInfo{value},
        grocery_surge_shared::js::PipelineName{"pipeline"},
        DeliveryType::kPedestrian,
        std::chrono::system_clock::time_point{std::chrono::seconds{ts}});
  }

  for (auto [seconds, expected_level] : std::vector<std::tuple<int, double>>{
           {0, 0.1}, {1000, 0.4}, {115, 0.3}}) {
    auto load_level = timelines
                          .GetHistorical(grocery_shared::LegacyDepotId{"1"},
                                         DeliveryType::kPedestrian,
                                         std::chrono::system_clock::time_point{
                                             std::chrono::seconds{seconds}})
                          ->load_level;
    EXPECT_EQ(load_level, expected_level);
  }
}

}  // namespace tests
