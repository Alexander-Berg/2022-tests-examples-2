#include "utils/helpers/pack.hpp"

#include <gtest/gtest.h>

class PackIntoJsonFixture : public testing::Test {};

using utils::helpers::PackIntoJson;

TEST_F(PackIntoJsonFixture, TestMerging) {
  Json::Value a{Json::objectValue};

  a["x"] = 5;

  std::unordered_map<std::string, int> data;
  data["y"] = 9;

  PackIntoJson(a, data);

  ASSERT_TRUE(a.isMember("y"));
  ASSERT_EQ(9, a["y"].asInt());

  ASSERT_TRUE(a.isMember("x"));
  ASSERT_EQ(5, a["x"].asInt());
}

TEST_F(PackIntoJsonFixture, TestEmptyReplace) {
  Json::Value a{Json::nullValue};

  PackIntoJson(a, 9);
  ASSERT_TRUE(a.isIntegral());
  ASSERT_EQ(9, a.asInt());
}

TEST_F(PackIntoJsonFixture, TestEmptyMerging) {
  Json::Value a{Json::objectValue};

  a["x"] = 5;

  Json::Value b{a};

  std::unordered_map<std::string, int> data;
  PackIntoJson(a, data);

  ASSERT_EQ(b, a);
}
