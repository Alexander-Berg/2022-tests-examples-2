#include <unordered_map>

#include <gtest/gtest.h>

#include <userver/utils/underlying_value.hpp>

#include <eats-shared/types.hpp>

namespace eats_shared {

TEST(Business, EnumValue) {
  constexpr const std::string_view message =
      "Illegal eats_shared::Business enum value";
  // NOTE(nk2ge5k): данный тест выглядит как параноя, но позволяет
  // гарантировать, что значение перечисления не будет, случано, изменино лучше
  // чем комментарий.
  EXPECT_EQ(utils::UnderlyingValue(Business::kRestaurant), 1) << message;
  EXPECT_EQ(utils::UnderlyingValue(Business::kStore), 2) << message;
  EXPECT_EQ(utils::UnderlyingValue(Business::kPharmacy), 3) << message;
  EXPECT_EQ(utils::UnderlyingValue(Business::kShop), 4) << message;
  EXPECT_EQ(utils::UnderlyingValue(Business::kZapravki), 5) << message;
}

TEST(Business, ToString) {
  const std::unordered_map<Business, std::string> kBuisinessString{
      {Business::kRestaurant, "restaurant"}, {Business::kStore, "store"},
      {Business::kPharmacy, "pharmacy"},     {Business::kShop, "shop"},
      {Business::kZapravki, "zapravki"},
  };

  for (const auto& [business, expected_string] : kBuisinessString) {
    EXPECT_EQ(ToString(business), expected_string)
        << "Unexpected string representation of eats_shared::Business enum "
           "value";
  }
}

}  // namespace eats_shared
