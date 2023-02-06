#include <gtest/gtest.h>

#include <radio/detail/solomon/usage_percent_ssb_preparer.hpp>

namespace hejmdal::radio::detail::solomon {

TEST(UsagePersentSsbPreparer, MainTest) {
  static const std::string kExpectedProgram =
      "1 - "
      "{cluster='production',group='taxi_db_mongo_*',path='/Memory/"
      "MemAvailable',service='sys'} / "
      "{cluster='production',group='taxi_db_mongo_*',path='/Memory/"
      "MemTotal',service='sys'}";
  auto base_selector = clients::utils::SolomonSelectorBuilder().AddKeyValue(
      "group", "taxi_db_mongo_*");
  UsagePersentSsbPreparer tpl{
      "path", "/Memory/MemAvailable", "/Memory/MemTotal",
      "1 - {usage_selector} / {total_selector}",
      base_selector.Copy().Cluster("production").Service("sys")};

  EXPECT_EQ(kExpectedProgram, tpl.Build().Get());

  static const std::string kTotalProgram =
      "{cluster='production',group='taxi_db_mongo_*',path='/Memory/"
      "MemTotal',service='sys'}";
  EXPECT_EQ(kTotalProgram, tpl.BuildTotal().Get());
}

}  // namespace hejmdal::radio::detail::solomon
