#include "enum.hpp"

#include <vector>

#include <gtest/gtest.h>

namespace tests {
#define TEST_ENUM_MAP(XX) \
  XX(Test0, "test0")      \
  XX(Test1, "test1")      \
  XX(Test2, "test2")
ENUM_DECLARE(TEST_ENUM_MAP)
ENUM_DEFINE(TEST_ENUM_MAP)
ENUM_DECLARE_MASK(TEST_ENUM_MAP)
}  // namespace tests

TEST(Enum, Count) {
  EXPECT_EQ(4u, tests::Count());  // 3 + Undefined
}

TEST(Enum, Parse) {
  EXPECT_THROW(tests::Parse("notest"), std::out_of_range);

  EXPECT_EQ(tests::Test0, tests::Parse("test0"));
  EXPECT_EQ(tests::Test1, tests::Parse("test1"));
  EXPECT_EQ(tests::Test2, tests::Parse("test2"));
}

TEST(Enum, ToString) {
  EXPECT_THROW(tests::ToString(tests::Undefined), std::out_of_range);

  EXPECT_STREQ("test0", tests::ToString(tests::Test0).c_str());
  EXPECT_STREQ("test1", tests::ToString(tests::Test1).c_str());
  EXPECT_STREQ("test2", tests::ToString(tests::Test2).c_str());
}

TEST(Enum, Mask) {
  tests::Mask mask;

  EXPECT_TRUE(mask.IsEmpty());
  EXPECT_FALSE(mask.IsFull());
  EXPECT_FALSE(mask.Check());
  EXPECT_FALSE(mask);
  EXPECT_TRUE(!mask);
  EXPECT_STREQ(mask.ToString().data(), "0000");
  {
    size_t cnt = 0;
    for (auto i : mask) {
      std::ignore = i;
      ++cnt;
    }
    EXPECT_EQ(cnt, 0u);
  }
  tests::Mask empty_mask = mask;

  mask.Flip();
  EXPECT_FALSE(mask.IsEmpty());
  EXPECT_TRUE(mask.IsFull());
  EXPECT_TRUE(mask.Check());
  const tests::Mask full_mask = mask;

  std::vector<tests::Type> types;
  for (auto i : mask) {
    types.push_back(i);
  }
  std::vector<tests::Type> expected{tests::Undefined, tests::Test0,
                                    tests::Test1, tests::Test2};
  EXPECT_EQ(types, expected);

  for (auto i : types) {
    tests::Mask m1(i);
    EXPECT_FALSE(m1.IsEmpty());
    EXPECT_FALSE(m1.IsFull());
    EXPECT_TRUE(mask.Check());
    EXPECT_TRUE(mask.Check(i));
    EXPECT_TRUE(mask[i]);
    for (auto j : types) {
      if (i != j) {
        EXPECT_FALSE(m1.Check(j));
        EXPECT_FALSE(m1[j]);
      }
    }

    tests::Mask m2;
    m2 |= i;
    EXPECT_EQ(m1, m2);

    tests::Mask m3 = full_mask;
    m3.Drop(i);
    EXPECT_FALSE(m1.IsEmpty());
    EXPECT_FALSE(m1.IsFull());
    EXPECT_TRUE(mask.Check());
    EXPECT_FALSE(m3[i]);

    EXPECT_EQ(m3 | m1, full_mask);
    EXPECT_EQ(m3 | i, full_mask);
    EXPECT_EQ(i | m3, full_mask);
    EXPECT_EQ(m3 & m1, empty_mask);
    EXPECT_EQ(m3 & i, empty_mask);
    EXPECT_EQ(i & m3, empty_mask);
    EXPECT_TRUE(m3 | m1);
    EXPECT_TRUE(m3 | i);
    EXPECT_TRUE(i | m3);
    EXPECT_FALSE(m3 & m1);
    EXPECT_FALSE(m3 & i);
    EXPECT_FALSE(i & m3);

    tests::Mask m4 = full_mask;
    m4 &= m1;
    EXPECT_EQ(m1, m4);

    tests::Mask m5;
    m5[i] = true;
    EXPECT_TRUE(m5[i]);
    EXPECT_EQ(m5, m1);
    m5[i] = false;
    EXPECT_FALSE(m5[i]);
    EXPECT_EQ(m5, empty_mask);
  }

  tests::Mask some_mask{tests::Test0, tests::Test2};
  EXPECT_FALSE(some_mask.IsEmpty());
  EXPECT_FALSE(some_mask.IsFull());
  EXPECT_TRUE(some_mask.Check());
  EXPECT_FALSE(some_mask.Check(tests::Undefined));
  EXPECT_TRUE(some_mask.Check(tests::Test0));
  EXPECT_FALSE(some_mask.Check(tests::Test1));
  EXPECT_TRUE(some_mask.Check(tests::Test2));
  EXPECT_EQ(some_mask | full_mask, full_mask);
  EXPECT_EQ(some_mask & full_mask, some_mask);
  EXPECT_EQ(some_mask | empty_mask, some_mask);
  EXPECT_EQ(some_mask & empty_mask, empty_mask);

  tests::Mask flipped_mask = some_mask;
  flipped_mask.Flip();
  EXPECT_EQ(some_mask ^ full_mask, flipped_mask);
  EXPECT_EQ(some_mask ^ empty_mask, some_mask);

  types.clear();
  for (auto i : some_mask) types.push_back(i);
  expected = {tests::Test0, tests::Test2};
  EXPECT_EQ(types, expected);

  constexpr tests::Mask cmask = tests::Mask::Make<tests::Test0, tests::Test1>();
  static_assert(cmask[tests::Test0] && cmask.Check<tests::Test0>(), "oops1");
  static_assert(cmask[tests::Test1] && cmask.Check<tests::Test1>(), "oops2");
  static_assert(!cmask[tests::Test2] && !cmask.Check<tests::Test2>(), "oops2");
  static_assert(!cmask[tests::Undefined] && !cmask.Check<tests::Undefined>(),
                "oops2");

  EXPECT_THROW(tests::Mask{"00000"}, std::runtime_error);
  EXPECT_THROW(tests::Mask("000000", 5), std::runtime_error);

  tests::Mask mask_from_c_string{"0100"};
  EXPECT_TRUE(mask_from_c_string.Check(tests::Test1));

  tests::Mask mask_from_short_c_string{"10"};
  EXPECT_TRUE(mask_from_short_c_string.Check(tests::Test0));

  tests::Mask mask_from_c_string_with_len{"00100", 4};
  EXPECT_EQ(mask_from_c_string_with_len, mask_from_short_c_string);

  EXPECT_THROW(tests::Mask{std::string{"00000"}}, std::runtime_error);
  EXPECT_THROW(tests::Mask(std::string{"000000"}, 1, 5), std::runtime_error);

  tests::Mask mask_from_string{std::string{"1000"}};
  EXPECT_TRUE(mask_from_string.Check(tests::Test2));

  tests::Mask mask_from_short_string{std::string{"01"}};
  EXPECT_TRUE(mask_from_short_string.Check(tests::Undefined));

  tests::Mask mask_from_string_with_len{std::string{"00010"}, 0, 4};
  EXPECT_EQ(mask_from_string_with_len, mask_from_short_string);
}
