#include <gtest/gtest.h>
#include <graph/config/graph.hpp>
#include <graph/dijkstra_object_searcher.hpp>
#include <graph/graph_loader.hpp>
#include <graph/tests/graph_fixture_config.hpp>
#include <jams-closures/jams_closures_loader.hpp>

#include <functional>

#include <userver/components/component_context.hpp>
#include <userver/engine/mutex.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/rcu/rcu.hpp>
#include <userver/utest/utest.hpp>

#include <boost/filesystem/path.hpp>

namespace jams_closures::examples {

namespace mock {

using DriverId = std::string;
struct ComponentContext {
  ComponentContext() {}
};

struct ProbablePosition {
  double GetProbability() const { return 0.4; }
  ::geometry::Position GetPosition() const {
    return {37 * geometry::lon, 55 * geometry::lat};
  };
};

struct DriverEdgePosition {
  DriverId driver_id;
  std::vector<ProbablePosition> possible_positions;
};

class GeobusEdgePositionsListener {
 public:
  using Payload = std::vector<DriverEdgePosition>;
  using CallbackType = std::function<void(const std::string&, Payload&&)>;

 public:
  GeobusEdgePositionsListener(
      [[maybe_unused]] const std::string& redis_client_name,
      [[maybe_unused]] const std::string& channel,
      [[maybe_unused]] CallbackType on_message_received,
      [[maybe_unused]] const ComponentContext& context) {}
};

}  // namespace mock

// Please use geobus::clients::GeobusEdgePositionsListener from geobus library
// in your code instead.
using mock::GeobusEdgePositionsListener;
// Please use ::components::ComponentContext instead of this in your code.
using mock::ComponentContext;

//! [CODE_BLOCK2]
// Instead of inheriting from GeobusEdgePositionsListener you could take
// reference to GeobusEdgePositionsChannel in the constructor.
class ObjectIndex : public GeobusEdgePositionsListener {
 public:
  struct DriverData {
    double probability;
  };

 public:
  ObjectIndex(const graph::Graph& graph, const graph::Jams* jams,
              const graph::Closures* closures,
              const std::string& redis_client_name, const std::string& channel,
              const ComponentContext& context)
      : GeobusEdgePositionsListener(
            redis_client_name, channel,
            [this](const std::string&, Payload&& payload) {
              // onMessageReceived - our callback for receiving drivers'
              // positions.
              onMessageReceived(std::move(payload));
            },
            context),
        objects_index_(graph),
        graph_(graph),
        jams_(jams),
        closures_(closures) {}

  // Основной метод - найти всех водителей от указанной точки.
  auto Search(const ::geometry::Position& start_pos,
              const typename graph::DijkstraObjectStoringSearcher<
                  mock::DriverId, DriverData>::UserSaveCallback& callback) {
    const auto& pos = graph_.NearestEdge(start_pos);
    if (pos.IsUndefined()) {
      throw std::runtime_error("Failed to find nearest position on graph.");
    }

    // RCU gives us smart pointer to data that definitely wouldn't change.
    auto objects_index_ro = objects_index_.Read();
    graph::DijkstraObjectSearcher<mock::DriverId, DriverData> searcher(
        graph_, jams_, closures_, callback, *objects_index_ro);
    return searcher.Search(pos.edge_id);
  }

 private:
  void onMessageReceived(Payload&& payload) {
    // Take current RCU record
    auto objects_index_rw = objects_index_.StartWrite();
    for (const auto& pos : payload) {
      // Clean previous driver positions
      objects_index_rw->Remove(pos.driver_id);

      // Add new driver's positions.
      // possible_positions - this is possible driver'ss positions on that
      // moment.
      for (const auto& possible_pos : pos.possible_positions) {
        // Add new driver's position to index. Data for position gonna be its
        // probability.
        objects_index_rw->Insert(pos.driver_id,
                                 DriverData{possible_pos.GetProbability()},
                                 possible_pos.GetPosition(), 100);
      }
    }
    // Save new index value.
    objects_index_rw.Commit();
  }

 private:
  rcu::Variable<graph::GraphObjectIndex<mock::DriverId, DriverData>>
      objects_index_;
  const graph::Graph& graph_;
  const graph::Jams* jams_;
  const graph::Closures* closures_;
};
//! [CODE_BLOCK2]

}  // namespace jams_closures::examples

namespace jams_closures {
namespace test {

// Test for checking object index with jams and closures work correctly.
UTEST(Examples, TestJamsAndClosures) {
  graph::GraphLoader graph_loader;
  jams_closures::JamsClosuresLoader jams_closures_loader;
  auto graph = graph_loader.LoadGraph(
      ::graph::test::GraphTestFixtureConfig::kTestGraphDataDir,
      graph::configs::kPopulateMemoryMapName);
  auto persistent_index = graph_loader.LoadPersistentIndex(
      graph::test::GraphTestFixtureConfig::kTestGraphDataDir,
      graph::configs::kPopulateMemoryMapName);
  /// Please use jams-cache in production code.
  auto jams_data = jams_closures_loader.LoadJams(
      *persistent_index, engine::current_task::GetTaskProcessor(),
      graph::test::GraphTestFixtureConfig::GetJamsTestMetaJson(),
      graph::test::GraphTestFixtureConfig::kJamsFilenamePrefix,
      graph::test::GraphTestFixtureConfig::kJamsPath);
  /// Please use closures-cache in production code.
  const auto& now = utils::datetime::Now();
  auto closures =
      graph::Closures{persistent_index->GetRawIndex(),
                      static_cast<NTaxiExternal::NGraph2::TTimestamp>(
                          std::chrono::system_clock::to_time_t(now))};

  graph::Jams graph_jams{std::move(jams_data.jams)};

  examples::ObjectIndex index(*graph, &graph_jams, &closures, "", "",
                              examples::ComponentContext());

  /// TODO: call search and check that closures work correctly
  /// (https://st.yandex-team.ru/TAXIGRAPH-887)
}

}  // namespace test
}  // namespace jams_closures
