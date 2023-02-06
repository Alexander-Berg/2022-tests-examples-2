#include <gtest/gtest.h>

#include <string>

#include "utils/geo.hpp"

TEST(TestUserplaces, TestGeoDescription) {
  auto res = userplaces::utils::GetDescriptionFromShortTextAndFullText(
      "улица Атасу, 12А",
      "Казахстан, Нур-Султан (Астана), микрорайон Чубары, улица Атасу, 12А, "
      "12");
  EXPECT_EQ(res.value(), "микрорайон Чубары, Нур-Султан (Астана), Казахстан");
}
