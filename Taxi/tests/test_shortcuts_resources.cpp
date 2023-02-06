#include <gtest/gtest.h>

#include <string>

#include <ml/common/filesystem.hpp>
#include <ml/shortcuts/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("shorcuts_resources");
}  // namespace

TEST(ShortcutsResources, FoodTechBase) {
  auto base = ml::shortcuts::resources::v1::FoodTechBase(kTestDataDir, true);

  auto grocery_shortcuts = base.GetGroceryCategoryShortcutsByPlace(71249);
  ASSERT_EQ(grocery_shortcuts.size(), 4ul);
  auto empty_grocery_shortcuts = base.GetGroceryCategoryShortcutsByPlace(777);
  ASSERT_EQ(empty_grocery_shortcuts.size(), 0ul);

  auto eats_shortcuts = base.GetEatsPlaceShortcutsByPlace(57491);
  ASSERT_EQ(eats_shortcuts.size(), 1ul);
  auto empty_eats_shortcuts = base.GetEatsPlaceShortcutsByPlace(777);
  ASSERT_EQ(empty_eats_shortcuts.size(), 0ul);
}

TEST(ShortcutsResources, UserProfilesEmpty) {
  auto profiles =
      ml::shortcuts::resources::v1::UserProfiles(kTestDataDir, true);
  auto result = profiles.GetBrandPreference("aaa", 999);
  ASSERT_EQ(result.recent_orders_count, 0);
  ASSERT_EQ(result.last_order_age_days, 999);
}
TEST(ShortcutsResources, UserProfiles) {
  auto profiles =
      ml::shortcuts::resources::v1::UserProfiles(kTestDataDir, true);
  auto result = profiles.GetBrandPreference("aaa", 1);
  ASSERT_EQ(result.recent_orders_count, 10);
  ASSERT_EQ(result.last_order_age_days, 1);
}
