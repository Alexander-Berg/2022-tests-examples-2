#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/qc_covid19_settings.hpp>

TEST(TestQcCovid19Settings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& qc_covid19_settings = config.Get<config::QcCovid19Settings>();
  ASSERT_EQ(std::chrono::minutes(720), qc_covid19_settings.check_period);
}
