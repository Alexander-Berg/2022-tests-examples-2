#include <models/grocery/segment_combination.hpp>

#include <gtest/gtest.h>

#include <models/grocery/segment_combination_io.hpp>

using namespace ::models::grocery;

TEST(SegmentCombinationTest, PushSegmentBasic) {
  auto a = SegmentCombination{};
  auto b = a.Push(1);
  auto c = b.Push(2);
  auto d = c.Push(3);

  ASSERT_TRUE(a.Empty());
  ASSERT_FALSE(b.Empty());
  ASSERT_FALSE(c.Empty());
  ASSERT_FALSE(d.Empty());

  ASSERT_EQ(0, a.Size());
  ASSERT_EQ(1, b.Size());
  ASSERT_EQ(2, c.Size());
  ASSERT_EQ(3, d.Size());

  ASSERT_EQ(1, b.Front());
  ASSERT_EQ(1, c.Front());
  ASSERT_EQ(1, d.Front());

  ASSERT_EQ(1, b.Back());
  ASSERT_EQ(2, c.Back());
  ASSERT_EQ(3, d.Back());
}

TEST(SegmentCombinationTest, SegmentOrder) {
  auto a = SegmentCombination{}.Push(3).Push(2).Push(1);
  auto b = SegmentCombination{}.Push(2).Push(1).Push(3);
  auto c = SegmentCombination{}.Push(1).Push(2).Push(3);

  ASSERT_EQ(a, b);
  ASSERT_EQ(b, c);
  ASSERT_EQ(a, c);

  ASSERT_EQ(1, a.Front());
  ASSERT_EQ(1, b.Front());
  ASSERT_EQ(1, c.Front());

  ASSERT_EQ(3, a.Back());
  ASSERT_EQ(3, b.Back());
  ASSERT_EQ(3, c.Back());
}

TEST(SegmentCombinationTest, PushSegmentTwice) {
  auto c = SegmentCombination{}.Push(1).Push(3).Push(1);

  ASSERT_FALSE(c.Empty());
  ASSERT_EQ(2, c.Size());
  ASSERT_EQ(1, c.Front());
  ASSERT_EQ(3, c.Back());
}

TEST(SegmentCombinationTest, IsTaken) {
  TakenSegments taken{1, 3};
  auto a = SegmentCombination{}.Push(1).Push(2);
  auto b = SegmentCombination{}.Push(2).Push(3);
  auto c = SegmentCombination{}.Push(2).Push(4);

  ASSERT_FALSE(SegmentCombination{}.IsTaken(taken));
  ASSERT_TRUE(a.IsTaken(taken));
  ASSERT_TRUE(b.IsTaken(taken));
  ASSERT_FALSE(c.IsTaken(taken));
}
