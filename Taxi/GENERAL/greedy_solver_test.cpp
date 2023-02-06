#include <memory>
#include <string>

#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <dispatch/planner.hpp>
#include <dispatch/proposition-builders/delivery.hpp>
#include <dispatch/proposition-builders/delivery/solver.hpp>
#include <dispatch/proposition-builders/delivery/solver/greedy_solver.hpp>

#include <models/candidates/candidate.hpp>
#include <models/united_dispatch/waybill_ref.hpp>

using SolverEdge = united_dispatch::waybill::delivery::solver::SolverEdge;

class GreedySolverTest : public ::testing::Test {
 protected:
  void SetUp() override {}
};

namespace handlers {
struct Dependencies final {};
}  // namespace handlers

UTEST_F(GreedySolverTest, TotallyGreedyAlgorithm) {
  // The 'totally' greedy algorithm is expected to score routes
  // by (num segments DESC, score DESC) and assign

  // non-trivial routes with scores < 0 shouldn't be assigned
  united_dispatch::waybill::delivery::solver::GreedySolver solver(
      handlers::Dependencies{}, 0);

  // the largest batch, positive scores, must be assigned to candidate_1
  SolverEdge good_batch_3__1{"good-batch-3",
                             "candidate-1",
                             10,
                             {"segment-1", "segment-2", "segment-3"}};
  SolverEdge good_batch_3__2{"good-batch-3",
                             "candidate-2",
                             5,
                             {"segment-1", "segment-2", "segment-3"}};

  // also a large batch, but scores are negative, must be filtered
  SolverEdge bad_batch_3__1{"bad-batch-3",
                            "candidate-3",
                            -2,
                            {"segment-4", "segment-5", "segment-6"}};
  SolverEdge bad_batch_3__2{"bad-batch-3",
                            "candidate-4",
                            -1,
                            {"segment-4", "segment-5", "segment-6"}};

  // intersects with good_batch_3, should be ignored by the greedy algorithm
  // despite scores are higher
  SolverEdge intersection_batch_2__1{
      "intersection-batch-2", "candidate-1", 20, {"segment-3", "segment-7"}};
  SolverEdge intersection_batch_2__2{
      "intersection-batch-2", "candidate-2", 10, {"segment-3", "segment-7"}};

  // good batch of size 2, must be assigned to candidate_2
  SolverEdge good_batch_2__1{
      "good-batch-2", "candidate-1", 20, {"segment-4", "segment-5"}};
  SolverEdge good_batch_2__2{
      "good-batch-2", "candidate-2", 10, {"segment-4", "segment-5"}};
  SolverEdge good_batch_2__3{
      "good-batch-2", "candidate-3", 5, {"segment-4", "segment-5"}};

  // will be assigned to candidate_4 by a greedy assignment and to candidate_3
  // by hungarian algorithm
  SolverEdge batch_1_1__1{"batch-1-1", "candidate-1", 20, {"segment-6"}};
  SolverEdge batch_1_1__2{"batch-1-1", "candidate-2", 10, {"segment-6"}};
  SolverEdge batch_1_1__3{"batch-1-1", "candidate-3", 4, {"segment-6"}};
  SolverEdge batch_1_1__4{"batch-1-1", "candidate-4", 5, {"segment-6"}};

  // will be assigned to candidate_4 by a greedy assignment and to candidate_3
  // by hungarian algorithm
  SolverEdge batch_1_2__1{"batch-1-2", "candidate-1", 20, {"segment-7"}};
  SolverEdge batch_1_2__2{"batch-1-2", "candidate-2", 10, {"segment-7"}};
  SolverEdge batch_1_2__3{"batch-1-2", "candidate-3", 1, {"segment-7"}};
  SolverEdge batch_1_2__4{"batch-1-2", "candidate-4", 4, {"segment-7"}};

  // won't be assigned by either greedy or hungarian assignment, not enough
  // candidates
  SolverEdge batch_1_3__1{"batch-1-3", "candidate-1", 20, {"segment-8"}};
  SolverEdge batch_1_3__2{"batch-1-3", "candidate-2", 10, {"segment-8"}};
  SolverEdge batch_1_3__3{"batch-1-3", "candidate-3", 1, {"segment-8"}};
  SolverEdge batch_1_3__4{"batch-1-3", "candidate-4", 3, {"segment-8"}};

  std::vector<SolverEdge> edges = {good_batch_3__1,
                                   good_batch_3__2,
                                   bad_batch_3__1,
                                   bad_batch_3__2,
                                   intersection_batch_2__1,
                                   intersection_batch_2__2,
                                   good_batch_2__1,
                                   good_batch_2__2,
                                   good_batch_2__3,
                                   batch_1_1__1,
                                   batch_1_1__2,
                                   batch_1_1__3,
                                   batch_1_1__4,
                                   batch_1_2__1,
                                   batch_1_2__2,
                                   batch_1_2__3,
                                   batch_1_2__4,
                                   batch_1_3__1,
                                   batch_1_3__2,
                                   batch_1_3__3,
                                   batch_1_3__4};
  united_dispatch::waybill::delivery::solver::GreedySolverStats stats;
  std::vector<SolverEdge> output = solver.DoSolve(edges, stats);

  EXPECT_EQ(output.size(), 4);

  std::map<std::string, std::string> candidate_assigned_routes;
  for (const auto& edge : output) {
    candidate_assigned_routes[edge.candidate_id] = edge.route_id;
  }
  std::map<std::string, std::string> candidate_expected_routes = {
      {"candidate-1", "good-batch-3"},
      {"candidate-2", "good-batch-2"},
      {"candidate-3", "batch-1-1"},
      {"candidate-4", "batch-1-2"},
  };

  for (const auto& [candidate_id, expected_route_id] :
       candidate_expected_routes) {
    EXPECT_EQ(candidate_assigned_routes[candidate_id], expected_route_id);
  }
}
