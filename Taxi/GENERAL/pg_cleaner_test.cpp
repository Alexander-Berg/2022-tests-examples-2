#include "pg_cleaner.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(PgCleaner, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& pg_cleaner_config = config.Get<config::reposition::PgCleaner>();

  ASSERT_NO_THROW(
      const auto& options = pg_cleaner_config.Get("__default__", "__default__");
      ASSERT_EQ(5000u, options.limit); ASSERT_EQ(1u, options.age.count()));
}

TEST(PgCleaner, Custom) {
  const auto data = R"({
    "__default__": {
      "__default__": {
        "age_hours": 1,
        "limit": 5000
      }
    },
    "custom_schema": {
      "__default__": {
        "age_hours": 6,
        "limit": 60
      },
      "custom_table": {
        "age_hours": 12,
        "limit": 120
      }
    }
  })";

  auto docs_map = config::DocsMapForTest();
  docs_map.Override("REPOSITION_PGCLEANER", mongo::fromjson(data));
  const auto& config = config::Config(docs_map);
  const auto& pg_cleaner_config = config.Get<config::reposition::PgCleaner>();

  ASSERT_NO_THROW(const auto& options = pg_cleaner_config.Get(
                      "custom_schema.custom_table", "custom_schema");
                  ASSERT_EQ(120u, options.limit);
                  ASSERT_EQ(12u, options.age.count()));

  ASSERT_NO_THROW(const auto& options = pg_cleaner_config.Get(
                      "custom_schema.invalid_table", "custom_schema");
                  ASSERT_EQ(60u, options.limit);
                  ASSERT_EQ(6u, options.age.count()));

  ASSERT_NO_THROW(const auto& options = pg_cleaner_config.Get(
                      "invalid_schema.invalid_table", "invalid_schema");
                  ASSERT_EQ(5000u, options.limit);
                  ASSERT_EQ(1u, options.age.count()));
}
