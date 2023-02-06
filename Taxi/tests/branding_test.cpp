#include <branding/branding.hpp>

#include <gtest/gtest.h>

#include <userver/dynamic_config/storage_mock.hpp>

#include <taxi_config/variables/FRIEND_BRANDS.hpp>

TEST(TestBranding, FriendBrands) {
  dynamic_config::StorageMock config_storage{
      {taxi_config::FRIEND_BRANDS, {{"yango", "yataxi"}, {"yauber"}}}};
  const auto config = config_storage.GetSnapshot();

  ASSERT_EQ(branding::GetFriendBrands("yango", config),
            (std::vector<std::string>{"yango", "yataxi"}));
  ASSERT_EQ(branding::GetFriendBrands("yataxi", config),
            (std::vector<std::string>{"yango", "yataxi"}));
  ASSERT_EQ(branding::GetFriendBrands("yauber", config),
            (std::vector<std::string>{"yauber"}));
  ASSERT_EQ(branding::GetFriendBrands("go", config),
            (std::vector<std::string>{"go"}));
}
