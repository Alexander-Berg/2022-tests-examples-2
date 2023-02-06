#include <graph/config/graph.hpp>
#include <graph/dijkstra_object_searcher.hpp>
#include <graph/graph_loader.hpp>
#include <graph/tests/graph_fixture_config.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/utest/utest.hpp>

#include <gtest/gtest.h>

#include <boost/filesystem/path.hpp>

namespace graph::examples {

namespace {

/// Driver information on position.
/// We add chain and non-chain position to index and choose needed when do the
/// search.
struct DriverPointInfo {
  double probability = 1.0;
  bool is_chain_position = false;  // true if point b for busy driver (chain
                                   // point), false - if driver position.
};

/// Just some imitation of real index data
struct DriverIndexData {
  bool IsChainBusyDriver() const { return is_chain_busy_driver; }

  bool is_chain_busy_driver = false;
};

/// Here gonna be real driver index in production code.
using DriverIndex = std::unordered_map<std::string, DriverIndexData>;

/// Data structure for search result of driver.
struct SearchResult {
  graph::PositionOnEdge pos;
  double distance = .0;
  bool is_chain_pos = false;
};

bool IsAcceptablePoint(bool is_chain_driver,
                       const DriverPointInfo& driver_info) {
  if ((is_chain_driver && driver_info.is_chain_position) ||
      (!is_chain_driver && !driver_info.is_chain_position)) {
    return true;
  }

  return false;
}

}  // namespace

UTEST(Examples, SearchChainDemo) {
  //! [CODE_BLOCK3]
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
  graph::GraphObjectIndex<std::string, DriverPointInfo> obj_index(*graph);
  const double kNearestEdgeMaxDistance = 100.0;

  const std::string driver_with_chain = "Ivan";
  const std::string driver_without_chain = "Maria";

  // Now, lets add some driver to index.
  obj_index.Insert(driver_with_chain, DriverPointInfo{},
                   {37.642077 * lon, 55.736958 * lat}, kNearestEdgeMaxDistance);
  // We can add chain position for this driver
  obj_index.Insert(driver_with_chain, DriverPointInfo{1.0, true},
                   {37.642000 * lon, 55.736900 * lat}, kNearestEdgeMaxDistance);

  // Lets add another driver
  obj_index.Insert(driver_without_chain, DriverPointInfo{},
                   {37.642077 * lon, 55.736958 * lat}, kNearestEdgeMaxDistance);
  // And add chain pos for this driver also
  obj_index.Insert(driver_without_chain, DriverPointInfo{1.0, true},
                   {37.642020 * lon, 55.736920 * lat}, kNearestEdgeMaxDistance);

  // Let's add information about drivers to our index.
  // One of these drivers have got chain info and another one haven't got.
  DriverIndex driver_index;
  driver_index.emplace(driver_with_chain, DriverIndexData{true});
  driver_index.emplace(driver_without_chain, DriverIndexData{false});

  // Now, lets search
  {
    std::unordered_map<std::string, SearchResult> found_drivers;
    using Searcher =
        graph::DijkstraObjectSearcher<std::string, DriverPointInfo>;
    Searcher searcher(
        *graph, nullptr, nullptr,
        // this is user callback. It is called for every found driver
        [&found_drivers,
         &driver_index](const Searcher::SearchResult& search_result) -> int {
          const auto& it = driver_index.find(search_result.key);
          const auto& driver_info = search_result.value;
          if (it != driver_index.end()) {
            const auto& index_data = it->second;
            const bool is_chain_driver = index_data.IsChainBusyDriver();

            // Accept only chain points for chain drivers and only non-chain
            // points for non-chain drivers.
            if (IsAcceptablePoint(is_chain_driver, driver_info)) {
              found_drivers.emplace(
                  search_result.key,
                  SearchResult{search_result.position,
                               static_cast<double>(search_result.route_time),
                               is_chain_driver});
            }
          }

          // We only need 2 drivers.
          return (found_drivers.size() >= 2
                      ? 1  // Any non-zero value will cease the search
                      : 0  // Zero means 'continue searching'
          );
        },
        obj_index);

    const ::geometry::Position source_pos{37.641412 * lon, 55.738432 * lat};
    const graph::PositionOnEdge kStartPos = graph->NearestEdge(source_pos);

    // Now, lets launch searching
    const auto& search_stop_reason = searcher.Search(kStartPos);

    // Searcher returns 1 because user callback return it
    ASSERT_EQ(search_stop_reason, graph::StopReason{1});
    // Check that we found chain pos for driver_with_chain, because it is
    // chain driver in index, and non-chain position for driver_without_chain,
    // because it is non-chain driver in index.
    ASSERT_EQ(found_drivers[driver_with_chain].is_chain_pos, true);
    ASSERT_EQ(found_drivers[driver_without_chain].is_chain_pos, false);
  }
  //! [CODE_BLOCK3]
}

}  // namespace graph::examples
