#include <gtest/gtest.h>

#include <iostream>
#include <random>

#include <algorithms/ortools/greedy_approach.hpp>
#include <algorithms/ortools/vrp.hpp>
#include <algorithms/vrp_executor.hpp>

namespace scooters_ops_dispatch::algorithms {

namespace {

using ms = std::chrono::milliseconds;
using Matrix = std::vector<std::vector<int64_t>>;

void Validate(const ortools::VrpInput& data,
              const ortools::VrpOutput& solution) {
  int64_t total_score = data.initial_time;
  int64_t total_time = data.initial_time;
  int64_t total_distance = data.initial_distance;

  int64_t cur_load = 0;
  int64_t min_load = 0;
  int64_t max_load = 0;

  std::vector<bool> visited(data.vertices_count);

  int prev_vertex = -1;

  int depot_visited = 0;

  for (auto vertex : solution.path) {
    EXPECT_FALSE(visited[vertex]);
    if (vertex != 0) {
      visited[vertex] = true;
    } else {
      depot_visited++;
    }

    if (prev_vertex != -1) {
      total_score += data.time_matrix[prev_vertex][vertex] +
                     data.job_time[vertex] + data.priorities[vertex];
      total_time +=
          data.time_matrix[prev_vertex][vertex] + data.job_time[vertex];
      total_distance += data.distance_matrix[prev_vertex][vertex];
      cur_load += data.demand[vertex];
      min_load = std::min(min_load, cur_load);
      max_load = std::max(max_load, cur_load);
    }
    prev_vertex = vertex;
  }

  // std::cerr << "Vertices: " << solution.path.size() << ", score: " <<
  // total_score << ", time: " << total_time << "s, distance: " <<
  // total_distance
  // << "m" << std::endl;

  EXPECT_EQ(depot_visited, 2);

  EXPECT_TRUE(min_load >= 0);
  EXPECT_TRUE(max_load <= data.max_capacity);
  if (data.load_target_is_zero) {
    EXPECT_TRUE(cur_load == 0);
  }
  if (data.max_mission_time) {
    EXPECT_TRUE(total_time <= *data.max_mission_time);
  }
  if (data.max_mission_distance) {
    EXPECT_TRUE(total_distance <= *data.max_mission_distance);
  }

  EXPECT_EQ(solution.total_distance, total_distance);
  EXPECT_EQ(solution.total_time, total_time);
  EXPECT_EQ(solution.total_score, total_score);
}

std::vector<std::pair<double, double>> GenerateRandomPoints(int vertices_count,
                                                            double scale_factor,
                                                            int random_seed) {
  std::mt19937 gen(random_seed);
  std::uniform_real_distribution<double> dist(scale_factor);

  std::vector<std::pair<double, double>> result(vertices_count);
  for (int i = 0; i < vertices_count; i++) {
    result[i].first = dist(gen);
    result[i].second = dist(gen);
  }
  return result;
}

Matrix GenerateMatrixByPoints(
    const std::vector<std::pair<double, double>>& points, int random_seed) {
  std::mt19937 gen(random_seed);
  std::uniform_real_distribution<double> dist(
      1.0, 4.0);  // for more similar distances to real

  int vertices_count = (int)points.size();
  Matrix matrix(vertices_count, std::vector<int64_t>(vertices_count));

  for (int i = 0; i < vertices_count; i++) {
    for (int j = 0; j < vertices_count; j++) {
      double distance = std::hypot(points[i].first - points[j].first,
                                   points[i].second - points[j].second);
      double random_factor = dist(gen);
      matrix[i][j] = distance * random_factor;
    }
  }

  // NOTE: http://e-maxx.ru/algo/floyd_warshall_algorithm
  for (int k = 0; k < vertices_count; k++) {
    for (int i = 0; i < vertices_count; i++) {
      for (int j = 0; j < vertices_count; j++) {
        matrix[i][j] = std::min(matrix[i][j], matrix[i][k] + matrix[k][j]);
      }
    }
  }

  return matrix;
}

ortools::VrpInput BuildVrpInput(Matrix time_matrix, Matrix distance_matrix) {
  ortools::VrpInput data;

  data.vertices_count = (int)time_matrix.size();
  data.time_matrix = std::move(time_matrix);
  data.distance_matrix = std::move(distance_matrix);
  data.priorities.resize(data.vertices_count);
  data.job_time.resize(data.vertices_count);
  data.demand.resize(data.vertices_count);

  return data;
}

void RecursiveSolveDummy(const ortools::VrpInput& data,
                         std::optional<ortools::VrpOutput>& best_solution,
                         int vertex, std::vector<int>& path,
                         std::vector<bool>& visited, int capacity,
                         int64_t score, int64_t time, int64_t distance) {
  if (vertex == 0 && path.size() > 1) {
    if (data.load_target_is_zero && capacity != 0) return;
    if (data.max_mission_time && time > *data.max_mission_time) return;
    if (data.max_mission_distance && distance > *data.max_mission_distance)
      return;

    if (!best_solution || best_solution->path.size() < path.size() ||
        (best_solution->path.size() == path.size() &&
         best_solution->total_score > score)) {
      ortools::VrpOutput solution;
      solution.path = path;
      solution.total_score = score;
      solution.total_time = time;
      solution.total_distance = distance;
      best_solution = std::move(solution);
    }
    return;
  }

  for (int next_vertex = 0; next_vertex < data.vertices_count; next_vertex++) {
    if (vertex == next_vertex) continue;
    if (visited[next_vertex]) continue;

    int64_t next_capacity = capacity + data.demand[next_vertex];
    int64_t next_score = score + data.time_matrix[vertex][next_vertex] +
                         data.job_time[next_vertex] +
                         data.priorities[next_vertex];
    int64_t next_time = time + data.time_matrix[vertex][next_vertex] +
                        data.job_time[next_vertex];
    int64_t next_distance =
        distance + data.distance_matrix[vertex][next_vertex];

    if (next_capacity > data.max_capacity) continue;
    if (next_capacity < 0) continue;

    path.push_back(next_vertex);
    visited[next_vertex] = true;

    RecursiveSolveDummy(data, best_solution, next_vertex, path, visited,
                        next_capacity, next_score, next_time, next_distance);

    visited[next_vertex] = false;
    path.pop_back();
  }
}

std::optional<ortools::VrpOutput> SolveVrpDummy(const ortools::VrpInput& data) {
  std::vector<int> path = {0};
  std::vector<bool> visited(data.vertices_count);
  std::optional<ortools::VrpOutput> solution;

  RecursiveSolveDummy(data, solution, 0, path, visited, 0, data.initial_time,
                      data.initial_time, data.initial_distance);
  return solution;
}

/*
std::optional<ortools::VrpOutput> TspOverSolution(
    const ortools::VrpInput& init_data,
    const std::optional<ortools::VrpOutput>& init_solution_opt,
    const std::chrono::milliseconds& time_limit) {
  if (!init_solution_opt) return std::nullopt;
  const auto& init_solution = *init_solution_opt;

  std::vector<bool> used_vertices(init_data.vertices_count);
  for (const auto& vertex : init_solution.path) {
    used_vertices[vertex] = true;
  }

  ortools::VrpInput data;
  data.vertices_count = (int)init_solution.path.size() - 1;
  data.max_capacity = init_data.max_capacity;
  data.load_target_is_zero = init_data.load_target_is_zero;
  data.max_mission_time = init_data.max_mission_time;
  data.max_mission_distance = init_data.max_mission_distance;
  data.initial_time = init_data.initial_time;
  data.initial_distance = init_data.initial_distance;
  data.visit_penalty = init_data.visit_penalty;

  data.time_matrix.resize(data.vertices_count,
                          std::vector<int64_t>(data.vertices_count));
  data.distance_matrix.resize(data.vertices_count,
                              std::vector<int64_t>(data.vertices_count));
  data.priorities.resize(data.vertices_count);
  data.job_time.resize(data.vertices_count);
  data.demand.resize(data.vertices_count);

  for (int i = 0; i < (int)init_solution.path.size() - 1; i++) {
    int i_vertex = init_solution.path[i];

    data.priorities[i] = init_data.priorities[i_vertex];
    data.job_time[i] = init_data.job_time[i_vertex];
    data.demand[i] = init_data.demand[i_vertex];

    for (int j = 0; j < (int)init_solution.path.size() - 1; j++) {
      int j_vertex = init_solution.path[j];

      data.time_matrix[i][j] = init_data.time_matrix[i_vertex][j_vertex];
      data.distance_matrix[i][j] =
          init_data.distance_matrix[i_vertex][j_vertex];
    }
  }

  auto final_solution = ortools::SolveVrp(data, time_limit);
  if (!final_solution) {
    std::cerr << "- ";
    return init_solution_opt;
  }
  if (final_solution->total_score >= init_solution.total_score) {
    std::cerr << "= ";
    return init_solution_opt;
  }

  for (auto& elem : final_solution->path) {
    elem = init_solution.path[elem];
  }

  return final_solution;
}

std::optional<ortools::VrpOutput> OrOverSolution(
    const ortools::VrpInput& data,
    const std::optional<ortools::VrpOutput>& init_solution_opt,
    const std::chrono::milliseconds& time_limit) {
  if (!init_solution_opt) return std::nullopt;
  const auto& init_solution = *init_solution_opt;

  auto final_solution = ortools::SolveVrp(data, time_limit, init_solution.path);
  if (!final_solution) {
    std::cerr << "- ";
    return init_solution_opt;
  }
  if (final_solution->total_score >= init_solution.total_score) {
    std::cerr << "= ";
    return init_solution_opt;
  }

  return final_solution;
}
*/

}  // namespace

TEST(TestVrp, Recharge_100_100) {
  int scooters = 100;
  int capacity = 100;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
}

TEST(TestVrp, Recharge_100_50) {
  int scooters = 100;
  int capacity = 50;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
}

TEST(TestVrp, Recharge_50_50) {
  int scooters = 50;
  int capacity = 50;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
}

TEST(TestVrp, Recharge_50_20) {
  int scooters = 50;
  int capacity = 20;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
}

// Typical scenario for underesupply
TEST(TestVrp, Recharge_100_6) {
  int scooters = 100;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  EXPECT_EQ((int)solution.value().path.size(), 8);
}

TEST(TestVrp, Recharge_Dummy_9_9) {
  int scooters = 9;
  int capacity = 9;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_priorities) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  {
    std::mt19937 gen(0);
    std::uniform_int_distribution<int> dist(-1000, 1000);
    for (int i = 1; i < data.vertices_count; i++)
      data.priorities[i] = dist(gen);
  }

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_jobs) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  {
    std::mt19937 gen(1);
    std::uniform_int_distribution<int> dist(0, 1000);
    for (int i = 1; i < data.vertices_count; i++) data.job_time[i] = dist(gen);
  }

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_priorities_jobs) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  {
    std::mt19937 gen(2);
    std::uniform_int_distribution<int> dist(-1000, 1000);
    for (int i = 1; i < data.vertices_count; i++)
      data.priorities[i] = dist(gen);
  }
  {
    std::mt19937 gen(3);
    std::uniform_int_distribution<int> dist(0, 1000);
    for (int i = 1; i < data.vertices_count; i++) data.job_time[i] = dist(gen);
  }

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_time_limit_ok) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  data.max_mission_time = 3061;  // don't affect optimal solution

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  // std::cerr << dummy_solution.value().total_time << std::endl;

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_time_limit_other) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  data.max_mission_time = 3060;  // need new solution

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  // std::cerr << dummy_solution.value().total_time << std::endl;

  EXPECT_EQ((int)solution.value().path.size(), capacity + 1);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_distance_limit_ok) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  data.max_mission_distance = 4018;  // don't affect optimal solution

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  // std::cerr << dummy_solution.value().total_distance << std::endl;

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_distance_limit_other) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  data.max_mission_distance = 4017;  // need new solution

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  // std::cerr << dummy_solution.value().total_distance << std::endl;

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_init_time) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  data.initial_time = 10;
  data.max_mission_time = 3070;  // need new solution

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  // std::cerr << dummy_solution.value().total_time << std::endl;

  EXPECT_EQ((int)solution.value().path.size(), capacity + 1);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_distance_init_distance) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  data.initial_distance = 10;
  data.max_mission_distance = 4027;  // need new solution

  auto solution = ortools::SolveVrp(data, ms(500));
  Validate(data, solution.value());

  auto dummy_solution = SolveVrpDummy(data);
  Validate(data, dummy_solution.value());

  // std::cerr << dummy_solution.value().total_distance << std::endl;

  EXPECT_EQ((int)solution.value().path.size(), capacity + 2);
  EXPECT_EQ(solution.value().path.size(), dummy_solution.value().path.size());
  EXPECT_EQ(solution.value().path, dummy_solution.value().path);
  EXPECT_EQ(solution.value().total_score, dummy_solution.value().total_score);
  EXPECT_EQ(solution.value().total_time, dummy_solution.value().total_time);
  EXPECT_EQ(solution.value().total_distance,
            dummy_solution.value().total_distance);
}

TEST(TestVrp, Recharge_Dummy_9_6_without_solution) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  data.load_target_is_zero = true;  // wrong for recharging

  auto solution = ortools::SolveVrp(data, ms(500));

  auto dummy_solution = SolveVrpDummy(data);

  EXPECT_EQ(solution.has_value(), false);
  EXPECT_EQ(dummy_solution.has_value(), false);
}

TEST(TestVrp, Recharge_Dummy_9_6_without_solution2) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  data.max_mission_distance = 1;

  auto solution = ortools::SolveVrp(data, ms(500));

  auto dummy_solution = SolveVrpDummy(data);

  EXPECT_EQ(solution.has_value(), false);
  EXPECT_EQ(dummy_solution.has_value(), false);
}

TEST(TestVrp, Recharge_Dummy_9_6_without_solution3) {
  int scooters = 9;
  int capacity = 6;
  int vertices = 1 + scooters;

  auto points = GenerateRandomPoints(vertices, 1000.0, 0);
  auto time_matrix = GenerateMatrixByPoints(points, 0);
  auto distance_matrix = GenerateMatrixByPoints(points, 1);

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
  data.max_capacity = capacity;

  data.max_mission_time = 1;

  auto solution = ortools::SolveVrp(data, ms(500));

  auto dummy_solution = SolveVrpDummy(data);

  EXPECT_EQ(solution.has_value(), false);
  EXPECT_EQ(dummy_solution.has_value(), false);
}

TEST(TestVrp, Relocation_OrtoolsWithGreedyInit) {
  int pickup_places = 100;
  int pickup_places_capacity = 1;

  int dropoff_places = 100;
  int dropoff_places_capacity = 5;

  int contractor_capacity = 25;

  int64_t pickup_base_job_time = 300;
  int64_t pickup_time_per_unit = 180;
  int64_t dropoff_base_job_time = 300;
  int64_t dropoff_time_per_unit = 120;

  int places_count = 1 + pickup_places + dropoff_places;
  auto points = GenerateRandomPoints(places_count, 3600.0, 0);
  auto places_time_matrix = GenerateMatrixByPoints(points, 1);
  auto places_distance_matrix = GenerateMatrixByPoints(points, 2);

  int vertices_count = 1 + pickup_places * pickup_places_capacity +
                       dropoff_places * dropoff_places_capacity;
  std::vector<int> vertex_to_place_mapping;
  int place_id = 0;
  vertex_to_place_mapping.push_back(place_id++);
  std::vector<int64_t> demand;
  demand.push_back(0);
  for (int i = 0; i < pickup_places; i++) {
    for (int j = 0; j < pickup_places_capacity; j++) {
      vertex_to_place_mapping.push_back(place_id);
      demand.push_back(1);
    }
    place_id++;
  }
  for (int i = 0; i < dropoff_places; i++) {
    for (int j = 0; j < dropoff_places_capacity; j++) {
      vertex_to_place_mapping.push_back(place_id);
      demand.push_back(-1);
    }
    place_id++;
  }

  Matrix time_matrix(vertices_count, std::vector<int64_t>(vertices_count));
  Matrix distance_matrix(vertices_count, std::vector<int64_t>(vertices_count));
  for (int i = 0; i < vertices_count; i++) {
    int i_place_idx = vertex_to_place_mapping[i];
    for (int j = 0; j < vertices_count; j++) {
      int j_place_idx = vertex_to_place_mapping[j];
      if (i_place_idx == j_place_idx) {
        time_matrix[i][j] = 0;
        distance_matrix[i][j] = 0;
      } else {
        int64_t additional_time = 0;
        if (j_place_idx >= 1 && j_place_idx <= pickup_places) {
          additional_time = pickup_base_job_time;
        } else if (j_place_idx > pickup_places) {
          additional_time = dropoff_base_job_time;
        }
        time_matrix[i][j] =
            places_time_matrix[i_place_idx][j_place_idx] + additional_time;
        distance_matrix[i][j] =
            places_distance_matrix[i_place_idx][j_place_idx];
      }
    }
  }

  auto data = BuildVrpInput(time_matrix, distance_matrix);
  data.load_target_is_zero = true;
  data.max_capacity = contractor_capacity;
  for (int i = 0; i < vertices_count; i++) {
    if (demand[i] == -1) {
      data.job_time[i] = dropoff_time_per_unit;
    } else if (demand[i] == -1) {
      data.job_time[i] = pickup_time_per_unit;
    }
  }
  data.demand = std::move(demand);

  data.max_mission_time = 40000;

  auto time_limit = ms(500);

  auto greedy_solution = ortools::FindGreedyApproach(data);
  Validate(data, greedy_solution.value());

  // std::cerr << "greedy_solution scooters: " <<
  // greedy_solution.value().path.size() / 2 - 1 << std::endl;

  auto ortools_over_greedy_solution =
      ortools::SolveVrp(data, time_limit, greedy_solution.value().path);
  Validate(data, ortools_over_greedy_solution.value());

  // std::cerr << "ortools_over_greedy_solution scooters: " <<
  // ortools_over_greedy_solution.value().path.size() / 2 - 1 << std::endl;
}

/*
TEST(TestVrp, Relocation_CompareWithGreedy) {
  int pickup_places = 1000;
  int pickup_places_capacity = 1;

  int dropoff_places = 1000;
  int dropoff_places_capacity = 5;

  int contractor_capacity = 25;

  int64_t pickup_base_job_time = 300;
  int64_t pickup_time_per_unit = 180;
  int64_t dropoff_base_job_time = 300;
  int64_t dropoff_time_per_unit = 120;

  int64_t total_or = 0;
  int64_t total_greedy = 0;
  int64_t total_tsp_over_greedy = 0;
  int64_t total_or_over_greedy = 0;
  int64_t total_or_over_optimized_greedy = 0;

  int64_t total_or_scooters = 0;
  int64_t total_greedy_scooters = 0;
  int64_t total_tsp_over_greedy_scooters = 0;
  int64_t total_or_over_greedy_scooters = 0;
  int64_t total_or_over_optimized_greedy_scooters = 0;

  for (int itt = 0; itt < 1; itt++) {
    int places_count = 1 + pickup_places + dropoff_places;
    auto points = GenerateRandomPoints(places_count, 3600.0, itt);
    auto places_time_matrix = GenerateMatrixByPoints(points, itt * 2);
    auto places_distance_matrix = GenerateMatrixByPoints(points, itt * 2 + 1);

    int vertices_count = 1 + pickup_places * pickup_places_capacity +
                         dropoff_places * dropoff_places_capacity;
    std::vector<int> vertex_to_place_mapping;
    int place_id = 0;
    vertex_to_place_mapping.push_back(place_id++);
    std::vector<int64_t> demand;
    demand.push_back(0);
    for (int i = 0; i < pickup_places; i++) {
      for (int j = 0; j < pickup_places_capacity; j++) {
        vertex_to_place_mapping.push_back(place_id);
        demand.push_back(1);
      }
      place_id++;
    }
    for (int i = 0; i < dropoff_places; i++) {
      for (int j = 0; j < dropoff_places_capacity; j++) {
        vertex_to_place_mapping.push_back(place_id);
        demand.push_back(-1);
      }
      place_id++;
    }

    Matrix time_matrix(vertices_count, std::vector<int64_t>(vertices_count));
    Matrix distance_matrix(vertices_count,
                           std::vector<int64_t>(vertices_count));
    for (int i = 0; i < vertices_count; i++) {
      int i_place_idx = vertex_to_place_mapping[i];
      for (int j = 0; j < vertices_count; j++) {
        int j_place_idx = vertex_to_place_mapping[j];
        if (i_place_idx == j_place_idx) {
          time_matrix[i][j] = 0;
          distance_matrix[i][j] = 0;
        } else {
          int64_t additional_time = 0;
          if (j_place_idx >= 1 && j_place_idx <= pickup_places) {
            additional_time = pickup_base_job_time;
          } else if (j_place_idx > pickup_places) {
            additional_time = dropoff_base_job_time;
          }
          time_matrix[i][j] =
              places_time_matrix[i_place_idx][j_place_idx] + additional_time;
          distance_matrix[i][j] =
              places_distance_matrix[i_place_idx][j_place_idx];
        }
      }
    }

    auto data = BuildVrpInput(time_matrix, distance_matrix);
    data.load_target_is_zero = true;
    data.max_capacity = contractor_capacity;
    for (int i = 0; i < vertices_count; i++) {
      if (demand[i] == -1) {
        data.job_time[i] = dropoff_time_per_unit;
      } else if (demand[i] == -1) {
        data.job_time[i] = pickup_time_per_unit;
      }
    }
    data.demand = std::move(demand);

    data.max_mission_time = 40000;

    auto time_limit = ms(120 * 1000);  // *4

    auto greedy_solution = ortools::FindGreedyApproach(data);
    {
      Validate(data, greedy_solution.value());

      total_greedy += greedy_solution.value().total_score;
      total_greedy_scooters += greedy_solution.value().path.size() / 2 - 1;

      std::cerr << greedy_solution.value().total_score << "("
                << greedy_solution.value().path.size() / 2 - 1 << ")"
                << "   ";
    }

    auto tsp_over_greedy_solution =
        TspOverSolution(data, greedy_solution, time_limit);
    {
      Validate(data, tsp_over_greedy_solution.value());

      total_tsp_over_greedy += tsp_over_greedy_solution.value().total_score;
      total_tsp_over_greedy_scooters +=
          tsp_over_greedy_solution.value().path.size() / 2 - 1;

      std::cerr << tsp_over_greedy_solution.value().total_score << "("
                << tsp_over_greedy_solution.value().path.size() / 2 - 1 << ")"
                << "   ";
    }

    auto or_over_greedy_solution =
        OrOverSolution(data, greedy_solution, time_limit);
    {
      Validate(data, or_over_greedy_solution.value());

      total_or_over_greedy += or_over_greedy_solution.value().total_score;
      total_or_over_greedy_scooters +=
          or_over_greedy_solution.value().path.size() / 2 - 1;

      std::cerr << or_over_greedy_solution.value().total_score << "("
                << or_over_greedy_solution.value().path.size() / 2 - 1 << ")"
                << "   ";
    }

    auto or_over_optimized_greedy_solution =
        OrOverSolution(data, tsp_over_greedy_solution, time_limit);
    {
      Validate(data, or_over_optimized_greedy_solution.value());

      total_or_over_optimized_greedy +=
          or_over_optimized_greedy_solution.value().total_score;
      total_or_over_optimized_greedy_scooters +=
          or_over_optimized_greedy_solution.value().path.size() / 2 - 1;

      std::cerr << or_over_optimized_greedy_solution.value().total_score << "("
                << or_over_optimized_greedy_solution.value().path.size() / 2 - 1
                << ")" << std::endl;
    }
  }

  std::cerr << "total_or: " << total_or << " (" << total_or_scooters << ")"
            << std::endl;
  std::cerr << "total_greedy: " << total_greedy << " (" << total_greedy_scooters
            << ")" << std::endl;
  std::cerr << "total_tsp_over_greedy: " << total_tsp_over_greedy << " ("
            << total_tsp_over_greedy_scooters << ")" << std::endl;
  std::cerr << "total_or_over_greedy: " << total_or_over_greedy << " ("
            << total_or_over_greedy_scooters << ")" << std::endl;
  std::cerr << "total_or_over_optimized_greedy: "
            << total_or_over_optimized_greedy << " ("
            << total_or_over_optimized_greedy_scooters << ")" << std::endl;
}

// Moscow recharging
TEST(TestVrp, Recharge_CompareWithGreedy) {
  int scooters = 1000;
  int capacity = 100;
  int vertices = 1 + scooters;

  int64_t total_or = 0;
  int64_t total_greedy = 0;
  int64_t total_tsp_over_greedy = 0;
  int64_t total_or_over_greedy = 0;
  int64_t total_or_over_optimized_greedy = 0;

  for (int itt = 0; itt < 2; itt++) {
    auto points = GenerateRandomPoints(vertices, 3600.0, itt);
    auto time_matrix = GenerateMatrixByPoints(points, itt * 2);
    auto distance_matrix = GenerateMatrixByPoints(points, itt * 2 + 1);

    auto data = BuildVrpInput(time_matrix, distance_matrix);
    for (int i = 1; i < data.vertices_count; i++) data.demand[i] = 1;
    for (int i = 1; i < data.vertices_count; i++) data.job_time[i] = 300;
    data.max_capacity = capacity;

    auto time_limit = ms(60 * 1000);  // *4

    auto or_solution = ortools::SolveVrp(data, time_limit);
    {
      Validate(data, or_solution.value());

      EXPECT_EQ(or_solution.value().path.size(), capacity + 2);

      total_or += or_solution.value().total_score;

      std::cerr << or_solution.value().total_score << "   ";
    }

    auto greedy_solution = ortools::FindGreedyApproach(data);
    {
      Validate(data, greedy_solution.value());

      EXPECT_EQ(greedy_solution.value().path.size(), capacity + 2);

      total_greedy += greedy_solution.value().total_score;

      std::cerr << greedy_solution.value().total_score << "   ";
    }

    auto tsp_over_greedy_solution =
        TspOverSolution(data, greedy_solution, time_limit);
    {
      Validate(data, tsp_over_greedy_solution.value());

      EXPECT_EQ(tsp_over_greedy_solution.value().path.size(), capacity + 2);

      total_tsp_over_greedy += tsp_over_greedy_solution.value().total_score;

      std::cerr << tsp_over_greedy_solution.value().total_score << "   ";
    }

    auto or_over_greedy_solution =
        OrOverSolution(data, greedy_solution, time_limit);
    {
      Validate(data, or_over_greedy_solution.value());

      EXPECT_EQ(or_over_greedy_solution.value().path.size(), capacity + 2);

      total_or_over_greedy += or_over_greedy_solution.value().total_score;

      std::cerr << or_over_greedy_solution.value().total_score << "   ";
    }

    auto or_over_optimized_greedy_solution =
        OrOverSolution(data, tsp_over_greedy_solution, time_limit);
    {
      Validate(data, or_over_optimized_greedy_solution.value());

      EXPECT_EQ(or_over_optimized_greedy_solution.value().path.size(),
                capacity + 2);

      total_or_over_optimized_greedy +=
          or_over_optimized_greedy_solution.value().total_score;

      std::cerr << or_over_optimized_greedy_solution.value().total_score
                << std::endl;
    }
  }
  std::cerr << "total_or: " << total_or << std::endl;
  std::cerr << "total_greedy: " << total_greedy << std::endl;
  std::cerr << "total_tsp_over_greedy: " << total_tsp_over_greedy << std::endl;
  std::cerr << "total_or_over_greedy: " << total_or_over_greedy << std::endl;
  std::cerr << "total_or_over_optimized_greedy: "
            << total_or_over_optimized_greedy << std::endl;
}
*/

}  // namespace scooters_ops_dispatch::algorithms
