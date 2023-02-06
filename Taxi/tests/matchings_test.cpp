#include <gtest/gtest.h>

#include <algorithm>
#include <cstdlib>
#include <limits>
#include <numeric>
#include <optional>
#include <random>
#include <unordered_set>

#include <boost/graph/bipartite.hpp>
#include <boost/graph/graph_utility.hpp>
#include <boost/graph/iteration_macros.hpp>
#include <boost/graph/transpose_graph.hpp>

#include <userver/logging/log.hpp>

#include "matching-algorithms/matching-algorithms.hpp"

namespace {

namespace algo = matching_algorithms;

using Randomizer = std::mt19937_64;
Randomizer GetRandomizer(
    const std::optional<Randomizer::result_type>& seed = std::nullopt) {
  const auto seed_value = seed.value_or(std::random_device()());
  LOG_WARNING() << "Initialize randomizer with seed " << seed_value;
  return Randomizer(seed_value);
}

template <template <typename> class TAlgo, typename Graph>
std::vector<algo::VertexIdx> FindMatching(const Graph& graph) {
  TAlgo solver(graph);
  return solver.Solve();
}

template <typename TWeight>
void ValidateAlgos(const algo::BipartiteGraph<TWeight>& graph) {
  auto greedy = FindMatching<algo::GreedyMatching>(graph);
  auto hungarian = FindMatching<algo::Hungarian>(graph);
  auto hungarian_sparse = FindMatching<algo::HungarianSparse>(graph);

  EXPECT_TRUE(algo::IsValidMatching(graph, greedy));
  EXPECT_TRUE(algo::IsValidMatching(graph, hungarian));
  EXPECT_TRUE(algo::IsValidMatching(graph, hungarian_sparse));

  auto greedy_size = algo::MatchingSize(graph, greedy);
  auto greedy_cost = algo::MatchingCost(graph, greedy);
  auto hungarian_size = algo::MatchingSize(graph, hungarian);
  auto hungarian_cost = algo::MatchingCost(graph, hungarian);
  auto hungarian_sparse_size = algo::MatchingSize(graph, hungarian_sparse);
  auto hungarian_sparse_cost = algo::MatchingCost(graph, hungarian_sparse);

  EXPECT_EQ(hungarian_size, hungarian_sparse_size);
  EXPECT_EQ(hungarian_cost, hungarian_sparse_cost);

  EXPECT_LE(greedy_size, hungarian_size);
  if (greedy_size == hungarian_size) {
    EXPECT_GE(greedy_cost, hungarian_cost);
  }
}

template <typename TWeight>
algo::BipartiteGraph<TWeight> ShuffleVertices(
    const algo::BipartiteGraph<TWeight>& graph, Randomizer& randomizer) {
  using Graph = algo::BipartiteGraph<TWeight>;

  size_t n_vertices = static_cast<size_t>(boost::num_vertices(graph));
  auto vertex_index = boost::get(boost::vertex_index, graph);
  auto edge_weight = boost::get(boost::edge_weight, graph);

  std::vector<size_t> permutation(n_vertices);
  std::iota(permutation.begin(), permutation.end(), 0);
  std::shuffle(permutation.begin(), permutation.end(), randomizer);

  Graph result(n_vertices);
  BGL_FORALL_EDGES_T(edge, graph, Graph) {
    auto lp_vtx = boost::source(edge, graph);
    auto rp_vtx = boost::target(edge, graph);
    auto lp_idx = static_cast<size_t>(vertex_index[lp_vtx]);
    auto rp_idx = static_cast<size_t>(vertex_index[rp_vtx]);
    lp_idx = permutation[lp_idx];
    rp_idx = permutation[rp_idx];
    boost::add_edge(lp_idx, rp_idx, edge_weight[edge], result);
  }

  return result;
}

template <typename TWeight>
struct GenSettings {
  size_t max_part_size{};
  TWeight min_weight{};
  TWeight max_weight{};
  double isolated_prob{};
};

template <typename TWeight>
algo::BipartiteGraph<TWeight> RandomGraph(const GenSettings<TWeight>& settings,
                                          Randomizer& randomizer) {
  using Graph = algo::BipartiteGraph<TWeight>;

  std::uniform_int_distribution<size_t> part_size_gen(1,
                                                      settings.max_part_size);
  size_t n_left_part = part_size_gen(randomizer);
  size_t n_right_part = part_size_gen(randomizer);

  size_t n_vertices = n_left_part + n_right_part;
  Graph graph(n_vertices);

  std::uniform_int_distribution<size_t> degree_gen(0, n_right_part);
  std::uniform_int_distribution<size_t> adj_vertex_gen(n_left_part,
                                                       n_vertices - 1);
  std::uniform_real_distribution<> weight_gen(settings.min_weight,
                                              settings.max_weight);
  std::bernoulli_distribution isolated_gen(settings.isolated_prob);

  for (size_t vertex = 0; vertex < n_left_part; ++vertex) {
    if (isolated_gen(randomizer)) continue;
    size_t degree = degree_gen(randomizer);
    std::unordered_set<size_t> adj_vertices;
    while (adj_vertices.size() < degree) {
      adj_vertices.insert(adj_vertex_gen(randomizer));
    }
    for (auto adj_vertex : adj_vertices) {
      auto weight = static_cast<TWeight>(weight_gen(randomizer));
      boost::add_edge(vertex, adj_vertex, weight, graph);
    }
  }

  graph = ShuffleVertices(graph, randomizer);
  EXPECT_TRUE(boost::is_bipartite(graph));
  return graph;
}

}  // namespace

TEST(TestMatchingAlgorithms, RealTestCase) {
  using WeightedEdge = algo::WeightedEdge<>;

  std::vector<WeightedEdge> edges = {
      WeightedEdge{0, 3, 280},   WeightedEdge{0, 4, 512},
      WeightedEdge{0, 5, 398},   WeightedEdge{0, 6, 435},
      WeightedEdge{0, 7, 653},   WeightedEdge{0, 8, 828},
      WeightedEdge{0, 9, 866},   WeightedEdge{0, 10, 841},
      WeightedEdge{0, 11, 1066}, WeightedEdge{0, 12, 1080},
      WeightedEdge{0, 13, 907},  WeightedEdge{0, 14, 849},
      WeightedEdge{0, 15, 1092}, WeightedEdge{0, 16, 827},
      WeightedEdge{0, 17, 1006}, WeightedEdge{0, 18, 1137},
      WeightedEdge{0, 19, 1238}, WeightedEdge{0, 20, 921},
      WeightedEdge{0, 21, 954},  WeightedEdge{0, 42, 1064},
      WeightedEdge{1, 35, 591},  WeightedEdge{1, 36, 640},
      WeightedEdge{1, 37, 754},  WeightedEdge{1, 38, 866},
      WeightedEdge{1, 39, 992},  WeightedEdge{1, 40, 1039},
      WeightedEdge{1, 41, 1795}, WeightedEdge{1, 22, 355},
      WeightedEdge{1, 23, 553},  WeightedEdge{1, 24, 475},
      WeightedEdge{1, 25, 545},  WeightedEdge{1, 26, 592},
      WeightedEdge{1, 27, 645},  WeightedEdge{1, 28, 624},
      WeightedEdge{1, 29, 618},  WeightedEdge{1, 30, 636},
      WeightedEdge{1, 31, 407},  WeightedEdge{1, 32, 649},
      WeightedEdge{1, 33, 887},  WeightedEdge{1, 34, 648},
      WeightedEdge{2, 3, 404},   WeightedEdge{2, 4, 795},
      WeightedEdge{2, 5, 705},   WeightedEdge{2, 6, 741},
      WeightedEdge{2, 7, 897},   WeightedEdge{2, 8, 999},
      WeightedEdge{2, 9, 1039},  WeightedEdge{2, 10, 1036},
      WeightedEdge{2, 11, 1404}, WeightedEdge{2, 12, 1240},
      WeightedEdge{2, 13, 1079}, WeightedEdge{2, 14, 1040},
      WeightedEdge{2, 15, 1248}, WeightedEdge{2, 16, 1104},
      WeightedEdge{2, 17, 1215}, WeightedEdge{2, 18, 1311},
      WeightedEdge{2, 19, 1242}, WeightedEdge{2, 20, 1196},
      WeightedEdge{2, 21, 1129}};

  auto graph = algo::CreateGraph(edges);

  ValidateAlgos(graph);
  auto hungarian = FindMatching<algo::Hungarian>(graph);
  auto greedy = FindMatching<algo::GreedyMatching>(graph);
  EXPECT_EQ(algo::MatchingCost(graph, hungarian), 1157);
  EXPECT_EQ(algo::MatchingCost(graph, greedy), 1340);

  // swap vertices 0 and 2 in the graph
  for (auto& edge : edges) {
    if (edge.src == 0)
      edge.src = 2;
    else if (edge.src == 2)
      edge.src = 0;
  }
  auto graph_swapped = algo::CreateGraph(edges);

  ValidateAlgos(graph_swapped);
  auto hungarian_swapped = FindMatching<algo::Hungarian>(graph_swapped);
  auto greedy_swapped = FindMatching<algo::GreedyMatching>(graph_swapped);
  EXPECT_EQ(algo::MatchingCost(graph_swapped, hungarian_swapped), 1157);
  EXPECT_EQ(algo::MatchingCost(graph_swapped, greedy_swapped), 1157);

  // swap vertices 0 and 2 in the matching
  auto mate_0 = static_cast<size_t>(hungarian_swapped[0]);
  auto mate_2 = static_cast<size_t>(hungarian_swapped[2]);
  std::swap(hungarian_swapped[0], hungarian_swapped[2]);
  std::swap(hungarian_swapped[mate_0], hungarian_swapped[mate_2]);

  EXPECT_EQ(hungarian, hungarian_swapped);
}

TEST(TestMatchingAlgorithms, DeficitCases) {
  using Weight = int;
  using WeightedEdge = algo::WeightedEdge<Weight>;

  struct TestCaseGraph {
    std::vector<WeightedEdge> edges{};
    size_t expected_size{};
    Weight expected_cost{};
  };

  std::vector<TestCaseGraph> test_cases;

  TestCaseGraph case_0;
  {
    case_0.edges = {WeightedEdge{1, 0, 1181}, WeightedEdge{2, 0, 329},
                    WeightedEdge{3, 0, 1256}, WeightedEdge{4, 0, 1407},
                    WeightedEdge{5, 0, 875},  WeightedEdge{6, 0, 110},
                    WeightedEdge{7, 0, 652}};
    case_0.expected_size = 1;
    case_0.expected_cost = 110;
  }
  test_cases.push_back(case_0);

  TestCaseGraph case_1;
  {
    case_1.edges = {WeightedEdge{0, 5, 168}, WeightedEdge{0, 6, 348},
                    WeightedEdge{0, 7, 336}, WeightedEdge{0, 8, 1895},
                    WeightedEdge{2, 7, 5}};
    case_1.expected_size = 2;
    case_1.expected_cost = 168 + 5;
  }
  test_cases.push_back(case_1);

  TestCaseGraph case_2;
  {
    case_2.edges = {WeightedEdge{0, 4, 298}, WeightedEdge{0, 5, 265},
                    WeightedEdge{3, 6, 193}};
    case_2.expected_size = 2;
    case_2.expected_cost = 265 + 193;
  }
  test_cases.push_back(case_2);

  const size_t iterations = 100;

  auto randomizer = GetRandomizer();
  for (size_t idx = 0; idx < test_cases.size(); ++idx) {
    const auto& test_case = test_cases[idx];
    auto graph = algo::CreateGraph(test_case.edges);
    for (size_t i = 0; i < iterations; ++i) {
      auto graph_shuffled = ShuffleVertices(graph, randomizer);

      ValidateAlgos(graph_shuffled);
      auto hungarian = FindMatching<algo::Hungarian>(graph_shuffled);
      EXPECT_EQ(algo::MatchingSize(graph_shuffled, hungarian),
                test_case.expected_size);
      EXPECT_EQ(algo::MatchingCost(graph_shuffled, hungarian),
                test_case.expected_cost);

      if (idx == 0) {
        auto greedy = FindMatching<algo::GreedyMatching>(graph_shuffled);
        auto greedy_cost = algo::MatchingCost(graph_shuffled, greedy);
        const auto it =
            std::find_if(test_case.edges.cbegin(), test_case.edges.cend(),
                         [greedy_cost](const WeightedEdge& e) {
                           return e.weight == greedy_cost;
                         });
        ASSERT_NE(it, test_case.edges.cend());
      }
    }
  }
}

TEST(TestMatchingAlgorithms, RandomCases) {
  using Weight = int;

  struct TestCase {
    GenSettings<Weight> settings;
    size_t iterations;
  };

  std::vector<TestCase> test_cases;

  TestCase case_0;
  {
    case_0.settings.max_part_size = 10;
    case_0.settings.min_weight = -10;
    case_0.settings.max_weight = +10;
    case_0.iterations = 1'000;
  }
  test_cases.push_back(case_0);

  TestCase case_1;
  {
    case_1.settings.max_part_size = 50;
    case_1.settings.min_weight = -100;
    case_1.settings.max_weight = +100;
    case_1.iterations = 100;
  }
  test_cases.push_back(case_1);

  TestCase case_2;
  {
    case_2.settings.max_part_size = 100;
    case_2.settings.min_weight = -1'000;
    case_2.settings.max_weight = +1'000;
    case_2.iterations = 50;
  }
  test_cases.push_back(case_2);

  TestCase case_3;
  {
    case_3.settings.max_part_size = 50;
    case_3.settings.min_weight = -100;
    case_3.settings.max_weight = +100;
    case_3.settings.isolated_prob = 0.5;
    case_3.iterations = 100;
  }
  test_cases.push_back(case_3);

  TestCase case_4;
  {
    case_4.settings.max_part_size = 50;
    case_4.settings.min_weight = -100;
    case_4.settings.max_weight = +100;
    case_4.settings.isolated_prob = 0.9;
    case_4.iterations = 100;
  }
  test_cases.push_back(case_4);

  TestCase case_5;
  {
    case_5.settings.max_part_size = 50;
    case_5.settings.min_weight = 0;
    case_5.settings.max_weight = 0;
    case_5.iterations = 100;
  }
  test_cases.push_back(case_5);

  auto randomizer = GetRandomizer();
  for (const auto& test_case : test_cases) {
    for (size_t i = 0; i < test_case.iterations; ++i) {
      auto graph = RandomGraph<Weight>(test_case.settings, randomizer);
      ValidateAlgos(graph);
    }
  }
}

TEST(TestMatchingAlgorithms, RealNumberWeightRandomCases) {
  using Weight = double;

  struct TestCase {
    GenSettings<Weight> settings;
    size_t iterations;
  };

  std::vector<TestCase> test_cases;

  TestCase case_0;
  {
    case_0.settings.max_part_size = 5;
    case_0.settings.min_weight = 0.0;
    case_0.settings.max_weight = 1.0;
    case_0.iterations = 10'000;
  }
  test_cases.push_back(case_0);

  TestCase case_1;
  {
    case_1.settings.max_part_size = 20;
    case_1.settings.min_weight = 200.0;
    case_1.settings.max_weight = 800.0;
    case_1.iterations = 1'000;
  }
  test_cases.push_back(case_1);

  TestCase case_2;
  {
    case_2.settings.max_part_size = 50;
    case_2.settings.min_weight = 200.0;
    case_2.settings.max_weight = 800.0;
    case_2.iterations = 100;
  }
  test_cases.push_back(case_2);

  auto randomizer = GetRandomizer();
  for (const auto& test_case : test_cases) {
    for (size_t i = 0; i < test_case.iterations; ++i) {
      auto graph = RandomGraph<Weight>(test_case.settings, randomizer);
      auto hungarian = FindMatching<algo::Hungarian>(graph);
      auto hungarian_sparse = FindMatching<algo::HungarianSparse>(graph);

      auto hungarian_size = algo::MatchingSize(graph, hungarian);
      auto hungarian_cost = algo::MatchingCost(graph, hungarian);
      auto hungarian_sparse_size = algo::MatchingSize(graph, hungarian_sparse);
      auto hungarian_sparse_cost = algo::MatchingCost(graph, hungarian_sparse);

      EXPECT_EQ(hungarian_size, hungarian_sparse_size);
      EXPECT_DOUBLE_EQ(hungarian_cost, hungarian_sparse_cost);
    }
  }
}

TEST(TestMatchingAlgorithms, TransposeCases) {
  using Weight = int;
  using Graph = algo::BipartiteGraph<Weight>;

  GenSettings<Weight> settings;
  settings.max_part_size = 20;
  settings.min_weight = -100;
  settings.max_weight = +100;

  const size_t iterations = 1'000;

  auto randomizer = GetRandomizer();
  for (size_t i = 0; i < iterations; ++i) {
    auto graph = RandomGraph<Weight>(settings, randomizer);

    Graph graph_transposed;
    boost::transpose_graph(graph, graph_transposed);

    auto hungarian = FindMatching<algo::Hungarian>(graph);
    auto hungarian_transposed = FindMatching<algo::Hungarian>(graph_transposed);

    EXPECT_TRUE(algo::IsValidMatching(graph, hungarian));
    EXPECT_TRUE(algo::IsValidMatching(graph_transposed, hungarian_transposed));

    EXPECT_EQ(algo::MatchingSize(graph, hungarian),
              algo::MatchingSize(graph_transposed, hungarian_transposed));
    EXPECT_EQ(algo::MatchingCost(graph, hungarian),
              algo::MatchingCost(graph_transposed, hungarian_transposed));
  }
}
