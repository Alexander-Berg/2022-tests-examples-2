#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "api_over_data_config.hpp"

TEST(TestDataApiConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::ApiOverData& api_over_data_config =
      config.Get<config::ApiOverData>();
  ASSERT_EQ(
      api_over_data_config.work_mode.Get("protocol").Get("driver-ratings"),
      api_over_data::work_mode::kOldWay);
}
