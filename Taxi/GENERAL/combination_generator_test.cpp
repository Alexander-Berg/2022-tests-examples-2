#include <models/grocery/combination_generator.hpp>

#include <gtest/gtest.h>

#include <models/grocery/segment_combination_io.hpp>

using namespace ::models::grocery;

TEST(GrocerySegmentGeneratorTest, ZeroSegmentCount) {
  {
    CombinationGenerator generator{0, 5};
    const auto next = generator.Next();
    ASSERT_EQ(std::nullopt, next);
  }

  {
    CombinationGenerator generator{0, 5};
    generator.SkipBranch();
    const auto next = generator.Next();
    ASSERT_EQ(std::nullopt, next);
  }
}

TEST(GrocerySegmentGeneratorTest, SingleSegment) {
  {
    CombinationGenerator generator{1, 2};
    ASSERT_EQ(SegmentCombination{}.Push(0), generator.Next());
    ASSERT_EQ(std::nullopt, generator.Next());
  }

  {
    CombinationGenerator generator{1, 2};
    generator.SkipBranch();
    ASSERT_EQ(std::nullopt, generator.Next());
  }
}

TEST(GrocerySegmentGeneratorTest, FourSegments) {
  {
    CombinationGenerator generator{4, 5};
    ASSERT_EQ(SegmentCombination{}.Push(0), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(0).Push(1), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(0).Push(1).Push(2), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(0).Push(1).Push(2).Push(3),
              generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(0).Push(1).Push(3), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(0).Push(2), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(0).Push(2).Push(3), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(0).Push(3), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(1), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(1).Push(2), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(1).Push(2).Push(3), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(1).Push(3), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(2), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(2).Push(3), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(3), generator.Next());
    ASSERT_EQ(std::nullopt, generator.Next());
  }

  {
    CombinationGenerator generator{4, 5};
    generator.SkipBranch();
    ASSERT_EQ(SegmentCombination{}.Push(1), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(1).Push(2), generator.Next());
    generator.SkipBranch();
    ASSERT_EQ(SegmentCombination{}.Push(1).Push(3), generator.Next());
    ASSERT_EQ(SegmentCombination{}.Push(2), generator.Next());
    generator.SkipBranch();
    ASSERT_EQ(SegmentCombination{}.Push(3), generator.Next());
    ASSERT_EQ(std::nullopt, generator.Next());
  }
}

TEST(GrocerySegmentGeneratorTest, SkipBranchOnBranchEnd) {
  CombinationGenerator generator{3, 3};
  EXPECT_EQ(SegmentCombination{}.Push(0), generator.Next());
  EXPECT_EQ(SegmentCombination{}.Push(0).Push(1), generator.Next());
  EXPECT_EQ(SegmentCombination{}.Push(0).Push(1).Push(2), generator.Next());
  generator.SkipBranch();  // 0, 2
  generator.SkipBranch();  // 1
  generator.SkipBranch();  // 2
  ASSERT_EQ(SegmentCombination{}.Push(2), generator.Next());
}
