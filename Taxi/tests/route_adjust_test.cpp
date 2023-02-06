#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/route_adjust.hpp>

TEST(RouteAdjustConfig, Ping) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  ASSERT_NO_THROW(config.Get<config::RouteAdjust>());
}
