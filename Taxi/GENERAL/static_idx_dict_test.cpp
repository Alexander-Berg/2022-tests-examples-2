#include <gtest/gtest.h>

#include <utils/static_idx_dict.hpp>

TEST(StaticIdxDict, One) {
  utils::StaticIdxDict dict({"one", "two", "three", "two"});
  ASSERT_EQ(3, dict.size());
  for (const auto& key : dict.GetKeys()) {
    uint16_t idx = 0;
    ASSERT_NO_THROW((idx = dict.GetIdx(key)));
    EXPECT_EQ(key, dict.GetKey(idx));
  }

  EXPECT_THROW(dict.GetIdx("ten"), std::out_of_range);
  EXPECT_THROW(dict.GetKey(10), std::out_of_range);
}
