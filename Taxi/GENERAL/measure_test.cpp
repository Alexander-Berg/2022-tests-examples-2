#include <gtest/gtest.h>

#include <eats-full-text-search-models/measure.hpp>

TEST(ToStringMeasure, GenericToString) {
  const auto result = eats_full_text_search_models::ToStringMeasure(10, "GRM");
  ASSERT_EQ(result, "10 г");
}

TEST(ToStringMeasure, NextUnitToString) {
  const auto result =
      eats_full_text_search_models::ToStringMeasure(1100, "MLT");
  std::cerr << result << std::endl;
  ASSERT_EQ(result, "1.1 л");
}
