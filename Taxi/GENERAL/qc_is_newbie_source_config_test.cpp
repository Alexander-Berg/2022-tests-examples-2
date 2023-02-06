#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/qc_is_newbie_source_config.hpp>

TEST(TestQcIsNewbieSourceConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& is_newbie_config = config.Get<config::QcIsNewbieSourceConfig>();

  ASSERT_EQ(is_newbie_config.sources_by_exam["dkk"],
            config::QcIsNewbieSource::Redis);
}
