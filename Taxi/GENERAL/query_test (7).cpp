#include <gtest/gtest.h>

#include <optional>

#include "query.hpp"

using namespace eats_picker_racks::utils::query;

const auto nullopt = std::optional<int>{};

TEST(HasNonEmpty, True) {
  ASSERT_TRUE(HasNonEmpty(1));
  ASSERT_TRUE(HasNonEmpty(1, 2));
  ASSERT_TRUE(HasNonEmpty(1, 2, "3"));
  ASSERT_TRUE(HasNonEmpty(1, 2, "3", nullopt));
  ASSERT_TRUE(HasNonEmpty(1, 2, "3", nullopt, nullopt));
}

TEST(HasNonEmpty, False) {
  ASSERT_FALSE(HasNonEmpty(nullopt));
  ASSERT_FALSE(HasNonEmpty(nullopt, nullopt));
  ASSERT_FALSE(HasNonEmpty(nullopt, nullopt, nullopt));
}
