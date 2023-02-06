#include <gtest/gtest-printers.h>
#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

#include <utils/sliding_windows.hpp>

bool TestDoubleEqVector(const std::vector<double>& expected,
                        const std::vector<double>& test) {
  const double kEpsilon = 1e-9;
  if (expected.size() != test.size()) {
    std::cerr << "vector sizes don't match, expected: " << expected.size()
              << ", test: " << test.size() << std::endl;
    return false;
  }
  for (size_t i = 0; i < expected.size(); ++i) {
    if (std::abs(expected[i] - test[i]) > kEpsilon) {
      std::cerr << "vector mismatch, expected: "
                << testing::PrintToString(expected)
                << ", test: " << testing::PrintToString(test) << std::endl;
      return false;
    }
  }

  return true;
}

namespace hejmdal::utils {

TEST(TestSlidingWindows, SimpleTest) {
  SlidingWindows sw({{time::Milliseconds(1000), 10},
                     {time::Milliseconds(2000), 20},
                     {time::Milliseconds(1000), 10}});

  EXPECT_EQ(0, sw.GetWindowSize(0));
  EXPECT_EQ(0, sw.GetWindowSize(1));
  EXPECT_EQ(0, sw.GetWindowSize(2));

  time::TimePoint current_time = time::From<time::Milliseconds>(10000);

  sw.PushData(1.0, current_time);

  bool expected_true = false;

  expected_true = (TestDoubleEqVector({1.0}, sw.GetValuesFromWindow(0)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({}, sw.GetValuesFromWindow(1)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({}, sw.GetValuesFromWindow(2)));
  EXPECT_TRUE(expected_true);

  current_time += time::Milliseconds(100);
  sw.PushData(2.0, current_time);
  expected_true = (TestDoubleEqVector({1.0, 2.0}, sw.GetValuesFromWindow(0)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({}, sw.GetValuesFromWindow(1)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({}, sw.GetValuesFromWindow(2)));
  EXPECT_TRUE(expected_true);

  current_time += time::Milliseconds(950);
  sw.PushData(3.0, current_time);
  expected_true = (TestDoubleEqVector({2.0, 3.0}, sw.GetValuesFromWindow(0)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({1.0}, sw.GetValuesFromWindow(1)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({}, sw.GetValuesFromWindow(2)));
  EXPECT_TRUE(expected_true);

  current_time += time::Milliseconds(1000);
  sw.PushData(4.0, current_time);
  expected_true = (TestDoubleEqVector({4.0}, sw.GetValuesFromWindow(0)));
  EXPECT_TRUE(expected_true);
  expected_true =
      (TestDoubleEqVector({1.0, 2.0, 3.0}, sw.GetValuesFromWindow(1)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({}, sw.GetValuesFromWindow(2)));
  EXPECT_TRUE(expected_true);

  current_time += time::Milliseconds(1000);
  sw.PushData(5.0, current_time);
  expected_true = (TestDoubleEqVector({5.0}, sw.GetValuesFromWindow(0)));
  EXPECT_TRUE(expected_true);
  expected_true =
      (TestDoubleEqVector({2.0, 3.0, 4.0}, sw.GetValuesFromWindow(1)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({1.0}, sw.GetValuesFromWindow(2)));
  EXPECT_TRUE(expected_true);

  current_time += time::Milliseconds(1000);
  sw.PushData(6.0, current_time);
  expected_true = (TestDoubleEqVector({6.0}, sw.GetValuesFromWindow(0)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({4.0, 5.0}, sw.GetValuesFromWindow(1)));
  EXPECT_TRUE(expected_true);
  expected_true = (TestDoubleEqVector({2.0, 3.0}, sw.GetValuesFromWindow(2)));
  EXPECT_TRUE(expected_true);
}

}  // namespace hejmdal::utils
