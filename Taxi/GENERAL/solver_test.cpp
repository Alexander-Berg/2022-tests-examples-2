#include <vector>

#include <userver/utest/utest.hpp>

#include <dispatch/proposition-builders/delivery/solver.hpp>

using SolverEdge = united_dispatch::waybill::delivery::solver::SolverEdge;
using united_dispatch::waybill::delivery::solver::ShiftScoresToNonNegative;

UTEST(ShiftScoresToNonNegativeTest, MultipleEdges) {
  std::vector<SolverEdge> edges;
  SolverEdge edge{};
  edge.score = 11;
  edges.emplace_back(edge);
  edge.score = -5;
  edges.emplace_back(edge);
  edge.score = 12;
  edges.emplace_back(edge);
  ShiftScoresToNonNegative(edges, 2);
  EXPECT_EQ(edges[0].score, 18);
  EXPECT_EQ(edges[1].score, 2);
  EXPECT_EQ(edges[2].score, 19);
}

UTEST(ShiftScoresToNonNegativeTest, NoEdges) {
  std::vector<SolverEdge> edges;
  ShiftScoresToNonNegative(edges, 228);
  EXPECT_TRUE(edges.empty());
}
