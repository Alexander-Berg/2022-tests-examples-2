#include "request.hpp"

#include <string>
#include <unordered_map>

#include <gtest/gtest.h>

namespace eats_catalog::utils {

TEST(IsMagnitApp, Empty) {
  const std::string user_agent{""};
  ASSERT_FALSE(IsMagnitApp(user_agent));
}

TEST(IsMagnitApp, Web) {
  const std::string user_agent{
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:85.0) Gecko/20100101 "
      "Firefox/85.0"};
  ASSERT_FALSE(IsMagnitApp(user_agent));
}

TEST(IsMagnitApp, Regular) {
  const std::string user_agent{"Mozilla/5.0 MagnitApp_IosWeb/1.2.3"};
  ASSERT_TRUE(IsMagnitApp(user_agent));
}

TEST(IsMagnitApp, Upper) {
  const std::string user_agent{"MOZILLA/5.0 MAGNITAPP_IOSWEB/1.2.3"};
  ASSERT_TRUE(IsMagnitApp(user_agent));
}

TEST(IsMagnitApp, Lower) {
  const std::string user_agent{"mozilla/5.0 magnitapp_iosweb/1.2.3"};
  ASSERT_TRUE(IsMagnitApp(user_agent));
}

TEST(IsSuperapp, True) {
  const static std::unordered_map<std::string, bool> platforms{
      {"superapp_web", true},
      {"superapp_taxi_web", true},
      {"superapp_pp_web", true},
      {"superapp_bro_web", true},
      {"superapp_eats_web", true},
      {"desktop_web", false},
      {"ios_app", false},
      {"superapp_ios", false},
      {"", false},
  };

  for (const auto& [platform, expected] : platforms) {
    EXPECT_EQ(expected, IsSuperapp(platform))
        << "unexpected result for platform " << platform;
  }
}

}  // namespace eats_catalog::utils
