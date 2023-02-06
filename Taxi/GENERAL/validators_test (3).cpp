#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>

#include <ibox/validators.hpp>

namespace iv = ::ibox::validators;

TEST(NormalizationsTest, SimplifyName) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& taxi_config = config.Get<taxi_config::TaxiConfig>();
  EXPECT_EQ(iv::SimplifyName("Ё", taxi_config), "Е");
  EXPECT_EQ(iv::SimplifyName("ABCEHKMOPTXY", taxi_config), "ABCEHKMOPTXY");
  EXPECT_EQ(iv::SimplifyName("abcehkmoptxy", taxi_config), "abcehkmoptxy");
  EXPECT_EQ(iv::SimplifyName("Ёршунов", taxi_config), "Ершунов");
  // ё and ë are different
  EXPECT_EQ(iv::SimplifyName("Ёёеë", taxi_config), "Ееее");
}
