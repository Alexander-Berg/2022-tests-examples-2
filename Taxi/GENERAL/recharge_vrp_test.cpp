#include <gtest/gtest.h>

#include <algorithms/recharge_vrp.hpp>
#include <models/models.hpp>
#include <models/recharge_graph.hpp>

namespace scooters_ops_dispatch::algorithms {

namespace {

const double kEpsilon = 1e-6;

models::Contractor BuildDefaultContractor(const std::string& id) {
  models::Contractor contractor;
  contractor.id = id;
  contractor.vehicle_type = models::VehicleType::kScooter;
  contractor.capacity = 6;
  return contractor;
}

models::AggregatedCabinets BuildDefaultCabinets(int accums) {
  models::AggregatedCabinets cabinets;
  cabinets.Put(models::CabinetType::kCabinet, accums);
  cabinets.Put(models::CabinetType::kChargeStation, 0);
  return cabinets;
}

models::RechargeDepotSettings BuildDefaultRechargeDepotSettings() {
  models::RechargeDepotSettings settings;
  return settings;
}

models::RechargeDepot BuildDefaultDepot(const std::string& id) {
  models::RechargeDepot depot;
  depot.id = id;
  depot.cabinets = BuildDefaultCabinets(100);
  depot.settings = BuildDefaultRechargeDepotSettings();
  return depot;
}

models::Scooter BuildDefaultScooter(const std::string& id) {
  models::Scooter scooter;
  scooter.id = id;
  scooter.draft_id = "draft_for_" + id;
  scooter.need_tackle = false;
  return scooter;
}

models::Edge BuildDefaultEdge(size_t idx, int time) {
  return models::Edge{idx, (double)time * 4.0, std::chrono::seconds(time),
                      (double)time, models::VehicleType::kScooter};
}

models::RechargeGraph BuildDefaultGraph() {
  const size_t kScootersNumber = 5;

  std::vector<models::Contractor> contractors{
      BuildDefaultContractor("contractor_0")};
  std::vector<models::RechargeDepot> depots{BuildDefaultDepot("depot_0")};

  std::vector<models::Scooter> scooters;
  for (size_t i = 0; i < kScootersNumber; i++) {
    scooters.emplace_back(BuildDefaultScooter("scooter_" + std::to_string(i)));
  }

  // NOTE: time for reverse edges equals time for direct edges + 1 sec
  // it might be useful to prevent errors with non-symmetric weights

  contractors[0].edges_to_depots.emplace_back(BuildDefaultEdge(0, 100));

  depots[0].edges_to_scooters.emplace_back(BuildDefaultEdge(0, 100));
  scooters[0].edges_to_depots.emplace_back(BuildDefaultEdge(0, 101));

  depots[0].edges_to_scooters.emplace_back(BuildDefaultEdge(1, 150));
  scooters[1].edges_to_depots.emplace_back(BuildDefaultEdge(0, 151));

  depots[0].edges_to_scooters.emplace_back(BuildDefaultEdge(2, 200));
  scooters[2].edges_to_depots.emplace_back(BuildDefaultEdge(0, 201));

  depots[0].edges_to_scooters.emplace_back(BuildDefaultEdge(3, 450));
  scooters[3].edges_to_depots.emplace_back(BuildDefaultEdge(0, 451));

  depots[0].edges_to_scooters.emplace_back(BuildDefaultEdge(4, 150));
  scooters[4].edges_to_depots.emplace_back(BuildDefaultEdge(0, 151));

  std::vector<std::vector<int>> matrix{
      std::vector<int>{-1, 100, 250, 500, 250},
      std::vector<int>{101, -1, 150, 400, 200},
      std::vector<int>{251, 501, -1, 250, 150},
      std::vector<int>{501, 401, 251, -1, 300},
      std::vector<int>{251, 201, 151, 301, -1}};

  /* ALL MATRIX:
    contractor -> depot: 100
      0, 100, 150, 200, 450, 150
      101, 0, 100, 250, 500, 250
      151, 101, 0, 150, 400, 200
      201, 251, 501, 0, 250, 150
      451, 501, 401, 251, 0, 300
      151, 251, 201, 151, 301, 0
  */

  for (size_t i = 0; i < kScootersNumber; i++) {
    for (size_t j = 0; j < kScootersNumber; j++) {
      if (matrix[i][j] != -1) {
        scooters[i].edges_to_scooters.emplace_back(
            BuildDefaultEdge(j, matrix[i][j]));
      }
    }
  }

  models::RechargeGraph graph;
  graph.contractors = std::move(contractors);
  graph.scooters = std::move(scooters);
  graph.depots = std::move(depots);

  return graph;
}

}  // namespace

using sec = std::chrono::seconds;
// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple) {
  const auto graph = BuildDefaultGraph();
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 3, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{250}, sec{300}, sec{151}},
      sec(1151),
      1151.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 3 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_DecreasedCapacity) {
  auto graph = BuildDefaultGraph();
  graph.contractors[0].capacity = 3;
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{
      RechargeMission{0,
                      0,
                      0,
                      {0, 1, 2},
                      {sec{100}, sec{100}, sec{100}, sec{150}, sec{201}},
                      sec(651),
                      651 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 3 accums, 5 scooters
TEST(TestRechargeVrp, Simple_NotEnoughAccums) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].cabinets = BuildDefaultCabinets(3);
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{
      RechargeMission{0,
                      0,
                      0,
                      {0, 1, 2},
                      {sec{100}, sec{100}, sec{100}, sec{150}, sec{201}},
                      sec(651),
                      651 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity and min_load 5, 1 depot with 100 accums, 5
// scooters
TEST(TestRechargeVrp, Simple_MinLoadOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].settings.min_load_from_capacity[6] = 5;
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 3, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{250}, sec{300}, sec{151}},
      sec(1151),
      1151.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity and min_load 6, 1 depot with 100 accums, 5
// scooters
TEST(TestRechargeVrp, Simple_MinLoadNotOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].settings.min_load_from_capacity[6] = 6;
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_MaxTimePerMissionOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].settings.max_time_per_mission = sec(1151);
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 3, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{250}, sec{300}, sec{151}},
      sec(1151),
      1151.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_MaxTimePerMissionNotOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].settings.max_time_per_mission = sec(1151 - 1);
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{150}, sec{151}},
      sec(751),
      751.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_MaxDistancePerMissionOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].settings.max_distance_per_mission = 1151.0 * 4.0 + kEpsilon;
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 3, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{250}, sec{300}, sec{151}},
      sec(1151),
      1151.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_MaxDistancePerMissionNotOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].settings.max_distance_per_mission = 1151.0 * 4.0 - kEpsilon;
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{150}, sec{151}},
      sec(751),
      751.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_TimeUntilClosingOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].time_until_closing = sec(1151);
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 3, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{250}, sec{300}, sec{151}},
      sec(1151),
      1151.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_TimeUntilClosingNotOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].time_until_closing = sec(1151 - 1);
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{150}, sec{151}},
      sec(751),
      751.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_TimeUntilEndOfShiftOK) {
  auto graph = BuildDefaultGraph();
  graph.contractors[0].time_until_end_of_shift = sec(1151);
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 3, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{250}, sec{300}, sec{151}},
      sec(1151),
      1151.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_TimeUntilEndOfShiftNotOK) {
  auto graph = BuildDefaultGraph();
  graph.contractors[0].time_until_end_of_shift = sec(1151 - 1);
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{150}, sec{151}},
      sec(751),
      751.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_BrokenEdgesToDepot) {
  auto graph = BuildDefaultGraph();
  graph.scooters[0].edges_to_depots.clear();
  graph.scooters[1].edges_to_depots.clear();
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_BrokenEdgesToScooters) {
  auto graph = BuildDefaultGraph();
  graph.scooters[4].edges_to_scooters.clear();
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 2 contractors with 3 and 6 capacity, 1 depot with 100 accums, 5 scooters
// second contractor closer than first
TEST(TestRechargeVrp, Simple_TwoContractors) {
  auto graph = BuildDefaultGraph();
  graph.contractors.emplace_back(BuildDefaultContractor("contractor_1"));
  auto& new_contractor = graph.contractors.back();
  new_contractor.capacity = 3;
  new_contractor.edges_to_depots.emplace_back(BuildDefaultEdge(0, 50));

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{
      RechargeMission{1,
                      0,
                      0,
                      {0, 1, 2},
                      {sec{50}, sec{100}, sec{100}, sec{150}, sec{201}},
                      sec(601),
                      601 * 4.0},
      RechargeMission{0,
                      0,
                      0,
                      {3, 4},
                      {sec{100}, sec{450}, sec{300}, sec{151}},
                      sec(1001),
                      1001 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 2 contractors with 6 capacity, 2 depot with 100 accums, 6 scooters
// second contractor priority than first, but have another depot
TEST(TestRechargeVrp, Simple_TwoContractorsAndTwoDepots) {
  auto graph = BuildDefaultGraph();

  graph.contractors.emplace_back(BuildDefaultContractor("contractor_1"));
  auto& new_contractor = graph.contractors.back();

  graph.depots.emplace_back(BuildDefaultDepot("depot_1"));
  auto& new_depot = graph.depots.back();

  graph.scooters.emplace_back(BuildDefaultScooter("scooter_5"));
  auto& new_scooter = graph.scooters.back();

  new_contractor.edges_to_depots.emplace_back(BuildDefaultEdge(0, 50));
  new_contractor.edges_to_depots.emplace_back(BuildDefaultEdge(1, 10));

  new_depot.edges_to_scooters.emplace_back(BuildDefaultEdge(5, 20));

  new_scooter.edges_to_depots.emplace_back(BuildDefaultEdge(1, 30));

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{
      RechargeMission{
          1, 1, 1, {5}, {sec{10}, sec{20}, sec{30}}, sec(60), 60 * 4.0},
      RechargeMission{0,
                      0,
                      0,
                      {0, 1, 2, 3, 4},
                      {sec{100}, sec{100}, sec{100}, sec{150}, sec{250},
                       sec{300}, sec{151}},
                      sec(1151),
                      1151.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 2 contractors with 3 and 6 capacity, 2 depots with 100 accums, 5 scooters
// different depots for different contractors but same set of scooters
TEST(TestRechargeVrp, Simple_CommonScooters) {
  auto graph = BuildDefaultGraph();

  graph.contractors.emplace_back(BuildDefaultContractor("contractor_1"));
  auto& new_contractor = graph.contractors.back();

  graph.depots.emplace_back(BuildDefaultDepot("depot_1"));
  auto& new_depot = graph.depots.back();

  new_contractor.capacity = 3;
  new_contractor.edges_to_depots.emplace_back(BuildDefaultEdge(1, 50));

  new_depot.edges_to_scooters = graph.depots[0].edges_to_scooters;

  for (auto& scooter : graph.scooters) {
    scooter.edges_to_depots.emplace_back(scooter.edges_to_depots.back());
    scooter.edges_to_depots.back().dst_idx = 1;
  }

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{
      RechargeMission{1,
                      1,
                      1,
                      {0, 1, 2},
                      {sec{50}, sec{100}, sec{100}, sec{150}, sec{201}},
                      sec(601),
                      601 * 4.0},
      RechargeMission{0,
                      0,
                      0,
                      {3, 4},
                      {sec{100}, sec{450}, sec{300}, sec{151}},
                      sec(1001),
                      1001 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_UnsuitableContractorVehicleType) {
  auto graph = BuildDefaultGraph();
  graph.contractors.front().vehicle_type = models::VehicleType::kCar;
  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_EdgesWithDifferentVehicleType) {
  auto graph = BuildDefaultGraph();

  auto DuplicateEdges = [](std::vector<models::Edge>& edges) -> void {
    for (size_t i = 0, max_i = edges.size(); i < max_i; i++) {
      auto copy = edges[i];
      copy.vehicle_type = models::VehicleType::kCar;
      copy.time = sec(1);
      copy.weight = 1.0;
      copy.distance = 1.0;
      edges.emplace_back(std::move(copy));
    }
  };

  DuplicateEdges(graph.contractors.front().edges_to_depots);
  DuplicateEdges(graph.depots.front().edges_to_scooters);
  for (auto& scooter : graph.scooters) {
    DuplicateEdges(scooter.edges_to_depots);
    DuplicateEdges(scooter.edges_to_scooters);
  }

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 3, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{250}, sec{300}, sec{151}},
      sec(1151),
      1151.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_AllEdgesForCars) {
  auto graph = BuildDefaultGraph();

  auto ChangeVehicleTypeToCar = [](std::vector<models::Edge>& edges) -> void {
    for (auto& edge : edges) {
      edge.vehicle_type = models::VehicleType::kCar;
    }
  };

  ChangeVehicleTypeToCar(graph.contractors.front().edges_to_depots);
  ChangeVehicleTypeToCar(graph.depots.front().edges_to_scooters);
  for (auto& scooter : graph.scooters) {
    ChangeVehicleTypeToCar(scooter.edges_to_depots);
    ChangeVehicleTypeToCar(scooter.edges_to_scooters);
  }

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_ContractorAndAllEdgesForCars) {
  auto graph = BuildDefaultGraph();

  auto ChangeVehicleTypeToCar = [](std::vector<models::Edge>& edges) -> void {
    for (auto& edge : edges) {
      edge.vehicle_type = models::VehicleType::kCar;
    }
  };

  ChangeVehicleTypeToCar(graph.contractors.front().edges_to_depots);
  ChangeVehicleTypeToCar(graph.depots.front().edges_to_scooters);
  for (auto& scooter : graph.scooters) {
    ChangeVehicleTypeToCar(scooter.edges_to_depots);
    ChangeVehicleTypeToCar(scooter.edges_to_scooters);
  }

  graph.contractors.front().vehicle_type = models::VehicleType::kCar;

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{RechargeMission{
      0,
      0,
      0,
      {0, 1, 2, 3, 4},
      {sec{100}, sec{100}, sec{100}, sec{150}, sec{250}, sec{300}, sec{151}},
      sec(1151),
      1151.0 * 4.0}};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 3 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_BonusForLowChargeLevel) {
  auto graph = BuildDefaultGraph();
  graph.contractors[0].capacity = 3;

  /* ALL MATRIX:
    contractor -> depot: 100
      0, 100, 150, 200, 450, 150
      101, 0, 100, 250, 500, 250
      151, 101, 0, 150, 400, 200
      201, 251, 501, 0, 250, 150
      451, 501, 401, 251, 0, 300
      151, 251, 201, 151, 301, 0
  */

  graph.scooters.at(2).charge_level = 10;
  graph.scooters.at(3).charge_level = 10;
  graph.scooters.at(4).charge_level = 10;

  std::unordered_map<std::string, int> bonus_for_charge_level_map;
  bonus_for_charge_level_map["10"] = 1000;

  graph.depots.at(0).settings.bonus_for_charge_level =
      models::BonusForChargeLevel(bonus_for_charge_level_map);

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{
      RechargeMission{0,
                      0,
                      0,
                      {2, 3, 4},
                      {sec{100}, sec{200}, sec{250}, sec{300}, sec{151}},
                      sec(1001),
                      1001 * 4.0}};

  /*
  std::cerr << "contractor_idx: " << solution.missions.back().contractor_idx
            << std::endl;
  std::cerr << "src_depot_idx: " << solution.missions.back().src_depot_idx
            << std::endl;
  std::cerr << "dst_depot_idx: " << solution.missions.back().dst_depot_idx
            << std::endl;

  std::cerr << "taken_scooters:";
  for (auto e : solution.missions.back().taken_scooters_idx)
    std::cerr << " " << e;
  std::cerr << std::endl;

  std::cerr << "moving_times:";
  for (auto e : solution.missions.back().moving_times)
    std::cerr << " " << e.count();
  std::cerr << std::endl;

  std::cerr << "time: " << solution.missions.back().time.count() << std::endl;
  std::cerr << "distance: " << solution.missions.back().distance << std::endl;
  */

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 3 capacity, 1 depot with 100 accums, 5 scooters
TEST(TestRechargeVrp, Simple_FineForLowChargeLevel) {
  auto graph = BuildDefaultGraph();
  graph.contractors[0].capacity = 3;

  /* ALL MATRIX:
    contractor -> depot: 100
      0, 100, 150, 200, 450, 150
      101, 0, 100, 250, 500, 250
      151, 101, 0, 150, 400, 200
      201, 251, 501, 0, 250, 150
      451, 501, 401, 251, 0, 300
      151, 251, 201, 151, 301, 0
  */

  graph.scooters.at(0).charge_level = 10;
  graph.scooters.at(1).charge_level = 10;

  std::unordered_map<std::string, int> bonus_for_charge_level_map;
  bonus_for_charge_level_map["10"] = -1000;

  graph.depots.at(0).settings.bonus_for_charge_level =
      models::BonusForChargeLevel(bonus_for_charge_level_map);

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{
      RechargeMission{0,
                      0,
                      0,
                      {2, 3, 4},
                      {sec{100}, sec{200}, sec{250}, sec{300}, sec{151}},
                      sec(1001),
                      1001 * 4.0}};

  /*
  std::cerr << "contractor_idx: " << solution.missions.back().contractor_idx
            << std::endl;
  std::cerr << "src_depot_idx: " << solution.missions.back().src_depot_idx
            << std::endl;
  std::cerr << "dst_depot_idx: " << solution.missions.back().dst_depot_idx
            << std::endl;

  std::cerr << "taken_scooters:";
  for (auto e : solution.missions.back().taken_scooters_idx)
    std::cerr << " " << e;
  std::cerr << std::endl;

  std::cerr << "moving_times:";
  for (auto e : solution.missions.back().moving_times)
    std::cerr << " " << e.count();
  std::cerr << std::endl;

  std::cerr << "time: " << solution.missions.back().time.count() << std::endl;
  std::cerr << "distance: " << solution.missions.back().distance << std::endl;
  */

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
// Bug from EFFICIENCYDEV-18964
TEST(TestRechargeVrp, Simple_BigTimeForEdgeFromContractorToDepot) {
  auto graph = BuildDefaultGraph();

  graph.contractors[0].edges_to_depots[0].time = sec(10000);
  graph.contractors[0].time_until_end_of_shift = sec(9999);

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{};

  EXPECT_EQ(solution.missions, expected_missions);
}

// 1 contractor with 6 capacity, 1 depot with 100 accums, 5 scooters
// Bug from EFFICIENCYDEV-18964
TEST(TestRechargeVrp, Simple_BigDistanceForEdgeFromContractorToDepot) {
  auto graph = BuildDefaultGraph();

  graph.contractors[0].edges_to_depots[0].distance = 10000.0;
  graph.depots[0].settings.max_distance_per_mission = 9999.0;

  const auto solution = RunRechargeAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RechargeMission>{};

  EXPECT_EQ(solution.missions, expected_missions);
}

}  // namespace scooters_ops_dispatch::algorithms
