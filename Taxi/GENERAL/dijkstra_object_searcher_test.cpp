#include <graph/dijkstra_object_searcher.hpp>
#include <graph/types.hpp>

#include <functional>
#include <set>

#include <userver/engine/task/task.hpp>
#include <userver/utils/datetime.hpp>

#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <graph/tests/graph_fixture.hpp>
#include "graph_loader_fixture.hpp"

namespace graph::test {

namespace {

class SimpleSearchRules : public NTaxiExternal::NGraphSearch2::ISearchActions {
 public:
  virtual NTaxiExternal::NGraphSearch2::TEdgeDiscoverResult OnDiscoveredEdge(
      const NTaxiExternal::NGraph2::TGraph& graph,
      NTaxiExternal::NGraph2::TEdge&& edge,
      NTaxiExternal::NGraphSearch2::TWeight current_distance,
      NTaxiExternal::NGraph2::TEdge&& precedingEdge) {
    std::ignore = current_distance;
    std::ignore = precedingEdge;
    std::ignore = graph;
    std::ignore = edge;

    if (edge_count_ > edge_limit_) {
      return NTaxiExternal::NGraphSearch2::TEdgeDiscoverResult{true, 0};
    }

    ++edge_count_;
    return NTaxiExternal::NGraphSearch2::TEdgeDiscoverResult{false, 1};
  }

  virtual void OnPassedEdge(
      const NTaxiExternal::NGraph2::TGraph& graph,
      NTaxiExternal::NGraph2::TEdge&& edge,
      NTaxiExternal::NGraphSearch2::TWeight current_distance) {
    std::ignore = graph;
    std::ignore = edge;
    std::ignore = current_distance;
    // nothing to do.
  }

 private:
  std::size_t edge_count_ = 0;
  std::size_t edge_limit_ = 10000;
};

using Searcher = graph::DijkstraObjectSearcher<std::string, std::string>;
using StoringSearcher =
    graph::DijkstraObjectStoringSearcher<std::string, std::string>;

using SurgeSearcher = graph::DijkstraSurgeSearcher;

}  // namespace

using DijkstraSearchFixture = graph::test::GraphTestFixtureLegacy;

TEST_F(DijkstraSearchFixture, TestExceptionWithoutEdgeStorage) {
  RunInCoro([] {
    graph::GraphLoader loader;
    auto graph = loader.LoadGraph(kTestGraphDataDir,
                                  graph::configs::kPopulateMemoryMapName);

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    bool exceptionCaught = false;
    try {
      StoringSearcher searcher(*graph, nullptr, nullptr, obj_index);
    } catch (const std::exception&) {
      exceptionCaught = true;
    }

    ASSERT_TRUE(exceptionCaught);
  });
}

TEST_F(DijkstraSearchFixture, TestSearch) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index);
    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    const auto& results = searcher.GetResults();
    ASSERT_EQ(results.size(), 1ull);
    ASSERT_EQ(results[0].value, kValue);
    ASSERT_EQ(results[0].key, "uuid");
    ASSERT_EQ(results[0].position.position, pos.position);
    ASSERT_EQ(results[0].position.edge_id, pos.edge_id);
  });
}

TEST_F(DijkstraSearchFixture, TestSurgeSearchSimple) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphSurgeZoneIndex zone_index(*graph);

    // Visualization:
    // https://wiki.yandex-team.ru/users/mesyarik/test-na-poisk-shestiugolnikov/

    // aurora, zone id = 0
    zone_index.AddHexagonalZone({37.642694 * lon, 55.734508 * lat}, 0.008,
                                0.004);
    // red rose, zone_id = 1
    zone_index.AddHexagonalZone({37.588513 * lon, 55.733958 * lat}, 0.005);

    ::geometry::Position source_pos{37.615600 * lon, 55.733312 * lat};
    auto pos = graph->NearestEdge(source_pos);
    ASSERT_EQ(pos.edge_id, EdgeId{91650u});

    const int kStopReason = 100500;
    std::vector<::geometry::Position> expected_found_positions = {
        {37.6382606 * lon, 55.7314192 * lat},
        {37.59212878 * lon, 55.73635553 * lat}};

    std::vector<::geometry::Position> found_positions;

    SearchSettings settings;
    settings.max_visited_edges = 999'999'999;

    SurgeSearcher searcher(
        *graph, nullptr, nullptr,
        [&graph, &found_positions](
            const SurgeSearcher::SearchResult& search_result) -> int {
          const auto pos = search_result.position;
          const auto point = graph->GetCoords(pos);
          found_positions.push_back(point);
          if (found_positions.size() == 2) {
            return kStopReason;
          }
          return 0;
        },
        zone_index);

    searcher.SetSettings(settings);

    ASSERT_EQ(graph::StopReason{kStopReason}, searcher.Search(pos));
    ASSERT_EQ(searcher.GetVisitedEdgesCount(), 981);

    ASSERT_EQ(found_positions.size(), 2);
    for (size_t i = 0; i < 2; ++i) {
      const auto& found = found_positions[i];
      const auto& expected = expected_found_positions[i];
      ASSERT_TRUE(std::fabs(found.GetLongitudeAsDouble() -
                            expected.GetLongitudeAsDouble()) < 1e-6);
      ASSERT_TRUE(std::fabs(found.GetLatitudeAsDouble() -
                            expected.GetLatitudeAsDouble()) < 1e-6);
    }
  });
}

TEST_F(DijkstraSearchFixture, TestFastSurgeSearchSimple) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphSurgeZoneIndex zone_index(*graph);

    // Visualization:
    // https://wiki.yandex-team.ru/users/mesyarik/test-na-poisk-shestiugolnikov/

    // aurora, zone id = 0
    zone_index.AddHexagonalZone({37.642694 * lon, 55.734508 * lat}, 0.008,
                                0.004);
    // red rose, zone_id = 1
    zone_index.AddHexagonalZone({37.588513 * lon, 55.733958 * lat}, 0.005);

    ::geometry::Position source_pos{37.615600 * lon, 55.733312 * lat};
    auto pos = graph->NearestEdge(source_pos);
    ASSERT_EQ(pos.edge_id, EdgeId{91650u});

    const int kStopReason = 100500;
    std::vector<::geometry::Position> expected_found_positions = {
        {37.6382606 * lon, 55.7314192 * lat},
        {37.59212878 * lon, 55.73635553 * lat}};

    std::vector<::geometry::Position> found_positions;

    SurgeSearcher searcher(
        *graph, nullptr, nullptr,
        [&graph, &found_positions](
            const SurgeSearcher::SearchResult& search_result) -> int {
          const auto pos = search_result.position;
          const auto point = graph->GetCoords(pos);
          found_positions.push_back(point);
          if (found_positions.size() == 2) {
            return kStopReason;
          }
          return 0;
        },
        zone_index, {}, {});

    ASSERT_EQ(graph::StopReason{kStopReason}, searcher.Search(pos));
    ASSERT_EQ(searcher.GetVisitedEdgesCount(), 984);

    ASSERT_EQ(found_positions.size(), 2);
    for (size_t i = 0; i < 2; ++i) {
      const auto& found = found_positions[i];
      const auto& expected = expected_found_positions[i];
      ASSERT_TRUE(std::fabs(found.GetLongitudeAsDouble() -
                            expected.GetLongitudeAsDouble()) < 1e-6);
      ASSERT_TRUE(std::fabs(found.GetLatitudeAsDouble() -
                            expected.GetLatitudeAsDouble()) < 1e-6);
    }
  });
}

TEST_F(DijkstraSearchFixture, TestFastSurgeSearchWithMaxTime) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphSurgeZoneIndex zone_index(*graph);

    ::geometry::Position zone_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        zone_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    zone_index.AddHexagonalZone(zone_pos, 0.001, 0.001);

    ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    SearchSettings settings;
    settings.max_time = SecondsDouble{5.0};

    bool found_zone = false;

    SurgeSearcher searcher(
        *graph, nullptr, nullptr,
        [&found_zone](const SurgeSearcher::SearchResult&) -> int {
          found_zone = true;
          return 0;
        },
        zone_index, settings, {});

    ASSERT_EQ(SurgeSearcher::StopBecauseDone,
              searcher.Search(start_search_pos));

    ASSERT_FALSE(found_zone);
    EXPECT_GT(searcher.GetSkippedEdgesByTimeOrDistance(), 0);
  });
}

TEST_F(DijkstraSearchFixture, TestFastSurgeSearchChangingSettings) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphSurgeZoneIndex zone_index(*graph);

    zone_index.AddHexagonalZone({37.641875 * lon, 55.737519 * lat}, 0.001,
                                0.001);
    zone_index.AddHexagonalZone({37.641666 * lon, 55.738072 * lat}, 0.001,
                                0.001);
    zone_index.AddHexagonalZone({37.631737 * lon, 55.746784 * lat}, 0.001,
                                0.001);

    ::geometry::Position search_pos{37.642459 * lon, 55.736235 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    {
      SearchSettings start_settings;

      size_t results = 0;
      SurgeSearcher searcher(
          *graph, nullptr, nullptr,
          [&results, &searcher](const SurgeSearcher::SearchResult&) -> int {
            ++results;
            SearchSettings settings;
            settings.reversed_edges_mode = true;
            settings.max_time = SecondsDouble{150.0};
            EXPECT_TRUE(searcher.SetSettings(settings));
            return 0;
          },
          zone_index, start_settings, {});
      ASSERT_EQ(SurgeSearcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(results, 2);
    }

    {
      SearchSettings start_settings;
      start_settings.max_time = SecondsDouble{150.0};

      size_t results = 0;
      SurgeSearcher searcher(
          *graph, nullptr, nullptr,
          [&results, &searcher](const SurgeSearcher::SearchResult&) -> int {
            ++results;
            SearchSettings settings;
            EXPECT_FALSE(searcher.SetSettings(settings));
            return 0;
          },
          zone_index, start_settings, {});
      ASSERT_EQ(SurgeSearcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(results, 2);
    }

    {
      SearchSettings start_settings;

      size_t results = 0;
      SurgeSearcher searcher(
          *graph, nullptr, nullptr,
          [&results, &searcher](const SurgeSearcher::SearchResult&) -> int {
            ++results;
            SearchSettings settings;
            settings.max_path_length = 1000.0 * geometry::meters;
            EXPECT_TRUE(searcher.SetSettings(settings));
            return 0;
          },
          zone_index, start_settings, {});
      ASSERT_EQ(SurgeSearcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(results, 2);
    }

    {
      SearchSettings start_settings;
      start_settings.max_path_length = 1000.0 * geometry::meters;

      size_t results = 0;
      SurgeSearcher searcher(
          *graph, nullptr, nullptr,
          [&results, &searcher](const SurgeSearcher::SearchResult&) -> int {
            ++results;
            SearchSettings settings;
            EXPECT_FALSE(searcher.SetSettings(settings));
            return 0;
          },
          zone_index, start_settings, {});
      ASSERT_EQ(SurgeSearcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(results, 2);
    }
  });
}

TEST_F(DijkstraSearchFixture, TestFastSurgeSearchFromMultiplePositions) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphSurgeZoneIndex zone_index(*graph);

    zone_index.AddHexagonalZone({37.636418 * lon, 55.735999 * lat}, 0.001,
                                0.001);
    zone_index.AddHexagonalZone({37.638230 * lon, 55.731601 * lat}, 0.001,
                                0.001);
    zone_index.AddHexagonalZone({37.639319 * lon, 55.733164 * lat}, 0.001,
                                0.001);

    ::geometry::Position first_start_pos{37.636170 * lon, 55.735305 * lat};
    auto first_start = graph->NearestEdge(first_start_pos);
    EXPECT_NE(kUndefined, first_start.edge_id);

    ::geometry::Position second_search_pos{37.638901 * lon, 55.731910 * lat};
    auto second_start = graph->NearestEdge(second_search_pos);
    EXPECT_NE(kUndefined, second_start.edge_id);

    {
      SearchSettings settings;
      settings.max_visited_edges = 50;

      size_t found_zones = 0;

      SurgeSearcher searcher(
          *graph, nullptr, nullptr,
          [&found_zones](const SurgeSearcher::SearchResult&) -> int {
            ++found_zones;
            return 0;
          },
          zone_index, settings, {});
      ASSERT_EQ(SurgeSearcher::StopBecauseDone, searcher.Search(second_start));

      ASSERT_EQ(found_zones, 1);

      // just check that there is no error when searching with empty container
      ASSERT_EQ(SurgeSearcher::StopBecauseDone,
                searcher.Search(std::vector<PositionOnEdge>{}));
    }

    {
      SearchSettings settings;
      settings.max_visited_edges = 50;

      size_t found_zones = 0;

      SurgeSearcher searcher(
          *graph, nullptr, nullptr,
          [&found_zones](const SurgeSearcher::SearchResult&) -> int {
            ++found_zones;
            return 0;
          },
          zone_index, settings, {});

      ASSERT_EQ(SurgeSearcher::StopBecauseDone,
                searcher.Search({second_start, first_start}));
      ASSERT_EQ(found_zones, 2);
    }
  });
}

TEST_F(DijkstraSearchFixture, TestSearchWithLeewaysCount) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index);
    graph::SearchSettings settings;
    settings.enable_leeways_count_mode = true;
    searcher.SetSettings(settings);

    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    const auto& results = searcher.GetResults();
    ASSERT_EQ(results.size(), 1ull);
    ASSERT_EQ(results[0].leeway, std::nullopt);
  });
}

TEST_F(DijkstraSearchFixture, TestSearchWithUserStopReason) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();
    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    ::geometry::Position source_pos2{37.641551 * lon, 55.730629 * lat};
    const auto pos2 = graph->NearestEdge(
        source_pos2, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::ProperSide);
    ASSERT_EQ(pos2.edge_id, EdgeId{221126u});

    ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);
    const std::string kValue{"test"};
    const std::string kValue2{"test2"};
    const int kStopReason = 100500;

    obj_index.Insert("uuid", kValue, pos);
    obj_index.Insert("uuid2", kValue2, pos2);

    std::set<std::string> found_values;
    Searcher searcher(
        *graph, nullptr, nullptr,
        [&kValue,
         &found_values](const Searcher::SearchResult& search_result) -> int {
          found_values.insert(search_result.value);
          if (search_result.value == kValue) {
            return kStopReason;
          }

          return 0;
        },
        obj_index);

    ASSERT_EQ(graph::StopReason{kStopReason},
              searcher.Search(start_search_pos.edge_id));
    ASSERT_EQ(found_values, std::set<std::string>{kValue});
  });
}

TEST_F(DijkstraSearchFixture, TestGetRouteInfo) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    const ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    const ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    const auto start_search_pos = graph->NearestEdge(
        search_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::ProperSide);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index);
    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    const auto route_info = searcher.GetRouteInfo(pos);
    ASSERT_TRUE(route_info);

    ASSERT_TRUE(route_info->distance);
    ASSERT_NEAR(307., (*route_info->distance).value(), 2);

    ASSERT_TRUE(route_info->has_toll_roads);
    ASSERT_EQ(*route_info->has_toll_roads, false);

    const auto empty_route_info = searcher.GetRouteInfo(PositionOnEdge());
    ASSERT_FALSE(empty_route_info);
  });
}

TEST_F(DijkstraSearchFixture, TestGetPathLength) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    const ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    const ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    const auto start_search_pos = graph->NearestEdge(
        search_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::ProperSide);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index);
    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    const auto path_length_to_found_edge = searcher.GetPathLength(pos);
    ASSERT_TRUE(path_length_to_found_edge);
    ASSERT_NEAR(307., path_length_to_found_edge->value(), 2);

    const auto path_length_to_not_found_edge =
        searcher.GetPathLength(PositionOnEdge());
    ASSERT_FALSE(path_length_to_not_found_edge);
  });
}

TEST_F(DijkstraSearchFixture, TestPathLengthInCallback) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    const ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    const ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    const auto start_search_pos = graph->NearestEdge(
        search_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::ProperSide);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    std::vector<std::optional<::geometry::Distance>> found_lengthes;
    Searcher searcher{
        *graph, nullptr, nullptr,
        [&found_lengthes](const Searcher::SearchResult& search_result) -> int {
          found_lengthes.emplace_back(search_result.PathLength());
          return 0;
        },
        obj_index};

    ASSERT_EQ(Searcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    ASSERT_EQ(1u, found_lengthes.size());
    const auto& found_length = found_lengthes.front();
    ASSERT_TRUE(found_length);
    ASSERT_NEAR(307., found_length->value(), 2.);
  });
}

TEST_F(DijkstraSearchFixture, TestGetPath) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    const ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    const ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    const auto start_search_pos = graph->NearestEdge(
        search_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::ProperSide);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index);

    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos));

    const auto path_to_found_edge = searcher.GetPath(pos);

    ASSERT_TRUE(path_to_found_edge);
    /* for debug needs
    for (auto segment : *path_to_found_edge) {
      std::cout << segment.edge_id << ' ' << segment.start << ' '
            << segment.end << '\n';
    }
    */
    ASSERT_GE(
        std::distance(path_to_found_edge->begin(), path_to_found_edge->end()),
        2);

    const auto start_segment = *path_to_found_edge->begin();
    const auto finish_segment = *path_to_found_edge->rbegin();

    // Check last and first edge of path
    // end always is where found driver is
    EXPECT_EQ(finish_segment.edge_id, pos.edge_id);
    // start is always at the start
    EXPECT_EQ(start_segment.edge_id, start_search_pos.edge_id);

    ASSERT_DOUBLE_EQ(start_segment.start, start_search_pos.position);
    ASSERT_DOUBLE_EQ(start_segment.end, 1.0);
    ASSERT_DOUBLE_EQ(finish_segment.start, 0.0);
    ASSERT_DOUBLE_EQ(finish_segment.end, pos.position);

    const auto path_to_not_found_edge = searcher.GetPath(PositionOnEdge());
    ASSERT_FALSE(path_to_not_found_edge);
  });
}

TEST_F(DijkstraSearchFixture, TestGetPathReverseEdges) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    const ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto start_search_pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(start_search_pos.edge_id, EdgeId{220875u});

    const ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    const auto pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, pos.edge_id);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index);
    graph::SearchSettings settings;
    settings.reversed_edges_mode = true;
    searcher.SetSettings(settings);

    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos));

    const auto path_to_found_edge = searcher.GetPath(pos);

    ASSERT_TRUE(path_to_found_edge);
    /* for debug needs
    for (auto segment : *path_to_found_edge) {
    std::cout << segment.edge_id << ' ' << segment.start << ' '
              << segment.end << '\n';
    }
    */
    ASSERT_GE(
        std::distance(path_to_found_edge->begin(), path_to_found_edge->end()),
        2);

    const auto start_segment = *path_to_found_edge->begin();
    const auto finish_segment = *path_to_found_edge->rbegin();

    // Check last and first edge of path
    // end always is where found driver is
    EXPECT_EQ(finish_segment.edge_id, pos.edge_id);
    // start is always at the start
    EXPECT_EQ(start_segment.edge_id, start_search_pos.edge_id);
    ASSERT_DOUBLE_EQ(start_segment.start, start_search_pos.position);
    ASSERT_DOUBLE_EQ(start_segment.end, 0.0);
    ASSERT_DOUBLE_EQ(finish_segment.start, 1.0);
    ASSERT_DOUBLE_EQ(finish_segment.end, pos.position);
  });
}

TEST_F(DijkstraSearchFixture, TestPathInCallback) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    const ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    const ::geometry::Position search_pos{37.662077 * lon, 55.706958 * lat};
    const auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);
    // lets not start search on the same edge as driver is.
    // nothing wrong in real life, just not a good test case
    EXPECT_NE(pos.edge_id, start_search_pos.edge_id);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    std::vector<std::optional<Route>> found_pathes;
    Searcher searcher{
        *graph, nullptr, nullptr,
        [&found_pathes](const Searcher::SearchResult& search_result) -> int {
          found_pathes.emplace_back(search_result.Path());
          return 0;
        },
        obj_index};

    ASSERT_EQ(Searcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    ASSERT_EQ(1u, found_pathes.size());
    const auto& found_path = found_pathes.front();
    ASSERT_TRUE(found_path);
    ASSERT_GE(std::distance(found_path->begin(), found_path->end()), 2);
  });
}

TEST_F(DijkstraSearchFixture, TestGetEdgesVisitedCount) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    const ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    const ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    const auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index);
    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    const size_t visited_edges_count = searcher.GetVisitedEdgesCount();
    ASSERT_GE(visited_edges_count, 0);
  });
}

TEST_F(DijkstraSearchFixture, TestSearchSimple) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);

    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    SimpleSearchRules rules;
    NTaxiExternal::NGraphSearch2::TDijkstraSearcher searcher(
        *graph->GetRawGraph(), rules);
    searcher.Search(static_cast<NTaxiExternal::NGraph2::TId>(pos.edge_id));
  });
}

TEST_F(DijkstraSearchFixture, TestSetSettings) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    // somewhere in Kuntsevo
    ::geometry::Position first{37.408094 * lon, 55.733913 * lat};
    auto pos_first = graph->NearestEdge(first);

    // somewhere in Ismaylovo
    ::geometry::Position second{37.815232 * lon, 55.793580 * lat};
    auto pos_second = graph->NearestEdge(second);

    const std::string kValueFirst{"test1"};
    const std::string kValueSecond{"test2"};
    obj_index.Insert("uuid1", kValueFirst, pos_first);
    obj_index.Insert("uuid2", kValueSecond, pos_second);

    // near to driver 2 but very far from driver 1
    const ::geometry::Position search_pos{37.806869 * lon, 55.793456 * lat};
    const auto start_search_pos = graph->NearestEdge(search_pos);

    // Now search without edges limit and hope to find both drivers
    int found_drivers = 0;
    Searcher searcher{*graph, nullptr, nullptr,
                      [&found_drivers](const Searcher::SearchResult&) -> int {
                        ++found_drivers;
                        return 0;
                      },
                      obj_index};

    ASSERT_EQ(Searcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    ASSERT_EQ(found_drivers, 2);

    // Now add edges limit and hope to find only one
    {
      found_drivers = 0;

      graph::SearchSettings settings;
      settings.max_visited_edges = 10'000;
      searcher.SetSettings(settings);

      ASSERT_EQ(Searcher::StopByStopCondition,
                searcher.Search(start_search_pos.edge_id));
      ASSERT_EQ(found_drivers, 1);
    }

    // Now set original settings and hope to find both drivers
    {
      found_drivers = 0;
      searcher.SetSettings(graph::SearchSettings{});

      ASSERT_EQ(Searcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));
      ASSERT_EQ(found_drivers, 2);
    }

    // Now set distance limit in meters and hope to find only one again
    {
      found_drivers = 0;

      graph::SearchSettings settings;
      settings.max_path_length = 2000.0 * ::geometry::meters;
      searcher.SetSettings(settings);

      ASSERT_EQ(Searcher::StopByPathGeolength,
                searcher.Search(start_search_pos.edge_id));
      ASSERT_EQ(found_drivers, 1);
    }

    // Now set original settings again and hope to find both drivers
    {
      found_drivers = 0;
      searcher.SetSettings(graph::SearchSettings{});

      ASSERT_EQ(Searcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));
      ASSERT_EQ(found_drivers, 2);
    }

    // Now add custom stop condition by distance and hope to find only one
    {
      found_drivers = 0;

      std::function<bool(EdgeId, detail::Weight)> stop_condition =
          [](EdgeId, detail::Weight weight) { return weight > 1'000; };

      searcher.SetStopCondition(stop_condition);

      ASSERT_EQ(Searcher::StopByStopCondition,
                searcher.Search(start_search_pos.edge_id));
      ASSERT_EQ(found_drivers, 1);
    }
  });
}

TEST_F(DijkstraSearchFixture, TestCustomSearchSettings) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    // somewhere in Kuntsevo
    ::geometry::Position first{37.408094 * lon, 55.733913 * lat};
    auto pos_first = graph->NearestEdge(first);

    // somewhere in Ismaylovo
    ::geometry::Position second{37.815232 * lon, 55.793580 * lat};
    auto pos_second = graph->NearestEdge(second);

    const std::string kValueFirst{"test1"};
    const std::string kValueSecond{"test2"};
    obj_index.Insert("uuid1", kValueFirst, pos_first);
    obj_index.Insert("uuid2", kValueSecond, pos_second);

    // near to driver 2 but very far from driver 1
    const ::geometry::Position search_pos{37.806869 * lon, 55.793456 * lat};
    const auto start_search_pos = graph->NearestEdge(search_pos);

    // Now search without edges limit and hope to find both drivers
    {
      int found_drivers = 0;

      Searcher searcher{*graph, nullptr, nullptr,
                        [&found_drivers](const Searcher::SearchResult&) -> int {
                          ++found_drivers;
                          return 0;
                        },
                        obj_index};

      ASSERT_EQ(Searcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(found_drivers, 2);
    }

    // Now add edges limit and hope to find only one
    {
      int found_drivers = 0;

      graph::SearchSettings settings;
      settings.max_visited_edges = 10'000;

      Searcher searcher{*graph,
                        nullptr,
                        nullptr,
                        [&found_drivers](const Searcher::SearchResult&) -> int {
                          ++found_drivers;
                          return 0;
                        },
                        obj_index,
                        settings};

      ASSERT_EQ(Searcher::StopByStopCondition,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(found_drivers, 1);
    }

    // Now add custom stop condition by distance and hope to find only one
    {
      int found_drivers = 0;

      std::function<bool(EdgeId, detail::Weight)> stop_condition =
          [](EdgeId, detail::Weight weight) { return weight > 1'000; };

      Searcher searcher{*graph, nullptr, nullptr,
                        [&found_drivers](const Searcher::SearchResult&) -> int {
                          ++found_drivers;
                          return 0;
                        },
                        obj_index};

      searcher.SetStopCondition(stop_condition);

      ASSERT_EQ(Searcher::StopByStopCondition,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(found_drivers, 1);
    }
  });
}

TEST_F(DijkstraSearchFixture, TestSearchWithUserCallbackWithExceptions) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();
    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    ::geometry::Position source_pos2{37.641551 * lon, 55.730629 * lat};
    const auto pos2 = graph->NearestEdge(
        source_pos2, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos2.edge_id, EdgeId{221133});

    ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    const auto start_search_pos = graph->NearestEdge(
        search_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    const std::string kValue{"test"};
    const std::string kValue2{"test2"};

    obj_index.Insert("uuid", kValue, pos);
    obj_index.Insert("uuid2", kValue2, pos2);

    std::set<std::string> found_values;
    Searcher searcher(
        *graph, nullptr, nullptr,
        [&kValue, &kValue2,
         &found_values](const Searcher::SearchResult& search_result) -> int {
          found_values.insert(search_result.value);

          if (search_result.value == kValue) {
            throw std::runtime_error("I hate exceptions :)");
          }
          if (search_result.value == kValue2) {
            throw 42;
          }

          return 0;
        },
        obj_index);

    ASSERT_EQ(Searcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));
    const auto exp_values = std::set<std::string>{kValue, kValue2};
    ASSERT_EQ(found_values, exp_values);
  });
}

TEST_F(DijkstraSearchFixture, TestSearchFromMultiplePositions) {
  // Test description:
  // https://wiki.yandex-team.ru/users/mesyarik/Test-na-proexavshego-voditelja-i-neskolko-startovyx-reber/
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position drove_past_pos{37.636700 * lon, 55.731203 * lat};
    auto drove_past_driver = graph->NearestEdge(drove_past_pos);

    ::geometry::Position middle_pos{37.638230 * lon, 55.731601 * lat};
    auto middle_driver = graph->NearestEdge(middle_pos);

    ::geometry::Position backward_pos{37.639319 * lon, 55.732164 * lat};
    auto backward_driver = graph->NearestEdge(backward_pos);

    ::geometry::Position first_start_pos{37.637170 * lon, 55.731305 * lat};
    auto first_start = graph->NearestEdge(first_start_pos);
    EXPECT_NE(kUndefined, first_start.edge_id);

    ::geometry::Position second_search_pos{37.638901 * lon, 55.731910 * lat};
    auto second_start = graph->NearestEdge(second_search_pos);
    EXPECT_NE(kUndefined, second_start.edge_id);

    obj_index.Insert("clid_uuid_0", "drove_past", drove_past_driver);
    obj_index.Insert("clid_uuid_1", "middle", middle_driver);
    obj_index.Insert("clid_uuid_2", "backward", backward_driver);

    graph::SearchSettings settings;
    settings.max_visited_edges = 50;
    settings.reversed_edges_mode = true;

    size_t found_drivers = 0;
    using Searcher = graph::DijkstraObjectSearcher<std::string, std::string>;
    Searcher searcher{*graph,
                      nullptr,
                      nullptr,
                      [&found_drivers](const Searcher::SearchResult&) -> int {
                        ++found_drivers;
                        return 0;
                      },
                      obj_index,
                      settings};

    ASSERT_EQ(Searcher::StopByStopCondition, searcher.Search(second_start));
    ASSERT_EQ(found_drivers, 1);

    found_drivers = 0;
    ASSERT_EQ(Searcher::StopByStopCondition,
              searcher.Search({first_start, second_start}));
    ASSERT_EQ(found_drivers, 2);

    // just check that there is no error when searching with empty container
    ASSERT_EQ(Searcher::StopBecauseDone,
              searcher.Search(std::vector<PositionOnEdge>{}));
  });
}

TEST_F(DijkstraSearchFixture, TestSearchWithVisualization) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    EXPECT_EQ(pos.edge_id, EdgeId{220875u});

    ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index,
                             ObjectSearchVisualizationSettings{});
    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    const auto& results = searcher.GetResults();
    ASSERT_EQ(results.size(), 1ull);
    ASSERT_EQ(results[0].value, kValue);
    ASSERT_EQ(results[0].key, "uuid");
    ASSERT_EQ(results[0].position.position, pos.position);
    ASSERT_EQ(results[0].position.edge_id, pos.edge_id);
    ASSERT_FALSE(searcher.GetVisualization().empty());
  });
}

TEST_F(DijkstraSearchFixture, TestFastSearch) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::ProperSide);

    ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    SearchSettings settings;
    settings.reversed_edges_mode = true;

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index, settings,
                             FastDijkstraSearcherEnabler{});
    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    const auto& results = searcher.GetResults();
    ASSERT_EQ(results.size(), 1ull);
    ASSERT_EQ(results[0].value, kValue);
    ASSERT_EQ(results[0].key, "uuid");
    ASSERT_EQ(results[0].position.position, pos.position);
    ASSERT_EQ(results[0].position.edge_id, pos.edge_id);
  });
}

TEST_F(DijkstraSearchFixture, TestFastSearchWithLeewaysCount) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::ProperSide);

    ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    graph::SearchSettings settings;
    settings.enable_leeways_count_mode = true;
    settings.reversed_edges_mode = true;

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index, settings,
                             FastDijkstraSearcherEnabler{});

    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    const auto& results = searcher.GetResults();
    ASSERT_EQ(results.size(), 1ull);
    ASSERT_EQ(results[0].leeway, std::nullopt);
  });
}

TEST_F(DijkstraSearchFixture, TestSearchWithMaxTime) {
  // Test that SearchSettings.max_time parameters works
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
    const auto pos = graph->NearestEdge(
        source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
        100 * geometry::meter, Graph::RoadSideFilter::WrongSide);
    ASSERT_EQ(pos.edge_id, EdgeId{220875u});

    ::geometry::Position search_pos{37.642077 * lon, 55.736958 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    const std::string kValue{"test"};
    obj_index.Insert("uuid", kValue, pos);

    SearchSettings settings;
    settings.max_time = SecondsDouble{5.0};

    StoringSearcher searcher(*graph, nullptr, nullptr, obj_index, settings,
                             FastDijkstraSearcherEnabler{});
    ASSERT_EQ(StoringSearcher::StopBecauseDone,
              searcher.Search(start_search_pos.edge_id));

    const auto& results = searcher.GetResults();
    ASSERT_TRUE(results.empty());
    EXPECT_GT(searcher.GetSkippedEdgesByTimeOrDistance(), 0);
  });
}

TEST_F(DijkstraSearchFixture, TestChangingSettings) {
  RunInCoro([] {
    using ::geometry::lat;
    using ::geometry::lon;
    auto graph = Graph();

    ASSERT_NE(nullptr, graph);

    graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);

    {
      ::geometry::Position source_pos{37.641875 * lon, 55.737519 * lat};
      const auto pos = graph->NearestEdge(
          source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
          100 * geometry::meter, Graph::RoadSideFilter::ProperSide);
      const std::string kValue{"test1"};
      obj_index.Insert("uuid1", kValue, pos);
    }

    {
      ::geometry::Position source_pos{37.641666 * lon, 55.738072 * lat};
      const auto pos = graph->NearestEdge(
          source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
          100 * geometry::meter, Graph::RoadSideFilter::ProperSide);
      const std::string kValue{"test2"};
      obj_index.Insert("uuid2", kValue, pos);
    }

    {
      ::geometry::Position source_pos{37.631737 * lon, 55.746784 * lat};
      const auto pos = graph->NearestEdge(
          source_pos, EdgeAccess::kUnknown, EdgeCategory::kFieldRoads,
          100 * geometry::meter, Graph::RoadSideFilter::ProperSide);
      const std::string kValue{"test3"};
      obj_index.Insert("uuid3", kValue, pos);
    }

    ::geometry::Position search_pos{37.642459 * lon, 55.736235 * lat};
    auto start_search_pos = graph->NearestEdge(search_pos);
    EXPECT_NE(kUndefined, start_search_pos.edge_id);

    {
      SearchSettings start_settings;
      start_settings.reversed_edges_mode = true;

      size_t results = 0;
      Searcher searcher(
          *graph, nullptr, nullptr,
          [&](const detail::SearchResult&) -> int {
            results++;
            SearchSettings settings;
            settings.reversed_edges_mode = true;
            settings.max_time = SecondsDouble{150.0};
            EXPECT_TRUE(searcher.SetSettings(settings));
            return 0;
          },
          obj_index, start_settings, FastDijkstraSearcherEnabler{});
      ASSERT_EQ(StoringSearcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(results, 2);
    }

    {
      SearchSettings start_settings;
      start_settings.max_time = SecondsDouble{150.0};
      start_settings.reversed_edges_mode = true;

      size_t results = 0;
      Searcher searcher(
          *graph, nullptr, nullptr,
          [&](const detail::SearchResult&) -> int {
            results++;
            SearchSettings settings;
            settings.reversed_edges_mode = true;
            EXPECT_FALSE(searcher.SetSettings(settings));
            return 0;
          },
          obj_index, start_settings, FastDijkstraSearcherEnabler{});
      ASSERT_EQ(StoringSearcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(results, 2);
    }

    {
      SearchSettings start_settings;
      start_settings.reversed_edges_mode = true;

      size_t results = 0;
      Searcher searcher(
          *graph, nullptr, nullptr,
          [&](const detail::SearchResult&) -> int {
            results++;
            SearchSettings settings;
            settings.reversed_edges_mode = true;
            settings.max_path_length = 2000.0 * geometry::meters;
            EXPECT_TRUE(searcher.SetSettings(settings));
            return 0;
          },
          obj_index, start_settings, FastDijkstraSearcherEnabler{});
      ASSERT_EQ(StoringSearcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(results, 2);
    }

    {
      SearchSettings start_settings;
      start_settings.max_path_length = 2000.0 * geometry::meters;
      start_settings.reversed_edges_mode = true;

      size_t results = 0;
      Searcher searcher(
          *graph, nullptr, nullptr,
          [&](const detail::SearchResult&) -> int {
            results++;
            SearchSettings settings;
            settings.reversed_edges_mode = true;
            EXPECT_FALSE(searcher.SetSettings(settings));
            return 0;
          },
          obj_index, start_settings, FastDijkstraSearcherEnabler{});
      ASSERT_EQ(StoringSearcher::StopBecauseDone,
                searcher.Search(start_search_pos.edge_id));

      ASSERT_EQ(results, 2);
    }
  });
}

}  // namespace graph::test
