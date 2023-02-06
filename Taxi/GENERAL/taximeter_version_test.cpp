#include "taximeter_version.hpp"

#include <gtest/gtest.h>

TEST(TaximeterVersion, Parse) {
  taximeter::Version ver;

  ver.Parse("");
  EXPECT_EQ(0u, ver.major);
  EXPECT_EQ(0u, ver.minor);
  EXPECT_EQ(0u, ver.build);

  ver.Parse("1");
  EXPECT_EQ(1u, ver.major);
  EXPECT_EQ(0u, ver.minor);
  EXPECT_EQ(0u, ver.build);

  ver.Parse("1.2");
  EXPECT_EQ(1u, ver.major);
  EXPECT_EQ(2u, ver.minor);
  EXPECT_EQ(0u, ver.build);

  ver.Parse("1.2 (3)");
  EXPECT_EQ(1u, ver.major);
  EXPECT_EQ(2u, ver.minor);
  EXPECT_EQ(3u, ver.build);
}

TEST(TaximeterVersion, ToString) {
  taximeter::Version ver;

  EXPECT_STREQ("", ver.ToString().c_str());

  ver.major = 1;
  EXPECT_STREQ("1.0", ver.ToString().c_str());

  ver.minor = 2;
  EXPECT_STREQ("1.2", ver.ToString().c_str());

  ver.build = 3;
  EXPECT_STREQ("1.2 (3)", ver.ToString().c_str());
}
