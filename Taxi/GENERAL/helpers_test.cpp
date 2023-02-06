#include "helpers.hpp"

#include <gtest/gtest.h>

TEST(ExtractMetaTypeClassic, One) {
  using handlers::helpers::ExtractMetaTypeClassic;

  EXPECT_STREQ("none", ExtractMetaTypeClassic("", "").c_str());
  EXPECT_STREQ("none", ExtractMetaTypeClassic("wtf", "").c_str());

  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/hello", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/hello?", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/hello?a=b", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/hello?a=b/c", "").c_str());

  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/1.x/hello", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/1.x/hello?", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/1.x/hello?a=b", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/1.x/hello?a=b/c", "").c_str());

  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/3.0/hello", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/3.0/hello?", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/3.0/hello?a=b", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/3.0/hello?a=b/c", "").c_str());

  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/newest/hello", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaTypeClassic("/newest/hello?", "").c_str());
  EXPECT_STREQ("hello",
               ExtractMetaTypeClassic("/newest/hello?a=b", "").c_str());
  EXPECT_STREQ("hello",
               ExtractMetaTypeClassic("/newest/hello?a=b/c", "").c_str());
}

TEST(ExtractMetaType, One) {
  using handlers::helpers::ExtractMetaType;

  EXPECT_STREQ("none", ExtractMetaType("", "").c_str());
  EXPECT_STREQ("none", ExtractMetaType("wtf", "").c_str());

  EXPECT_STREQ("hello", ExtractMetaType("/hello", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaType("/hello?", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaType("/hello?a=b", "").c_str());
  EXPECT_STREQ("hello", ExtractMetaType("/hello?a=b/c", "").c_str());

  EXPECT_STREQ("1.x-hello", ExtractMetaType("/1.x/hello", "").c_str());
  EXPECT_STREQ("1.x-hello", ExtractMetaType("/1.x/hello?", "").c_str());
  EXPECT_STREQ("1.x-hello", ExtractMetaType("/1.x/hello?a=b", "").c_str());
  EXPECT_STREQ("1.x-hello", ExtractMetaType("/1.x/hello?a=b/c", "").c_str());

  EXPECT_STREQ("3.0-hello", ExtractMetaType("/3.0/hello", "").c_str());
  EXPECT_STREQ("3.0-hello", ExtractMetaType("/3.0/hello?", "").c_str());
  EXPECT_STREQ("3.0-hello", ExtractMetaType("/3.0/hello?a=b", "").c_str());
  EXPECT_STREQ("3.0-hello", ExtractMetaType("/3.0/hello?a=b/c", "").c_str());

  EXPECT_STREQ("newest-hello", ExtractMetaType("/newest/hello", "").c_str());
  EXPECT_STREQ("newest-hello", ExtractMetaType("/newest/hello?", "").c_str());
  EXPECT_STREQ("newest-hello",
               ExtractMetaType("/newest/hello?a=b", "").c_str());
  EXPECT_STREQ("newest-hello",
               ExtractMetaType("/newest/hello?a=b/c", "").c_str());
}
