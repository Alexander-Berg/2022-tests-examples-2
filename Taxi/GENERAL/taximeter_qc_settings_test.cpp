#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taximeter_qc_settings.hpp>

TEST(TestTaximeterQcSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& taximeter_qc_settings = config.Get<config::TaximeterQcSettings>();
  ASSERT_EQ(std::chrono::hours(3), taximeter_qc_settings.ready_gap_in_hours);
  ASSERT_EQ("on", taximeter_qc_settings.sync_mode);
  ASSERT_EQ("off", taximeter_qc_settings.sync_dkk);
  ASSERT_EQ("off", taximeter_qc_settings.sync_dkb);
  ASSERT_EQ("off", taximeter_qc_settings.sync_sts);
}
