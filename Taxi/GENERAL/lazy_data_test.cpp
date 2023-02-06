#include <gtest/gtest.h>

#include <discounts/models/lazy_data.hpp>

TEST(LazyData, Get) {
  const auto kTestString = "test";
  size_t call_count = 0;
  discounts::models::LazyData<std::string> lazy_data{
      [&kTestString, &call_count]() -> std::optional<std::string> {
        ++call_count;
        return kTestString;
      }};
  ASSERT_EQ(call_count, 0);
  ASSERT_EQ(lazy_data.Get(), kTestString);
  ASSERT_EQ(call_count, 1);
  ASSERT_EQ(lazy_data.Get(), kTestString);
  ASSERT_EQ(call_count, 1);
}
