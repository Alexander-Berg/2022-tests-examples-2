#include "lerp_func.hpp"

#include <gtest/gtest.h>
#include <vector>

TEST(LinearApproxFunc, FuncCalcTest) {
  using ListOfVectors = std::initializer_list<std::vector<double>>;

  utils::interpolation::LerpFunc<double, double> func(1);
  ASSERT_DOUBLE_EQ(1, func.Calc(12.3));

  const ListOfVectors points = {{8, 16}, {2, 10}, {11, 18}, {6, 4}};
  std::map<double, double> expected_values;
  for (const auto& point : points) {
    func.AddValue(point[0], point[1]);
    expected_values[point[0]] = point[1];
  }

  ASSERT_EQ(expected_values, func.GetAllValues());

  const ListOfVectors expected_res = {
      {-3, 10}, {1.5, 10}, {2, 10}, {3, 8.5},  {4, 7},   {6, 4},
      {7, 10},  {7.5, 13}, {8, 16}, {9.5, 17}, {11, 18}, {1000, 18}};
  for (const auto& expected : expected_res) {
    ASSERT_DOUBLE_EQ(expected[1], func.Calc(expected[0]));
  }
}
