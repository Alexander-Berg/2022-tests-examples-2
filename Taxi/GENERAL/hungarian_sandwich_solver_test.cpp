#include <memory>
#include <string>

#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <dispatch/planner.hpp>
#include <dispatch/proposition-builders/delivery.hpp>
#include <dispatch/proposition-builders/delivery/solver.hpp>
#include <dispatch/proposition-builders/delivery/solver/hungarian_sandwich_solver.hpp>

#include <models/candidates/candidate.hpp>
#include <models/united_dispatch/waybill_ref.hpp>

using SolverEdge = united_dispatch::waybill::delivery::solver::SolverEdge;

class HungarianSolverSolverTest : public ::testing::Test {
 protected:
  void SetUp() override {}
};

namespace handlers {
struct Dependencies final {};
}  // namespace handlers

UTEST_F(HungarianSolverSolverTest, DefaultSandwichAlgorithm) {
  united_dispatch::waybill::delivery::solver::HungarianSandwichSolver solver(
      handlers::Dependencies{}, 0.1);

  std::vector<SolverEdge> edges = {{"p-1", "c-1", 14, {"s-1"}},
                                   {"p-2", "c-2", 15, {"s-2"}},
                                   {"p-3", "c-3", 10, {"s-3"}},

                                   {"b-1", "c-1", 28, {"s-1", "s-2"}},
                                   {"b-2", "c-2", 27, {"s-2", "s-3"}},
                                   {"b-3", "c-4", 40, {"s-1", "s-2", "s-3"}}};
  united_dispatch::waybill::delivery::solver::HungarianSandwichSolverStats
      stats;
  std::vector<SolverEdge> output = solver.DoSolve(edges, stats);

  EXPECT_EQ(output.size(), 2);

  std::map<std::string, std::string> candidate_assigned_routes;
  for (const auto& edge : output) {
    candidate_assigned_routes[edge.candidate_id] = edge.route_id;
  }
  std::map<std::string, std::string> candidate_expected_routes = {
      {edges[0].candidate_id, edges[0].route_id},
      {edges[4].candidate_id, edges[4].route_id}};

  for (const auto& [candidate_id, expected_route_id] :
       candidate_expected_routes) {
    EXPECT_EQ(candidate_assigned_routes[candidate_id], expected_route_id);
  }
}

UTEST_F(HungarianSolverSolverTest, FullRatioSandwichAlgorithm) {
  united_dispatch::waybill::delivery::solver::HungarianSandwichSolver solver(
      handlers::Dependencies{}, 1.0);

  std::vector<SolverEdge> edges = {{"p-1", "c-1", 14, {"s-1"}},
                                   {"p-2", "c-2", 15, {"s-2"}},
                                   {"p-3", "c-3", 10, {"s-3"}},

                                   {"b-1", "c-1", 28, {"s-1", "s-2"}},
                                   {"b-2", "c-2", 27, {"s-2", "s-3"}},
                                   {"b-3", "c-4", 40, {"s-1", "s-2", "s-3"}}};
  united_dispatch::waybill::delivery::solver::HungarianSandwichSolverStats
      stats;
  std::vector<SolverEdge> output = solver.DoSolve(edges, stats);

  EXPECT_EQ(output.size(), 3);

  std::map<std::string, std::string> candidate_assigned_routes;
  for (const auto& edge : output) {
    candidate_assigned_routes[edge.candidate_id] = edge.route_id;
  }
  std::map<std::string, std::string> candidate_expected_routes = {
      {edges[0].candidate_id, edges[0].route_id},
      {edges[1].candidate_id, edges[1].route_id},
      {edges[2].candidate_id, edges[2].route_id},
  };

  for (const auto& [candidate_id, expected_route_id] :
       candidate_expected_routes) {
    EXPECT_EQ(candidate_assigned_routes[candidate_id], expected_route_id);
  }
}

UTEST_F(HungarianSolverSolverTest, SandwichZeroes) {
  united_dispatch::waybill::delivery::solver::HungarianSandwichSolver solver(
      handlers::Dependencies{}, 1.0);

  std::vector<SolverEdge> edges = {{"b-1", "c-1", 0, {"s-1", "s-2"}},
                                   {"b-2", "c-2", 0, {"s-3", "s-4"}},
                                   {"b-3", "c-4", 0, {"s-5", "s-6", "s-7"}}};
  united_dispatch::waybill::delivery::solver::HungarianSandwichSolverStats
      stats;
  std::vector<SolverEdge> output = solver.DoSolve(edges, stats);

  EXPECT_EQ(output.size(), 3);

  std::map<std::string, std::string> candidate_assigned_routes;
  for (const auto& edge : output) {
    candidate_assigned_routes[edge.candidate_id] = edge.route_id;
  }
  std::map<std::string, std::string> candidate_expected_routes = {
      {edges[0].candidate_id, edges[0].route_id},
      {edges[1].candidate_id, edges[1].route_id},
      {edges[2].candidate_id, edges[2].route_id},
  };

  for (const auto& [candidate_id, expected_route_id] :
       candidate_expected_routes) {
    EXPECT_EQ(candidate_assigned_routes[candidate_id], expected_route_id);
  }
}
