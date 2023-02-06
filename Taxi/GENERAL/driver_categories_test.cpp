#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/driver_categories.hpp>

TEST(TestDriverCategoriesAPI, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& driver_categories_config =
      config.Get<config::DriverCategoriesAPI>();

  ASSERT_FALSE(driver_categories_config.UseDriverCategoriesAPI());
}
