#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/xiva_config.hpp>

TEST(TestXivaConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::Xiva& xiva_config = config.Get<config::Xiva>();
  ASSERT_EQ(xiva_config.available_xiva_send_methods.Get().size(), 2u);
}
