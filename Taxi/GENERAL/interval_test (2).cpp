#include <ostream>

#include <interval/interval.hpp>

#include <gtest/gtest.h>

struct EqualComparableClass {
  int value;

  explicit EqualComparableClass(int val) : value(val) {}

  bool operator==(const EqualComparableClass& other) const {
    return value == other.value;
  }
};

struct ComparableClass : EqualComparableClass {
  using EqualComparableClass::EqualComparableClass;

  bool operator<(const ComparableClass& other) const {
    return value < other.value;
  }
};

struct SimpleDifferenceClass : ComparableClass {
  using ComparableClass::ComparableClass;

  int operator-(const SimpleDifferenceClass& other) const {
    return value - other.value;
  }
};

struct DifferenceClass : ComparableClass {
  using ComparableClass::ComparableClass;

  DifferenceClass operator-(const DifferenceClass& other) const {
    return DifferenceClass(value - other.value);
  }
};

struct PrintableClass : ComparableClass {
  using ComparableClass::ComparableClass;

  friend std::ostream& operator<<(std::ostream& out,
                                  const PrintableClass& obj) {
    return out << obj.value;
  }
};

TEST(IntervalTest, Constructor) {
  interval::Interval<int> i1;
  EXPECT_EQ(i1.Min(), 0);
  EXPECT_EQ(i1.Max(), 0);

  interval::Interval<int> i2(1, 10);
  EXPECT_EQ(i2.Min(), 1);
  EXPECT_EQ(i2.Max(), 10);

  // can create and use except Distance method
  interval::Interval<ComparableClass> i3(SimpleDifferenceClass{1},
                                         SimpleDifferenceClass{10});
  EXPECT_EQ(i3.Min(), ComparableClass{1});
  EXPECT_EQ(i3.Max(), ComparableClass{10});

  interval::Interval<int> i4 = interval::MakeNormalizedInterval<int>(10, 1);
  EXPECT_EQ(i4.Min(), 1);
  EXPECT_EQ(i4.Max(), 10);

  interval::Interval<int> i5(1, 10);
  EXPECT_EQ(i5.Min(), 1);
  EXPECT_EQ(i5.Max(), 10);
}

TEST(IntervalTest, Constexpr) {
  constexpr interval::Interval<int> def;
  constexpr interval::Interval<int> ctr(1, 2);
  [[maybe_unused]] constexpr interval::Interval<int> fab =
      interval::MakeNormalizedInterval(10, 1);
  [[maybe_unused]] constexpr interval::Interval<int> mov = std::move(def);
  [[maybe_unused]] constexpr interval::Interval<int> cop = ctr;
  [[maybe_unused]] constexpr auto min = ctr.Min();
  [[maybe_unused]] constexpr auto max = ctr.Max();
  [[maybe_unused]] constexpr auto distance = ctr.Distance();
  [[maybe_unused]] constexpr auto contains = ctr.Contains(1);
  [[maybe_unused]] constexpr auto bound = ctr.Bound(0);
}

TEST(IntervalTest, Distance) {
  interval::Interval<int> i1(1, 10);
  EXPECT_EQ(i1.Distance(), 9);

  interval::Interval<SimpleDifferenceClass> i2(SimpleDifferenceClass{1},
                                               SimpleDifferenceClass{10});
  EXPECT_EQ(i2.Distance(), 9);

  interval::Interval<DifferenceClass> i3(DifferenceClass{1},
                                         DifferenceClass{10});
  EXPECT_EQ(i3.Distance(), DifferenceClass{9});
}

TEST(IntervalTest, Contains) {
  interval::Interval<int> i1(1, 10);
  EXPECT_EQ(i1.Contains(-1), false);
  EXPECT_EQ(i1.Contains(1), true);
  EXPECT_EQ(i1.Contains(5), true);
  EXPECT_EQ(i1.Contains(10), true);
  EXPECT_EQ(i1.Contains(11), false);

  interval::Interval<ComparableClass> i3(ComparableClass{1},
                                         ComparableClass{10});
  EXPECT_EQ(i3.Contains(ComparableClass{-1}), false);
  EXPECT_EQ(i3.Contains(ComparableClass{1}), true);
  EXPECT_EQ(i3.Contains(ComparableClass{5}), true);
  EXPECT_EQ(i3.Contains(ComparableClass{10}), true);
  EXPECT_EQ(i3.Contains(ComparableClass{11}), false);
}

TEST(IntervalTest, Bound) {
  interval::Interval<int> i3(1, 10);
  EXPECT_EQ(i3.Bound(-1), 1);
  EXPECT_EQ(i3.Bound(5), 5);
  EXPECT_EQ(i3.Bound(11), 10);
}

TEST(IntervalTest, CustomCompare) {
  auto compare = [](const EqualComparableClass& lhs,
                    const EqualComparableClass& rhs) {
    return lhs.value < rhs.value;
  };

  auto i1 = interval::Interval(EqualComparableClass{1},
                               EqualComparableClass{10}, compare);
  EXPECT_EQ(i1.Min(), EqualComparableClass{1});
  EXPECT_EQ(i1.Max(), EqualComparableClass{10});
  EXPECT_EQ(i1.Contains(EqualComparableClass{-1}), false);
  EXPECT_EQ(i1.Contains(EqualComparableClass{1}), true);
  EXPECT_EQ(i1.Contains(EqualComparableClass{5}), true);
  EXPECT_EQ(i1.Contains(EqualComparableClass{10}), true);
  EXPECT_EQ(i1.Contains(EqualComparableClass{11}), false);
  EXPECT_EQ(i1.Bound(EqualComparableClass{-1}), EqualComparableClass{1});
  EXPECT_EQ(i1.Bound(EqualComparableClass{5}), EqualComparableClass{5});
  EXPECT_EQ(i1.Bound(EqualComparableClass{11}), EqualComparableClass{10});
}

TEST(IntervalTest, ExceptionWithValues) {
  try {
    [[maybe_unused]] interval::Interval<int> i1(10, 1);
    FAIL() << "Shouldn't create denormalized interval";
  } catch (const interval::WrongBoundsIntervalError& ex) {
    EXPECT_STREQ(
        "Wrong interval bounds of type int: "
        "min (10) > max (1)",
        ex.what());
  } catch (const std::exception& ex) {
    FAIL() << "Unexpected exception " << ex.what();
  }
}

TEST(IntervalTest, ExceptionWithCustomValues) {
  try {
    [[maybe_unused]] interval::Interval<PrintableClass> i1(PrintableClass{10},
                                                           PrintableClass{1});
    FAIL() << "Shouldn't create denormalized interval";
  } catch (const interval::WrongBoundsIntervalError& ex) {
    EXPECT_STREQ(
        "Wrong interval bounds of type PrintableClass: "
        "min (10) > max (1)",
        ex.what());
  } catch (const std::exception& ex) {
    FAIL() << "Unexpected exception " << ex.what();
  }
}

TEST(IntervalTest, ExceptionWithoutValues) {
  try {
    [[maybe_unused]] interval::Interval<DifferenceClass> i1(DifferenceClass{10},
                                                            DifferenceClass{1});
    FAIL() << "Shouldn't create denormalized interval";
  } catch (const interval::WrongBoundsIntervalError& ex) {
    EXPECT_STREQ(
        "Wrong interval bounds of type DifferenceClass: "
        "min > max",
        ex.what());
  } catch (const std::exception& ex) {
    FAIL() << "Unexpected exception " << ex.what();
  }
}
