#include <gtest/gtest.h>

#include <algorithms/relocation_vrp.hpp>
#include <models/models.hpp>
#include <models/relocation_graph.hpp>

namespace scooters_ops_dispatch::algorithms {

namespace {

const double kEpsilon = 1e-6;

using sec = std::chrono::seconds;

models::Contractor BuildDefaultContractor(const std::string& id) {
  models::Contractor contractor;
  contractor.id = id;
  contractor.vehicle_type = models::VehicleType::kCar;
  contractor.capacity = 2;
  return contractor;
}

models::RelocationDepotSettings BuildDefaultRelocationDepotSettings() {
  models::RelocationDepotSettings settings;
  settings.job_times.dropoff_vehicle = models::WorkTime{sec(25), sec(10)};
  settings.job_times.pickup_vehicle = models::WorkTime{sec(30), sec(20)};
  settings.job_times.start_delay = sec(20);
  return settings;
}

models::RelocationDepot BuildDefaultDepot(const std::string& id) {
  models::RelocationDepot depot;
  depot.id = id;
  depot.settings = BuildDefaultRelocationDepotSettings();
  return depot;
}

models::Scooter BuildDefaultScooter(const std::string& id) {
  models::Scooter scooter;
  scooter.id = id;
  scooter.draft_id = "draft_for_" + id;
  return scooter;
}

models::ParkingPlace BuildDefaultParkingPlacePickup(const std::string& id,
                                                    int scooters) {
  models::ParkingPlace parking_place;
  parking_place.job_type = models::ParkingPlace::JobType::kPickup;
  parking_place.id = id;
  for (int i = 0; i < scooters; i++) {
    parking_place.scooters.push_back(
        BuildDefaultScooter(id + "_scooter_" + std::to_string(i)));
  }
  return parking_place;
}

models::ParkingPlace BuildDefaultParkingPlaceDropoff(const std::string& id,
                                                     int capacity) {
  models::ParkingPlace parking_place;
  parking_place.job_type = models::ParkingPlace::JobType::kDropOff;
  parking_place.draft_id = "draft_" + id;
  parking_place.id = id;
  parking_place.capacity = capacity;
  return parking_place;
}

models::Edge BuildDefaultEdge(size_t idx, int time) {
  return models::Edge{idx, (double)time * 4.0, std::chrono::seconds(time),
                      (double)time, models::VehicleType::kCar};
}

models::RelocationGraph BuildDefaultGraph() {
  const int kParkingPlacesNumber = 5;

  std::vector<models::Contractor> contractors{
      BuildDefaultContractor("contractor_0")};
  std::vector<models::RelocationDepot> depots{
      BuildDefaultDepot("depot_0")};  // coord: (0, 0)

  std::vector<models::ParkingPlace> parking_places;
  parking_places.emplace_back(
      BuildDefaultParkingPlaceDropoff("place_0", 2));  // coord: (-200, 0)
  parking_places.emplace_back(
      BuildDefaultParkingPlacePickup("place_1", 3));  // coord: (-200, 200)
  parking_places.emplace_back(
      BuildDefaultParkingPlaceDropoff("place_2", 2));  // coord: (-200, 400)
  parking_places.emplace_back(
      BuildDefaultParkingPlacePickup("place_3", 1));  // coord: (-200, 600)
  parking_places.emplace_back(
      BuildDefaultParkingPlacePickup("place_4", 1));  // coord: (0, 600)

  contractors[0].edges_to_depots.emplace_back(BuildDefaultEdge(0, 10));

  depots[0].edges_to_parking_places.emplace_back(BuildDefaultEdge(0, 200));
  parking_places[0].edges_to_depots.emplace_back(BuildDefaultEdge(0, 200));

  depots[0].edges_to_parking_places.emplace_back(BuildDefaultEdge(1, 300));
  parking_places[1].edges_to_depots.emplace_back(BuildDefaultEdge(0, 300));

  depots[0].edges_to_parking_places.emplace_back(BuildDefaultEdge(2, 475));
  parking_places[2].edges_to_depots.emplace_back(BuildDefaultEdge(0, 475));

  depots[0].edges_to_parking_places.emplace_back(BuildDefaultEdge(3, 650));
  parking_places[3].edges_to_depots.emplace_back(BuildDefaultEdge(0, 650));

  depots[0].edges_to_parking_places.emplace_back(BuildDefaultEdge(4, 600));
  parking_places[4].edges_to_depots.emplace_back(BuildDefaultEdge(0, 600));

  std::vector<std::vector<int>> matrix{
      std::vector<int>{-1, 200, 400, 600, 650},
      std::vector<int>{200, -1, 200, 401, 475},
      std::vector<int>{400, 200, -1, 200, 300},
      std::vector<int>{600, 400, 200, -1, 200},
      std::vector<int>{650, 475, 300, 200, -1}};

  // edge from place1 to place3 is increased by 1
  // because there were ambigious optimal solutions
  /* ALL MATRIX:
    contractor -> depot: 10
    depot is vertex 0
    0, 200, 300, 475, 650, 600
    200, 0, 200, 401, 600, 650
    300, 200, 0, 200, 400, 475
    475, 400, 200, 0, 200, 300
    650, 600, 400, 200, 0, 200
    600, 650, 475, 300, 200, 0
  */

  for (size_t i = 0; i < kParkingPlacesNumber; i++) {
    for (size_t j = 0; j < kParkingPlacesNumber; j++) {
      if (matrix[i][j] != -1) {
        parking_places[i].edges_to_parking_places.emplace_back(
            BuildDefaultEdge(j, matrix[i][j]));
      }
    }
  }

  models::RelocationGraph graph;
  graph.contractors = std::move(contractors);
  graph.parking_places = std::move(parking_places);
  graph.depots = std::move(depots);

  return graph;
}

void CompareJobs(const RelocationJob& result, const RelocationJob& expected) {
  EXPECT_EQ(result.job_type, expected.job_type);
  EXPECT_EQ(result.parking_place_idx, expected.parking_place_idx);
  EXPECT_EQ(result.moving_time, expected.moving_time);
  EXPECT_EQ(result.execution_time, expected.execution_time);
  EXPECT_EQ(result.scooters_idx.size(), expected.scooters_idx.size());
}

void ValidatePath(const std::vector<RelocationJob>& path,
                  int contractor_capacity) {
  EXPECT_TRUE(path.size() >= 3);
  std::set<std::pair<size_t, size_t>> current;

  for (int i = 0; i < (int)path.size(); i++) {
    const auto& job = path[i];
    switch (job.job_type) {
      case RelocationJob::RelocationJobType::kStart: {
        EXPECT_TRUE(i == 0);

        EXPECT_TRUE(job.scooters_idx.empty());
        EXPECT_TRUE(current.empty());
        break;
      }
      case RelocationJob::RelocationJobType::kPickup: {
        EXPECT_TRUE(i >= 1 && i < (int)path.size() - 1);

        for (const auto& elem : job.scooters_idx) {
          EXPECT_TRUE(elem.first == job.parking_place_idx);

          EXPECT_TRUE(current.count(elem) == 0);

          current.insert(elem);
          EXPECT_TRUE((int)current.size() <= contractor_capacity);
        }
        break;
      }
      case RelocationJob::RelocationJobType::kDropOff: {
        EXPECT_TRUE(i >= 1 && i < (int)path.size() - 1);

        for (const auto& elem : job.scooters_idx) {
          EXPECT_TRUE(current.count(elem) == 1);

          current.erase(elem);
        }
        break;
      }
      case RelocationJob::RelocationJobType::kFinish: {
        EXPECT_TRUE(i == (int)path.size() - 1);

        EXPECT_TRUE(job.scooters_idx.empty());
        EXPECT_TRUE(current.empty());
        break;
      }
    }
  }
}

void CompareAndValidateMissions(const RelocationMission& result,
                                const RelocationMission& expected,
                                int contractor_capacity) {
  EXPECT_EQ(result.contractor_idx, expected.contractor_idx);
  EXPECT_EQ(result.depot_idx, expected.depot_idx);
  EXPECT_TRUE(abs(result.distance - expected.distance) <= kEpsilon);
  EXPECT_EQ(result.time, expected.time);

  EXPECT_EQ(result.path.size(), expected.path.size());
  for (size_t i = 0; i < result.path.size(); i++) {
    CompareJobs(result.path[i], expected.path[i]);
  }
  ValidatePath(result.path, contractor_capacity);
  ValidatePath(expected.path, contractor_capacity);
}

void CompareAndValidateSolutions(const std::vector<RelocationMission>& result,
                                 const std::vector<RelocationMission>& expected,
                                 int contractor_capacity) {
  EXPECT_EQ(result.size(), expected.size());
  for (size_t i = 0; i < result.size(); i++) {
    CompareAndValidateMissions(result[i], expected[i], contractor_capacity);
  }
}

[[maybe_unused]] void PrintMissions(
    const std::vector<RelocationMission>& missions) {
  std::string prefix;

  std::cerr << prefix << "[" << std::endl;

  prefix += "  ";
  for (const auto& mission : missions) {
    std::cerr << prefix << "{" << std::endl;
    prefix += "  ";

    std::cerr << prefix << "\"contractor_idx\": " << mission.contractor_idx
              << "," << std::endl;
    std::cerr << prefix << "\"depot_idx\": " << mission.depot_idx << ","
              << std::endl;
    std::cerr << prefix << "\"time\": " << mission.time.count() << ","
              << std::endl;
    std::cerr << prefix << "\"distance\": " << mission.distance << ","
              << std::endl;
    std::cerr << prefix << "\"path\": [" << std::endl;

    prefix += "  ";
    for (const auto& job : mission.path) {
      std::cerr << prefix << "{" << std::endl;
      prefix += "  ";

      std::cerr << prefix << "\"job_type\": " << (int)job.job_type << ","
                << std::endl;
      std::cerr << prefix << "\"parking_place_idx\": " << job.parking_place_idx
                << "," << std::endl;
      std::cerr << prefix << "\"moving_time\": " << job.moving_time.count()
                << "," << std::endl;
      std::cerr << prefix
                << "\"execution_time\": " << job.execution_time.count() << ","
                << std::endl;
      std::cerr << prefix << "\"scooters_idx\": [";
      bool need_del = false;
      for (const auto& [parking_place_idx, scooter_idx] : job.scooters_idx) {
        if (need_del) {
          std::cerr << ", ";
        }
        need_del = true;
        std::cerr << "(" << parking_place_idx << ", " << scooter_idx << ")";
      }
      std::cerr << "]," << std::endl;

      prefix.resize(prefix.size() - 2);
      std::cerr << prefix << "}," << std::endl;
    }
    prefix.resize(prefix.size() - 2);

    std::cerr << prefix << "]," << std::endl;

    prefix.resize(prefix.size() - 2);
    std::cerr << prefix << "}," << std::endl;
  }
  prefix.resize(prefix.size() - 2);

  std::cerr << prefix << "]" << std::endl;
}

}  // namespace

// Contractor capacity is 2
TEST(TestRelocationVrp, Simple) {
  const auto graph = BuildDefaultGraph();
  const auto solution = RunRelocationAlgorithmVrp(graph);

  const auto expected_missions =
      std::vector<RelocationMission>{RelocationMission{
          0,
          0,
          {
              RelocationJob{RelocationJob::RelocationJobType::kStart,
                            {},
                            {},
                            sec(10 + 20),
                            sec(0)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 0}, {1, 1}},
                            sec(300 + 30),
                            sec(20 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            2,
                            {{1, 0}, {1, 1}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            3,
                            {{3, 0}},
                            sec(200 + 30),
                            sec(20 * 1)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 2}},
                            sec(400 + 30),
                            sec(20 * 1)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            0,
                            {{3, 0}, {1, 2}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kFinish,
                            {},
                            {},
                            sec(200),
                            sec(0)},
          },
          sec(1790),
          1510.0 * 4.0}};

  /*
  std::cerr << "EXPECTED: " << std::endl;
  PrintMissions(expected_missions);
  std::cerr << std::endl;

  std::cerr << "FOUND: " << std::endl;
  PrintMissions(solution.missions);
  std::cerr << std::endl;
  */

  CompareAndValidateSolutions(solution.missions, expected_missions, 2);
}

TEST(TestRelocationVrp, Simple_TimeUntilClosingOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].time_until_closing = sec(1790);
  const auto solution = RunRelocationAlgorithmVrp(graph);

  const auto expected_missions =
      std::vector<RelocationMission>{RelocationMission{
          0,
          0,
          {
              RelocationJob{RelocationJob::RelocationJobType::kStart,
                            {},
                            {},
                            sec(10 + 20),
                            sec(0)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 0}, {1, 1}},
                            sec(300 + 30),
                            sec(20 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            2,
                            {{1, 0}, {1, 1}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            3,
                            {{3, 0}},
                            sec(200 + 30),
                            sec(20 * 1)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 2}},
                            sec(400 + 30),
                            sec(20 * 1)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            0,
                            {{3, 0}, {1, 2}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kFinish,
                            {},
                            {},
                            sec(200),
                            sec(0)},
          },
          sec(1790),
          1510.0 * 4.0}};

  /*
  std::cerr << "EXPECTED: " << std::endl;
  PrintMissions(expected_missions);
  std::cerr << std::endl;

  std::cerr << "FOUND: " << std::endl;
  PrintMissions(solution.missions);
  std::cerr << std::endl;
  */

  CompareAndValidateSolutions(solution.missions, expected_missions, 2);
}

TEST(TestRelocationVrp, Simple_TimeUntilClosingNotOK) {
  auto graph = BuildDefaultGraph();
  graph.depots[0].time_until_closing = sec(1329);
  const auto solution = RunRelocationAlgorithmVrp(graph);

  const auto expected_missions =
      std::vector<RelocationMission>{RelocationMission{
          0,
          0,
          {
              RelocationJob{RelocationJob::RelocationJobType::kStart,
                            {},
                            {},
                            sec(10 + 20),
                            sec(0)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 0}, {1, 1}},
                            sec(300 + 30),
                            sec(20 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            0,
                            {{1, 0}, {1, 1}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kFinish,
                            {},
                            {},
                            sec(200),
                            sec(0)},
          },
          sec(845),
          710.0 * 4.0}};

  /*
  std::cerr << "EXPECTED: " << std::endl;
  PrintMissions(expected_missions);
  std::cerr << std::endl;

  std::cerr << "FOUND: " << std::endl;
  PrintMissions(solution.missions);
  std::cerr << std::endl;
  */

  CompareAndValidateSolutions(solution.missions, expected_missions, 2);
}

TEST(TestRelocationVrp, Simple_TimeUntilEndOfShiftOK) {
  auto graph = BuildDefaultGraph();
  graph.contractors[0].time_until_end_of_shift = sec(1790);
  const auto solution = RunRelocationAlgorithmVrp(graph);

  const auto expected_missions =
      std::vector<RelocationMission>{RelocationMission{
          0,
          0,
          {
              RelocationJob{RelocationJob::RelocationJobType::kStart,
                            {},
                            {},
                            sec(10 + 20),
                            sec(0)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 0}, {1, 1}},
                            sec(300 + 30),
                            sec(20 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            2,
                            {{1, 0}, {1, 1}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            3,
                            {{3, 0}},
                            sec(200 + 30),
                            sec(20 * 1)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 2}},
                            sec(400 + 30),
                            sec(20 * 1)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            0,
                            {{3, 0}, {1, 2}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kFinish,
                            {},
                            {},
                            sec(200),
                            sec(0)},
          },
          sec(1790),
          1510.0 * 4.0}};

  /*
  std::cerr << "EXPECTED: " << std::endl;
  PrintMissions(expected_missions);
  std::cerr << std::endl;

  std::cerr << "FOUND: " << std::endl;
  PrintMissions(solution.missions);
  std::cerr << std::endl;
  */

  CompareAndValidateSolutions(solution.missions, expected_missions, 2);
}

TEST(TestRelocationVrp, Simple_TimeUntilEndOfShiftNotOK) {
  auto graph = BuildDefaultGraph();
  graph.contractors[0].time_until_end_of_shift = sec(1329);
  const auto solution = RunRelocationAlgorithmVrp(graph);

  const auto expected_missions =
      std::vector<RelocationMission>{RelocationMission{
          0,
          0,
          {
              RelocationJob{RelocationJob::RelocationJobType::kStart,
                            {},
                            {},
                            sec(10 + 20),
                            sec(0)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 0}, {1, 1}},
                            sec(300 + 30),
                            sec(20 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            0,
                            {{1, 0}, {1, 1}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kFinish,
                            {},
                            {},
                            sec(200),
                            sec(0)},
          },
          sec(845),
          710.0 * 4.0}};

  /*
  std::cerr << "EXPECTED: " << std::endl;
  PrintMissions(expected_missions);
  std::cerr << std::endl;

  std::cerr << "FOUND: " << std::endl;
  PrintMissions(solution.missions);
  std::cerr << std::endl;
  */

  CompareAndValidateSolutions(solution.missions, expected_missions, 2);
}

TEST(TestRelocationVrp, Simple_TwoContractors) {
  auto graph = BuildDefaultGraph();
  graph.contractors[0].time_until_end_of_shift = sec(1329);
  graph.contractors.push_back(BuildDefaultContractor("contractor_1"));
  graph.contractors[1].edges_to_depots.emplace_back(BuildDefaultEdge(0, 20));

  const auto solution = RunRelocationAlgorithmVrp(graph);

  const auto expected_missions = std::vector<RelocationMission>{
      RelocationMission{
          0,
          0,
          {
              RelocationJob{RelocationJob::RelocationJobType::kStart,
                            {},
                            {},
                            sec(10 + 20),
                            sec(0)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 0}, {1, 1}},
                            sec(300 + 30),
                            sec(20 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            0,
                            {{1, 0}, {1, 1}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kFinish,
                            {},
                            {},
                            sec(200),
                            sec(0)},
          },
          sec(845),
          710.0 * 4.0},

      RelocationMission{
          1,
          0,
          {
              RelocationJob{RelocationJob::RelocationJobType::kStart,
                            {},
                            {},
                            sec(20 + 20),
                            sec(0)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            1,
                            {{1, 2}},
                            sec(300 + 30),
                            sec(20 * 1)},
              RelocationJob{RelocationJob::RelocationJobType::kPickup,
                            3,
                            {{3, 0}},
                            sec(401 + 30),
                            sec(20 * 1)},
              RelocationJob{RelocationJob::RelocationJobType::kDropOff,
                            2,
                            {{3, 0}, {1, 2}},
                            sec(200 + 25),
                            sec(10 * 2)},
              RelocationJob{RelocationJob::RelocationJobType::kFinish,
                            {},
                            {},
                            sec(475),
                            sec(0)},
          },
          sec(1561),
          1396.0 * 4.0}};
  /*
  std::cerr << "EXPECTED: " << std::endl;
  PrintMissions(expected_missions);
  std::cerr << std::endl;

  std::cerr << "FOUND: " << std::endl;
  PrintMissions(solution.missions);
  std::cerr << std::endl;
  */

  CompareAndValidateSolutions(solution.missions, expected_missions, 2);
}

}  // namespace scooters_ops_dispatch::algorithms
