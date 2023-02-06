#include <graph/config/graph.hpp>
#include <graph/dijkstra_object_searcher.hpp>
#include <graph/graph_loader.hpp>
#include <graph/tests/graph_fixture_config.hpp>

#include <functional>

#include <userver/engine/task/task.hpp>
#include <userver/utest/utest.hpp>

#include <gtest/gtest.h>

#include <boost/filesystem/path.hpp>

namespace graph::examples {

UTEST(Examples, SearchDemo) {
  //! [CODE_BLOCK]
  using ::geometry::lat;
  using ::geometry::lon;

  // Lets load road graph from folder
  graph::GraphLoader loader;
  auto graph =
      loader.LoadGraph(graph::test::GraphTestFixtureConfig::kTestGraphDataDir,
                       graph::configs::kPopulateMemoryMapName);

  // Build edge storage for graph
  // Object search without built edge storage will cause an exception
  loader.BuildEdgeStorage(graph);

  // Create an index object
  graph::GraphObjectIndex<std::string, std::string> obj_index(*graph);
  const double kNearestEdgeMaxDistance = 100.0;

  // Now, lets add some drivers to index. say, Ivan
  obj_index.Insert("Ivan", "data 1 for Ivan",
                   {37.642077 * lon, 55.736958 * lat}, kNearestEdgeMaxDistance);
  // We can add another position for Ivan
  obj_index.Insert("Ivan", "data 2 for Ivan",
                   {37.642000 * lon, 55.736900 * lat}, kNearestEdgeMaxDistance);
  // Lets add another driver
  obj_index.Insert("Maria", "data 1 for Maria",
                   {37.642020 * lon, 55.736920 * lat}, kNearestEdgeMaxDistance);

  using Searcher = graph::DijkstraObjectSearcher<std::string, std::string>;

  // Now, lets search
  {
    const int stop_value = 1;
    int found_drivers{0};
    Searcher searcher(
        *graph, nullptr, nullptr,
        // this is user callback. It is called for every found driver
        [&found_drivers](const Searcher::SearchResult& search_result) -> int {
          // Look, we have found a driver:
          std::cout << "Found driver " << search_result.key << " at position "
                    << search_result.position.position << " on edge "
                    << search_result.position.edge_id << " on "
                    << search_result.PathLength().value()
                    << " meters from start vertex of start edge" << std::endl;
          found_drivers++;
          // May be we only need 2 drivers:
          // Or - in this case - 2 posible positions. Both of those positions
          // may belong to Ivan.
          return (found_drivers >= 2
                      ? stop_value  // Any non-zero value will cease the search
                      : 0           // Zero means 'continue searching'
          );
        },
        obj_index);

    const ::geometry::Position source_pos{37.641412 * lon, 55.738432 * lat};
    const graph::PositionOnEdge kStartPos = graph->NearestEdge(source_pos);

    // Now, lets launch searching
    const auto& search_stop_reason = searcher.Search(kStartPos);
    // Searcher return same value as user callback
    ASSERT_EQ(search_stop_reason, graph::StopReason{stop_value});
  }
  //! [CODE_BLOCK]
  //! [CODE_BLOCK2]
  // Now let's create search settings with custom edges limit
  {
    graph::SearchSettings settings;
    settings.max_visited_edges = 10'000;

    int found_drivers{0};

    Searcher searcher(
        *graph, nullptr, nullptr,
        [&found_drivers](const Searcher::SearchResult&) -> int {
          found_drivers++;
          return 0;
        },
        obj_index, settings);

    // And now let's add custom stop condition to searcher.
    // We can capture the searcher in our function if we want to use its
    // methods inside condition chek (for example, for getting path length) If
    // the function returns true, the search will stop (but note that
    // condition may be checked not on each search iteration due to
    // performance reasons)
    std::function<bool(EdgeId, detail::Weight)> stop_condition =
        [&searcher](EdgeId id, detail::Weight weight) {
          auto path_length_opt =
              searcher.GetPathLength(PositionOnEdge{id, 0.0});
          return weight > 10'000 ||
                 (path_length_opt &&
                  *path_length_opt > 20.000 * geometry::meters);
        };
    searcher.SetStopCondition(stop_condition);

    const ::geometry::Position source_pos{37.641412 * lon, 55.738432 * lat};
    const graph::PositionOnEdge kStartPos = graph->NearestEdge(source_pos);

    // Now, lets launch searching again
    const auto& search_stop_reason = searcher.Search(kStartPos);
    // Searcher returns StopByStopCondition because StopCondition returns true
    ASSERT_EQ(search_stop_reason, Searcher::StopByStopCondition);
  }
  //! [CODE_BLOCK2]

  //! [CODE_BLOCK3]
  // Now let's create search setting in another way
  {
    int found_drivers{0};
    Searcher searcher(
        *graph, nullptr, nullptr,
        [&found_drivers](const Searcher::SearchResult&) -> int {
          ++found_drivers;
          return 0;
        },
        obj_index);
    const graph::SearchSettings settings{[] {
      graph::SearchSettings result;
      result.max_visited_edges = 10'000ull;
      return result;
    }()};
    searcher.SetSettings(settings);

    const ::geometry::Position source_pos{37.641412 * lon, 55.738432 * lat};
    const graph::PositionOnEdge kStartPos = graph->NearestEdge(source_pos);

    searcher.Search(kStartPos);
  }
  //! [CODE_BLOCK3]
}

}  // namespace graph::examples
