#include <gtest/gtest.h>

#include <common/include/configs.h>

namespace configs = models::configs;

TEST(Configs, Serialize) {
  configs::Configs configs;
  EXPECT_EQ(configs::Parse(configs::Serialize(configs)),
            configs);

  configs = {{"key1", "val1"}, {"key2", "val2"}};
  EXPECT_EQ(configs::Parse(configs::Serialize(configs)),
            configs);

  EXPECT_ANY_THROW(configs::Parse("invalid"));
}

TEST(Configs, Getters) {
  configs::Configs configs{
      {"string", "string"}, {"empty", ""}, {"int", "42"}, {"bool", "0"}};

  EXPECT_FALSE(configs::Get(configs, "missing").has_value());
  EXPECT_EQ(configs::Get(configs, "string").value_or(""), "string");
  EXPECT_EQ(configs::Get(configs, "empty").value_or("something"), "");
  EXPECT_EQ(configs::GetAsInt(configs, "int").value_or(0), 42);
  EXPECT_ANY_THROW(configs::GetAsInt(configs, "string"));
  EXPECT_EQ(configs::GetAsBool(configs, "bool").value_or(true), false);
  EXPECT_EQ(configs::GetAsBool(configs, "int").value_or(false), true);
}
