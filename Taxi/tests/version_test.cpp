#include <gtest/gtest.h>
#include <models/version.hpp>
#include <userver/crypto/base64.hpp>

#include <string>

namespace coupons::models {

std::string EncodeVersion(std::string version) {
  return crypto::base64::Base64Encode(version);
}

TEST(Version, RightVersion) {
  std::string version = EncodeVersion("1:1,2:2,3:3,4:4");
  coupons::models::CouponsVersion vers(version);
  EXPECT_EQ(vers.GetVersion("1"), 1);
  EXPECT_EQ(vers.GetVersion("2"), 2);
  EXPECT_EQ(vers.GetVersion("3"), 3);
  EXPECT_EQ(vers.GetVersion("4"), 4);
}

TEST(Version, NullVersion) {
  coupons::models::CouponsVersion vers;
  EXPECT_EQ(vers.GetVersion("1"), 1);

  EXPECT_EQ(vers.Serialize(), "");
}

TEST(Version, BadVersion) {
  {
    std::string version = EncodeVersion("1:1.2:2.3:3.4:4");
    coupons::models::CouponsVersion vers(version);
    EXPECT_EQ(vers.GetVersion("1"), 1);
    EXPECT_EQ(vers.GetVersion("2"), 1);
    EXPECT_EQ(vers.GetVersion("3"), 1);
    EXPECT_EQ(vers.GetVersion("4"), 1);

    EXPECT_EQ(vers.Serialize(), "");
  }
  {
    std::string version = EncodeVersion("1.1,2.2,3.3,4.4");
    coupons::models::CouponsVersion vers(version);
    EXPECT_EQ(vers.GetVersion("1"), 1);
    EXPECT_EQ(vers.GetVersion("2"), 1);
    EXPECT_EQ(vers.GetVersion("3"), 1);
    EXPECT_EQ(vers.GetVersion("4"), 1);

    EXPECT_EQ(vers.Serialize(), "");
  }
}

TEST(Version, Update) {
  coupons::models::CouponsVersion vers;
  vers.UpdateVersion("1", 21);
  vers.UpdateVersion("2", 100);
  vers.UpdateVersion("3", 33);
  EXPECT_EQ(vers.GetVersion("1"), 21);
  EXPECT_EQ(vers.GetVersion("2"), 100);
  EXPECT_EQ(vers.GetVersion("3"), 33);
}

TEST(Version, Serialize) {
  coupons::models::CouponsVersion vers;
  vers.UpdateVersion("1", 21);
  auto result = vers.Serialize();
  bool condition = result == EncodeVersion("1:21");
  EXPECT_TRUE(condition);

  vers.UpdateVersion("2", 100);
  result = vers.Serialize();
  condition = result == EncodeVersion("1:21,2:100");
  EXPECT_TRUE(condition);

  vers.UpdateVersion("3", 33);
  result = vers.Serialize();
  condition = result == EncodeVersion("1:21,2:100,3:33");
  EXPECT_TRUE(condition);
}

}  // namespace coupons::models
