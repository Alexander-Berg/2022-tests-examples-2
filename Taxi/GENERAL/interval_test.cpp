#include "interval.hpp"

#include <gtest/gtest.h>

struct ComparableOnlyClass {
  int value;

  explicit ComparableOnlyClass(int val) : value(val) {}

  bool operator<(const ComparableOnlyClass& o) const { return value < o.value; }
  bool operator==(const ComparableOnlyClass& o) const {
    return value == o.value;
  }

  friend std::ostream& operator<<(std::ostream& stream,
                                  const ComparableOnlyClass& coc) {
    stream << "<" << coc.value << ">";
    return stream;
  }
};

struct SimpleDifferenceClass : ComparableOnlyClass {
  explicit SimpleDifferenceClass(int val) : ComparableOnlyClass(val) {}

  int operator-(const SimpleDifferenceClass& o) const {
    return value - o.value;
  }
};

struct DifferenceClass : ComparableOnlyClass {
  explicit DifferenceClass(int val) : ComparableOnlyClass(val) {}

  DifferenceClass operator-(const DifferenceClass& o) const {
    return DifferenceClass(value - o.value);
  }
};

TEST(IntervalTest, Constructor) {
  utils::Interval<int> i1;
  EXPECT_EQ(i1.Min(), 0);
  EXPECT_EQ(i1.Max(), 0);

  utils::Interval<int> i2(1, 10);
  EXPECT_EQ(i2.Min(), 1);
  EXPECT_EQ(i2.Max(), 10);

  // can create and use except Distance method
  utils::Interval<ComparableOnlyClass, int> i3(SimpleDifferenceClass{1},
                                               SimpleDifferenceClass{10});
  EXPECT_EQ(i3.Min(), ComparableOnlyClass{1});
  EXPECT_EQ(i3.Max(), ComparableOnlyClass{10});

  EXPECT_THROW((utils::Interval<int>{10, 1}), utils::WrongBoundsIntervalError);

  auto i4 = utils::Interval<int>::NormalizeAndCreate(10, 1);
  EXPECT_EQ(i4.Min(), 1);
  EXPECT_EQ(i4.Max(), 10);

  auto i5 = utils::Interval<int>::NormalizeAndCreate(1, 10);
  EXPECT_EQ(i5.Min(), 1);
  EXPECT_EQ(i5.Max(), 10);
}

TEST(IntervalTest, Distance) {
  utils::Interval<int> i1(1, 10);
  EXPECT_EQ(i1.Distance(), 9);

  utils::Interval<SimpleDifferenceClass, int> i2(SimpleDifferenceClass{1},
                                                 SimpleDifferenceClass{10});
  EXPECT_EQ(i2.Distance(), 9);

  utils::Interval<DifferenceClass> i3(DifferenceClass{1}, DifferenceClass{10});
  EXPECT_EQ(i3.Distance(), DifferenceClass{9});
}

TEST(IntervalTest, Contains) {
  utils::Interval<int> i1(1, 10);
  EXPECT_EQ(i1.Contains(-1), false);
  EXPECT_EQ(i1.Contains(1), true);
  EXPECT_EQ(i1.Contains(5), true);
  EXPECT_EQ(i1.Contains(10), true);
  EXPECT_EQ(i1.Contains(11), false);

  utils::Interval<ComparableOnlyClass> i3(ComparableOnlyClass{1},
                                          ComparableOnlyClass{10});
  EXPECT_EQ(i3.Contains(ComparableOnlyClass{-1}), false);
  EXPECT_EQ(i3.Contains(ComparableOnlyClass{1}), true);
  EXPECT_EQ(i3.Contains(ComparableOnlyClass{5}), true);
  EXPECT_EQ(i3.Contains(ComparableOnlyClass{10}), true);
  EXPECT_EQ(i3.Contains(ComparableOnlyClass{11}), false);
}

TEST(IntervalTest, Bound) {
  utils::Interval<int> i3(1, 10);
  EXPECT_EQ(i3.Bound(-1), 1);
  EXPECT_EQ(i3.Bound(5), 5);
  EXPECT_EQ(i3.Bound(11), 10);
}
