#include <gtest/gtest.h>

#include "copy.hpp"

namespace eats_catalog::utils {

TEST(CopyIf, Empty) {
  const std::vector<int> input;
  const auto result = CopyIf(input, [](const auto&) { return true; });
  ASSERT_TRUE(result.empty());
}

TEST(CopyIf, Filter) {
  const std::vector<int> input = {1, 2, 3, 4, 5};
  const auto result =
      CopyIf(input, [](const auto& value) { return value == 1 || value == 3; });
  const std::vector<int> expected = {1, 3};
  ASSERT_EQ(result, expected);
}

}  // namespace eats_catalog::utils
