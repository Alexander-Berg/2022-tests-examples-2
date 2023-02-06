#include <gtest/gtest.h>

#include "widgets.hpp"

using eats_layout_constructor::sources::catalog::Place;
using eats_layout_constructor::utils::widgets::IsEnoughPlaces;

TEST(IsEnoughPlaces, NoValue) {
  std::vector<Place> places(1);
  ASSERT_TRUE(IsEnoughPlaces(places, std::nullopt));
}

TEST(IsEnoughPlaces, Enough) {
  std::vector<Place> places(4);
  ASSERT_TRUE(IsEnoughPlaces(places, 3));
}

TEST(IsEnoughPlaces, Zero) {
  std::vector<Place> places(1);
  ASSERT_FALSE(IsEnoughPlaces(places, 0));
}

TEST(IsEnoughPlaces, Negative) {
  std::vector<Place> places(1);
  ASSERT_FALSE(IsEnoughPlaces(places, -10));
}
