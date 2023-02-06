#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

#include <models/partitions.hpp>

TEST(PartitionDateRange, stringtime_formats) {
  auto YYYY = ::utils::datetime::Stringtime(
      "2020_07011500", ::utils::datetime::kDefaultTimezone, "%Y_%m%d%H%M");
  auto yy = ::utils::datetime::Stringtime(
      "2007011500", ::utils::datetime::kDefaultTimezone, "%y%m%d%H%M");
  EXPECT_EQ(YYYY, yy);
}

TEST(PartitionDateRange, from_partition_name) {
  auto partition_name = "..._2020_070115_2020_070117";
  auto partition_range =
      billing_time_events::models::partitions::DateRange::FromPartitionName(
          partition_name);
  auto expected_from = ::utils::datetime::Stringtime(
      "2020_070115", ::utils::datetime::kDefaultTimezone, "%Y_%m%d%H");
  EXPECT_EQ(partition_range.from, expected_from);
  auto expected_to = ::utils::datetime::Stringtime(
      "2020_070117", ::utils::datetime::kDefaultTimezone, "%Y_%m%d%H");
  EXPECT_EQ(partition_range.to, expected_to);
}

TEST(PartitionDateRange, as_partition_postfix) {
  auto from = ::utils::datetime::Stringtime(
      "2020_070115", ::utils::datetime::kDefaultTimezone, "%Y_%m%d%H");
  auto to = ::utils::datetime::Stringtime(
      "2020_070117", ::utils::datetime::kDefaultTimezone, "%Y_%m%d%H");
  auto postfix = billing_time_events::models::partitions::DateRange{from, to}
                     .AsPartitionPostfix();
  auto expected = "2020_070115_2020_070117";
  EXPECT_EQ(postfix, expected) << "Failed with " << postfix << "!=" << expected;
}
