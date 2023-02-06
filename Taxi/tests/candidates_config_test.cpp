#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/candidates_config.hpp>
#include <config/config.hpp>

TEST(TestCandidatesConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& candidates_config = config.Get<config::Candidates>();
  ASSERT_EQ("http://candidates.taxi.yandex.net",
            candidates_config.base_url.Get());
  ASSERT_EQ(3, candidates_config.request_settings.Get("non_existent").retries);
  ASSERT_EQ(std::chrono::milliseconds(1000),
            candidates_config.request_settings.Get("non_existent").timeout_ms);
}
