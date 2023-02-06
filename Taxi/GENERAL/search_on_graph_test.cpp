#include <gtest/gtest.h>
#include <graph/config/graph.hpp>
#include <graph/dijkstra_object_searcher.hpp>
#include <graph/graph_loader.hpp>
#include <graph/tests/graph_fixture_config.hpp>

#include <functional>

#include <userver/components/component_context.hpp>
#include <userver/engine/mutex.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/rcu/rcu.hpp>
#include <userver/utest/utest.hpp>

#include <boost/filesystem/path.hpp>

namespace graph::examples {

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
  GeobusEdgePositionsListener(const std::string& redis_client_name,
                              const std::string& channel,
                              CallbackType on_message_received,
                              const ComponentContext& context) {
    std::ignore = channel;
    std::ignore = redis_client_name;
    std::ignore = on_message_received;
    std::ignore = context;
  }
};

}  // namespace mock

// Используйте вместо этого geobus::clients::GeobusEdgePositionsListener из
// geobus в своём коде.
using mock::GeobusEdgePositionsListener;
// Используйте вместо этого ::components::ComponentContext в своём коде.
using mock::ComponentContext;

//! [CODE_BLOCK2]
// Вместо наследования от GeobusEdgePositionsListener можно принимать в
// конструкторе ссылку на GeobusEdgePositionsChannel
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
              // onMessageReceived - наш колбек для получения координат
              // водителей
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

    // RCU даст нам "возможно"-копию данных, которая точно не будет меняться
    auto objects_index_ro = objects_index_.Read();
    graph::DijkstraObjectSearcher<mock::DriverId, DriverData> searcher(
        graph_, jams_, closures_, callback, *objects_index_ro);
    return searcher.Search(pos.edge_id);
  }

 private:
  void onMessageReceived(Payload&& payload) {
    // Берем RCU на запись
    auto objects_index_rw = objects_index_.StartWrite();
    for (const auto& pos : payload) {
      // Убираем предыдущие позиции водителя
      objects_index_rw->Remove(pos.driver_id);

      // Добавляем новые позиции водителя. possible_positions - его
      // вероятные позиции на данный момент
      for (const auto& possible_pos : pos.possible_positions) {
        // Добавляем позицию водителя в индекс. В качетсве данных сохраним
        // вероятность этой позиции
        objects_index_rw->Insert(pos.driver_id,
                                 DriverData{possible_pos.GetProbability()},
                                 possible_pos.GetPosition(), 100);
      }
    }
    // Сохраняем новое значение индекса
    objects_index_rw.Commit();
  }

 private:
  // We recommend using DriverIdView as a key to improve performance.
  rcu::Variable<graph::GraphObjectIndex<mock::DriverId, DriverData>>
      objects_index_;
  const graph::Graph& graph_;
  const graph::Jams* jams_;
  const graph::Closures* closures_;
};
//! [CODE_BLOCK2]

}  // namespace graph::examples

namespace graph {
namespace test {

// Тест только для того, чтобы скомпилировался класс ObjectIndex.
UTEST(Examples, TestObjectIndex) {
  graph::GraphLoader loader;
  auto graph =
      loader.LoadGraph(::graph::test::GraphTestFixtureConfig::kTestGraphDataDir,
                       graph::configs::kPopulateMemoryMapName);

  /// Closures and jams can be loaded with jams-closures library
  /// See examples/search_on_graph_test.cpp file in jams-closures library
  /// for example.
  const Jams* kEmptyJams = nullptr;
  const Closures* kEmptyClosures = nullptr;

  examples::ObjectIndex index(*graph, kEmptyJams, kEmptyClosures, "", "",
                              examples::ComponentContext());
}

}  // namespace test
}  // namespace graph
