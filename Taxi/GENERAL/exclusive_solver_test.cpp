#include <memory>
#include <optional>
#include <string>
#include <unordered_map>
#include <userver/utest/utest.hpp>
#include <utility>
#include <vector>

#include <dispatch/proposition-builders/delivery.hpp>
#include <dispatch/proposition-builders/delivery/route.hpp>
#include <models/united_dispatch/segment.hpp>

#include <handlers/dependencies_fwd.hpp>

#include <dispatch/planner.hpp>
#include <dispatch/proposition-builders/delivery/solver.hpp>
#include <dispatch/proposition-builders/delivery/solver/exclusive_solver.hpp>
#include <models/candidates/candidate.hpp>
#include <models/united_dispatch/waybill_ref.hpp>

using SolverEdge = united_dispatch::waybill::delivery::solver::SolverEdge;

using ExclusiveSolver =
    united_dispatch::waybill::delivery::solver::ExclusiveSolver;

using ExclusiveSolverStats =
    united_dispatch::waybill::delivery::solver::ExclusiveSolverStats;
using Proposition = united_dispatch::waybill::delivery::solver::Proposition;

// Пока что это калька с GreedySolverTest
class ExclusiveSolverTest : public ::testing::Test {
 protected:
  united_dispatch::models::WaybillRefGeneratorPtr waybill_ref_generator_;

  void SetUp() override {}
};

namespace handlers {
struct Dependencies final {};
}  // namespace handlers

UTEST_F(ExclusiveSolverTest, CommonExclusiveAlgorithm) {
  // Проверка общего случая, когда батчи весомее
  SolverEdge single_1{"single_1", "candidate-1", 3, {"segment-1"}};

  SolverEdge single_2{"single_2", "candidate-1", 4, {"segment-2"}};

  SolverEdge single_3{"single_3", "candidate-2", 8, {"segment-3"}};

  SolverEdge single_4__1{"single_4", "candidate-2", 5, {"segment-4"}};
  SolverEdge single_4__2{"single_4", "candidate-3", 4, {"segment-4"}};

  SolverEdge single_5{"single_5", "candidate-3", 2, {"segment-5"}};

  SolverEdge single_6{"single_6", "candidate-3", 1, {"segment-6"}};

  SolverEdge batch_1_2_3{"batch_1_2_3",
                         "candidate-1",
                         10,
                         {"segment-1", "segment-2", "segment-3"}};

  SolverEdge batch_3_4{
      "batch_3_4", "candidate-2", 6, {"segment-3", "segment-4"}};

  SolverEdge batch_1_5{
      "batch_1_5", "candidate-3", 3, {"segment-1", "segment-5"}};

  std::vector<SolverEdge> routes{single_1,    single_2, single_3, single_4__1,
                                 single_4__2, single_5, single_6, batch_1_2_3,
                                 batch_3_4,   batch_1_5};

  ExclusiveSolverStats stats;
  ExclusiveSolver solver(handlers::Dependencies{});

  std::vector<SolverEdge> output = solver.DoSolve(routes, stats);

  // Comparing
  EXPECT_EQ(output.size(), 3);

  std::map<std::string, std::string> candidate_assigned_route;
  for (const auto& edge : output) {
    candidate_assigned_route[edge.candidate_id] = edge.route_id;
  }

  std::map<std::string, std::string> candidate_expected_route = {
      {"candidate-1", batch_1_2_3.route_id},
      {"candidate-2", single_4__1.route_id},
      {"candidate-3", single_5.route_id},
  };

  for (const auto& [candidate_id, expected_route_id] :
       candidate_expected_route) {
    EXPECT_EQ(candidate_assigned_route[candidate_id], expected_route_id);
  }
}
