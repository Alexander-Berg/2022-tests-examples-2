#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "qc_config.hpp"

TEST(TestQcConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::Qc& qc_config = config.Get<config::Qc>();
  ASSERT_EQ(qc_config.client.url.Get(),
            "http://quality-control.taxi.yandex.net");
  ASSERT_EQ(qc_config.client.retry, 3u);
  ASSERT_EQ(qc_config.client.timeout.Get(), std::chrono::milliseconds(100));
  ASSERT_EQ(qc_config.info_urls[boost::none], "");
  ASSERT_EQ(qc_config.exam_sort_order[boost::none], 100u);
  ASSERT_EQ(qc_config.restrictions_min_version.major, 8u);
  ASSERT_EQ(qc_config.restrictions_min_version.minor, 63u);
}
