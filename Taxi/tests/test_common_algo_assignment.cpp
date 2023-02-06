#include <gtest/gtest.h>
#include <ml/common/algo/assignment.hpp>

namespace {
ml::common::algo::AssignmentResult SolveAssignmentHungarian(
    std::vector<std::vector<double>> costs) {
  ml::common::algo::AssignmentHungarianSolver solver;
  ml::common::algo::AssignmentTask task(std::move(costs));
  return solver.Apply(task);
}
}  // namespace

TEST(CommonAlgoAssignment, case_infinity) {
  double inf = std::numeric_limits<double>::max();
  std::vector<std::vector<double>> costs = {
      {2, inf, 4}, {inf, inf, inf}, {1, inf, inf}};

  auto result = SolveAssignmentHungarian(costs);
  ASSERT_EQ(result.assignment[0], 2ul);
  ASSERT_EQ(result.assignment[1], 1ul);
  ASSERT_EQ(result.assignment[2], 0ul);
  ASSERT_DOUBLE_EQ(result.total_cost, inf);
}

TEST(CommonAlgoAssignment, case_1) {
  std::vector<std::vector<double>> costs = {{1, 2}, {3, 5}};

  auto result = SolveAssignmentHungarian(costs);
  ASSERT_EQ(result.assignment[0], 1ul);
  ASSERT_EQ(result.assignment[1], 0ul);
  ASSERT_DOUBLE_EQ(result.total_cost, 5);
}

TEST(CommonAlgoAssignment, case_2) {
  std::vector<std::vector<double>> costs = {{1, 6, 5}, {3, 10, 10}};

  auto result = SolveAssignmentHungarian(costs);
  ASSERT_EQ(result.assignment[0], 2ul);
  ASSERT_EQ(result.assignment[1], 0ul);
  ASSERT_DOUBLE_EQ(result.total_cost, 8);
}

TEST(CommonAlgoAssignment, case_3) {
  std::vector<std::vector<double>> costs = {
      {1, 6, 5}, {3, 10, 10}, {3, 12, 10}};

  auto result = SolveAssignmentHungarian(costs);
  ASSERT_EQ(result.assignment[0], 2ul);
  ASSERT_EQ(result.assignment[1], 1ul);
  ASSERT_EQ(result.assignment[2], 0ul);
  ASSERT_DOUBLE_EQ(result.total_cost, 18);
}

TEST(CommonAlgoAssignment, case_4) {
  std::vector<std::vector<double>> costs = {
      {1, 6, 5}, {3, 10, 10}, {5, 12, 10}};

  auto result = SolveAssignmentHungarian(costs);
  ASSERT_EQ(result.assignment[0], 1ul);
  ASSERT_EQ(result.assignment[1], 0ul);
  ASSERT_EQ(result.assignment[2], 2ul);
  ASSERT_DOUBLE_EQ(result.total_cost, 19);
}

TEST(CommonAlgoAssignment, case_brute_force) {
  std::vector<std::vector<double>> costs;
  for (size_t i = 0; i < 4; ++i) {
    std::vector<double> row;
    for (size_t j = 0; j < 10; ++j) {
      row.push_back((i * 13 + j * 17 + i * j * 3 + 19) % 100);
    }
    costs.push_back(std::move(row));
  }

  double best_sum = 1000000000;
  for (size_t i0 = 0; i0 < 10; ++i0) {
    for (size_t i1 = 0; i1 < 10; ++i1) {
      for (size_t i2 = 0; i2 < 10; ++i2) {
        for (size_t i3 = 0; i3 < 10; ++i3) {
          if (i0 == i1 || i0 == i2 || i0 == i3 || i1 == i2 || i1 == i3 ||
              i2 == i3) {
            continue;
          }
          auto sum = costs[0][i0] + costs[1][i1] + costs[2][i2] + costs[3][i3];
          if (sum < best_sum) {
            best_sum = sum;
          }
        }
      }
    }
  }

  auto result = SolveAssignmentHungarian(costs);
  ASSERT_DOUBLE_EQ(result.total_cost, best_sum);
}

TEST(CommonAlgoAssignment, case_brute_force_negative) {
  std::vector<std::vector<double>> costs;
  for (size_t i = 0; i < 4; ++i) {
    std::vector<double> row;
    for (size_t j = 0; j < 10; ++j) {
      row.push_back(static_cast<int>(i * 13 + j * 17 + i * j * 3 + 19) % 100 -
                    200);
    }
    costs.push_back(std::move(row));
  }

  double best_sum = 1000000000;
  for (size_t i0 = 0; i0 < 10; ++i0) {
    for (size_t i1 = 0; i1 < 10; ++i1) {
      for (size_t i2 = 0; i2 < 10; ++i2) {
        for (size_t i3 = 0; i3 < 10; ++i3) {
          if (i0 == i1 || i0 == i2 || i0 == i3 || i1 == i2 || i1 == i3 ||
              i2 == i3) {
            continue;
          }
          auto sum = costs[0][i0] + costs[1][i1] + costs[2][i2] + costs[3][i3];
          if (sum < best_sum) {
            best_sum = sum;
          }
        }
      }
    }
  }

  auto result = SolveAssignmentHungarian(costs);
  ASSERT_DOUBLE_EQ(result.total_cost, best_sum);
}
