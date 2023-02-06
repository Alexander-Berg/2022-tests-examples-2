#include <models/driver_weariness_info.hpp>

#include <userver/dump/test_helpers.hpp>

#include <gtest/gtest.h>

namespace {

using namespace models;
using namespace std::chrono_literals;

const std::unordered_map<std::string, std::vector<TimeRange>>
    kDriverWorkingRanges{
        {"dbid0_uuid0",
         {TimeRange{TimePoint{1000s}, TimePoint{1010s}},
          TimeRange{TimePoint{2000s}, TimePoint{2123s}}}},
        {"dbid0_uuid1", {TimeRange{TimePoint{3000s}, TimePoint{4000s}}}},
        {"dbid0_uuid2",
         {TimeRange{TimePoint{1000s}, TimePoint{1010s}},
          TimeRange{TimePoint{1010s}, TimePoint{1020s}},
          TimeRange{TimePoint{1020s}, TimePoint{1030s}}}},
        {"dbid1_uuid0",
         {TimeRange{TimePoint{6000s}, TimePoint{6010s}},
          TimeRange{TimePoint{7000s}, TimePoint{8010s}}}},
        {"dbid2_uuid1",
         {TimeRange{TimePoint{1000s}, TimePoint{3001s}},
          TimeRange{TimePoint{4000s}, TimePoint{5001s}},
          TimeRange{TimePoint{6000s}, TimePoint{7001s}},
          TimeRange{TimePoint{8000s}, TimePoint{9999s}}}}};

DriverWearinessInfo MakeDriverWearinessInfo() {
  DriverWorkingRanges driver_working_ranges;

  int64_t revision = 0;
  for (const auto& [driver_profile, ranges] : kDriverWorkingRanges) {
    for (const auto& range : ranges) {
      EXPECT_TRUE(
          driver_working_ranges.Append(driver_profile, range, ++revision));
    }
  }

  return models::DriverWearinessInfo{std::move(driver_working_ranges), {}, {}};
}

}  // namespace

TEST(DriverWearinessInfo, DumpRestore) {
  dump::TestWriteReadCycle(DriverWearinessInfo{});
  dump::TestWriteReadCycle(MakeDriverWearinessInfo());
}
