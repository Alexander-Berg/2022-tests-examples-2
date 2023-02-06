#include <gtest/gtest.h>

#include "configs.hpp"

TEST(Configs, Serialize) {
  models::Configs configs;
  EXPECT_EQ(models::ParseConfigs(models::SerializeConfigs(configs)), configs);

  configs = {{"key1", "val1"}, {"key2", "val2"}};
  EXPECT_EQ(models::ParseConfigs(models::SerializeConfigs(configs)), configs);

  EXPECT_ANY_THROW(models::ParseConfigs("invalid"));
}
