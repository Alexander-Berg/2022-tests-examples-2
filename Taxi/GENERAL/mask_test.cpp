#include <enums/mask.hpp>

#include <vector>

#include <gtest/gtest.h>

namespace tests {

enum Type { Undefined, Test0, Test1, Test2, kSize };
using Mask = enums::Mask<Type>;
const Mask kEachBitSet{Undefined, Test0, Test1, Test2};

void IsFull(const Mask& mask) {
  bool is_full = true;
  for (int i = 0; i < tests::kSize; i++) {
    if (!mask[static_cast<tests::Type>(i)]) {
      is_full = false;
      break;
    }
  }
  EXPECT_EQ(mask.IsFull(), is_full);
}

void IsEmpty(Mask mask) {
  bool is_empty = true;
  for (int i = 0; i < tests::kSize; i++) {
    if (mask[static_cast<tests::Type>(i)]) {
      is_empty = false;
      break;
    }
  }
  EXPECT_EQ(mask.IsEmpty(), is_empty);
}

void BracketOperator(Mask mask, std::vector<bool> vec) {
  for (size_t i = 0; i < vec.size(); i++) {
    EXPECT_EQ(mask[static_cast<tests::Type>(i)], vec[i]);
  }

  for (size_t i = 0; i < vec.size(); i++) {
    const auto b = static_cast<tests::Type>(i);
    mask[b] = !vec[i];
    for (size_t j = 0; j < vec.size(); j++) {
      const auto x = static_cast<tests::Type>(j);
      if (i == j) {
        EXPECT_EQ(mask[x], !vec[x]);
      } else {
        EXPECT_EQ(mask[x], vec[x]);
      }
    }
    mask[b] = vec[i];
  }
}

void CheckOne(Mask mask) {
  for (size_t i = 0; i < tests::kSize; i++) {
    const auto b = static_cast<tests::Type>(i);
    EXPECT_EQ(mask[b], mask.Check(b));
  }
}

void FlipOne(Mask mask) {
  Mask prev{mask};
  for (size_t i = 0; i < tests::kSize; i++) {
    const auto b = static_cast<tests::Type>(i);
    mask.Flip(b);
    EXPECT_EQ(mask[b], !prev[b]);
  }
}

void FlipAll(Mask mask) {
  Mask prev{mask};
  mask.Flip();
  for (size_t i = 0; i < tests::kSize; i++) {
    const auto b = static_cast<tests::Type>(i);
    EXPECT_EQ(mask[b], !prev[b]);
  }
}

void SetOne(Mask mask) {
  Mask prev{mask};
  for (size_t i = 0; i < tests::kSize; i++) {
    const auto b = static_cast<tests::Type>(i);
    mask.Set(b, !prev[b]);
    // All the rest values remains unchanged
    for (size_t j = 0; j < tests::kSize; j++) {
      const auto x = static_cast<tests::Type>(j);
      if (i == j) {
        EXPECT_EQ(mask[x], !prev[x]);
      } else {
        EXPECT_EQ(mask[x], prev[x]);
      }
    }
    mask.Set(b, prev[b]);
  }
}

void SetAll(Mask mask) {
  mask.Set();
  for (size_t i = 0; i < tests::kSize; i++) {
    const auto b = static_cast<tests::Type>(i);
    EXPECT_TRUE(mask[b]);
  }
}

void ClearOne(Mask mask) {
  Mask prev{mask};
  for (size_t i = 0; i < tests::kSize; i++) {
    const auto b = static_cast<tests::Type>(i);
    mask.Clear(b);
    // All the rest values remains unchanged
    for (size_t j = 0; j < tests::kSize; j++) {
      const auto x = static_cast<tests::Type>(j);
      if (i == j) {
        EXPECT_FALSE(mask[x]);
      } else {
        EXPECT_EQ(mask[x], prev[x]);
      }
    }
    mask.Set(b, prev[b]);
  }
}

void AndAssignment(Mask lhs, const Mask rhs) {
  Mask prev{lhs};
  lhs &= rhs;
  // Set lhs bit to 0 if corresponding rhs bit is 0, otherwise lhs bit remains
  // unchanged
  for (size_t i = 0; i < tests::kSize; i++) {
    const auto b = static_cast<tests::Type>(i);
    if (!rhs[b]) {
      EXPECT_FALSE(lhs[b]);
    } else {
      EXPECT_EQ(lhs[b], prev[b]);
    }
  }
}

void OrAssignment(Mask lhs, const Mask rhs) {
  Mask prev{lhs};
  lhs |= rhs;
  // Sets lhs bit to 1 if corresponding rhs bit is 1, otherwies lhs bit remains
  // unchanged
  for (size_t i = 0; i < tests::kSize; i++) {
    const auto b = static_cast<tests::Type>(i);
    if (rhs[b]) {
      EXPECT_TRUE(lhs[b]);
    } else {
      EXPECT_EQ(lhs[b], prev[b]);
    }
  }
}

void XorAssignment(Mask lhs, const Mask rhs) {
  Mask prev{lhs};
  lhs ^= rhs;
  // Sets lhs bit to 1 if corresponding previous lhs bit and rhs bit are
  // different, otherwise lhs bit set to 0
  for (size_t i = 0; i < tests::kSize; i++) {
    const auto b = static_cast<tests::Type>(i);
    EXPECT_EQ(lhs[b], prev[b] != rhs[b]);
  }
}

void AndOperator(Mask lhs, const Mask& rhs) {
  Mask mask{lhs};
  EXPECT_EQ((lhs &= rhs), (mask & rhs));
}

void OrOperator(Mask lhs, const Mask& rhs) {
  Mask mask{lhs};
  EXPECT_EQ((lhs |= rhs), (mask | rhs));
}

void XorOperator(Mask lhs, const Mask& rhs) {
  Mask mask{lhs};
  EXPECT_EQ((lhs ^= rhs), (mask ^ rhs));
}

void EqualOperator(const Mask& lhs, const Mask& rhs) {
  if (lhs == rhs) {
    for (size_t i = 0; i < tests::kSize; i++) {
      const auto b = static_cast<tests::Type>(i);
      EXPECT_EQ(lhs[b], rhs[b]);
    }
  } else {
    bool has_diff{false};
    for (size_t i = 0; i < tests::kSize; i++) {
      const auto b = static_cast<tests::Type>(i);
      if (lhs[b] != rhs[b]) {
        has_diff = true;
        break;
      }
    }
    EXPECT_TRUE(has_diff);
  }
}

void NotEqualOperator(const Mask& lhs, const Mask& rhs) {
  if (lhs != rhs) {
    bool has_diff{false};
    for (size_t i = 0; i < tests::kSize; i++) {
      const auto b = static_cast<tests::Type>(i);
      if (lhs[b] != rhs[b]) {
        has_diff = true;
        break;
      }
      EXPECT_TRUE(has_diff);
    }
  } else {
    for (size_t i = 0; i < tests::kSize; i++) {
      const auto b = static_cast<tests::Type>(i);
      EXPECT_EQ(lhs[b], rhs[b]);
    }
  }
}

void SkipClear(const Mask& mask) {
  size_t ones = 0;
  for (size_t i = 0; i < tests::kSize; i++) {
    if (mask[static_cast<tests::Type>(i)]) ones++;
  }
  for ([[maybe_unused]] const auto b : mask) {
    ones--;
  }
  EXPECT_EQ(ones, 0);
}

}  // namespace tests

TEST(Enum, IsFull) {
  tests::IsFull(tests::Mask{});
  tests::IsFull(tests::Mask{tests::Test2});
  tests::IsFull(tests::kEachBitSet);
}

TEST(Enum, IsEmpty) {
  tests::IsEmpty(tests::Mask{});
  tests::IsEmpty(tests::Mask{tests::Test2});
  tests::IsEmpty(tests::kEachBitSet);
}

TEST(Enum, BracketOperator) {
  using tests::BracketOperator;
  BracketOperator(tests::Mask{}, {0, 0, 0, 0});
  BracketOperator(tests::Mask{{tests::Test0, tests::Test1}}, {0, 1, 1, 0});
  BracketOperator(tests::Mask{tests::Test2}, {0, 0, 0, 1});
  BracketOperator(tests::kEachBitSet, {1, 1, 1, 1});
}

TEST(Enum, CheckOne) {
  tests::CheckOne(tests::Mask{});
  tests::CheckOne(tests::Mask{{tests::Undefined, tests::Test0}});
  tests::CheckOne(tests::Mask{tests::Test2});
  tests::CheckOne(tests::kEachBitSet);
}

TEST(Enum, FlipOne) {
  tests::FlipOne(tests::Mask{});
  tests::FlipOne(tests::Mask{{tests::Undefined, tests::Test0}});
  tests::FlipOne(tests::Mask{tests::Test2});
  tests::FlipOne(tests::kEachBitSet);
}

TEST(Enum, FlipAll) {
  tests::FlipAll(tests::Mask{});
  tests::FlipAll(tests::Mask{{tests::Undefined, tests::Test0}});
  tests::FlipAll(tests::Mask{tests::Test2});
  tests::FlipAll(tests::kEachBitSet);
}

TEST(Enum, SetOne) {
  tests::SetOne(tests::Mask{});
  tests::SetOne(tests::Mask{{tests::Undefined, tests::Test0}});
  tests::SetOne(tests::Mask{tests::Test2});
  tests::SetOne(tests::kEachBitSet);
}

TEST(Enum, SetAll) {
  tests::SetAll(tests::Mask{});
  tests::SetAll(tests::Mask{{tests::Undefined, tests::Test0}});
  tests::SetAll(tests::Mask{tests::Test2});
  tests::SetAll(tests::kEachBitSet);
}

TEST(Enum, ClearOne) {
  tests::ClearOne(tests::Mask{});
  tests::ClearOne(tests::Mask{{tests::Undefined, tests::Test0}});
  tests::ClearOne(tests::Mask{tests::Test2});
  tests::ClearOne(tests::kEachBitSet);
}

TEST(Enum, OrAssignment) {
  tests::OrAssignment(tests::Mask{}, tests::Mask{});
  tests::OrAssignment(tests::kEachBitSet, tests::Mask{});
  tests::OrAssignment(tests::Mask{}, tests::kEachBitSet);
  tests::OrAssignment(tests::Mask{}, tests::Mask{tests::Test0});
}

TEST(Enum, AndAssignment) {
  tests::AndAssignment(tests::Mask{}, tests::Mask{});
  tests::AndAssignment(tests::kEachBitSet, tests::Mask{});
  tests::AndAssignment(tests::Mask{}, tests::kEachBitSet);
  tests::AndAssignment(tests::Mask{}, tests::Mask{tests::Test0});
}

TEST(Enum, XorAssignment) {
  tests::XorAssignment(tests::Mask{}, tests::Mask{});
  tests::XorAssignment(tests::kEachBitSet, tests::Mask{});
  tests::XorAssignment(tests::Mask{}, tests::kEachBitSet);
  tests::XorAssignment(tests::Mask{}, tests::Mask{tests::Test0});
}

TEST(Enum, OrOperator) {
  tests::OrOperator(tests::Mask{}, tests::Mask{});
  tests::OrOperator(tests::kEachBitSet, tests::Mask{});
  tests::OrOperator(tests::Mask{}, tests::kEachBitSet);
  tests::OrOperator(tests::Mask{}, tests::Mask{tests::Test0});
}

TEST(Enum, AndOperator) {
  tests::AndOperator(tests::Mask{}, tests::Mask{});
  tests::AndOperator(tests::kEachBitSet, tests::Mask{});
  tests::AndOperator(tests::Mask{}, tests::kEachBitSet);
  tests::AndOperator(tests::Mask{}, tests::Mask{tests::Test0});
}

TEST(Enum, XorOperator) {
  tests::XorOperator(tests::Mask{}, tests::Mask{});
  tests::XorOperator(tests::kEachBitSet, tests::Mask{});
  tests::XorOperator(tests::Mask{}, tests::kEachBitSet);
  tests::XorOperator(tests::Mask{}, tests::Mask{tests::Test0});
}

TEST(Enum, Make) {
  constexpr tests::Mask cmask = tests::Mask::Make<tests::Test0, tests::Test1>();
  static_assert(cmask[tests::Test0] && cmask.Check<tests::Test0>());
  static_assert(cmask[tests::Test1] && cmask.Check<tests::Test1>());
  static_assert(!cmask[tests::Test2] && !cmask.Check<tests::Test2>());
  static_assert(!cmask[tests::Undefined] && !cmask.Check<tests::Undefined>());
}

TEST(Enum, SkipClear) {
  tests::SkipClear(tests::Mask{});
  tests::SkipClear(tests::Mask{{tests::Undefined, tests::Test0}});
  tests::SkipClear(tests::Mask{tests::Test2});
  tests::SkipClear(tests::kEachBitSet);
}
