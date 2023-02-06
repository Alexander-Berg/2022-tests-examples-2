#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search2/dijkstra_edge_searcher.h>
#include <taxi/graph/libs/search2/reachable_sphere_edge_processor.h>
#include <taxi/graph/libs/search2/transformator.h>

#include <iostream>
#include <optional>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#include <util/stream/file.h>

#include "common.h"

using NTaxi::NGraph2::TClosures;
using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TJams;
using NTaxi::NGraph2::TObjectIndex;
using NTaxi::NGraph2::TPersistentIndex;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TVertexId;

using namespace NTaxi::NGraphSearch2;
using namespace NTaxi::NGraph2Literals;

namespace {

  struct TTestCallback {
    void operator()(const TPositionOnEdge& pos) {
      Positions.push_back(pos);
    }

    std::vector<TPositionOnEdge> Positions;
  };

struct TForwardSearchTraits {
  using TDirectionControl = TForwardSearchControl<NTaxi::NGraph2::TGraphFacadeCommon>;
  static constexpr size_t HeapReserve = 8;
  static constexpr size_t EdgeInfoStorageReserve = 8;
  static constexpr bool TrackPaths = false;
  static constexpr bool TrackTollRoads = false;
  static constexpr bool TrackEdgeLeeway = false;

  static constexpr EResidentialAreaDriveMode ResidentialAreaDriveMode =
      EResidentialAreaDriveMode::PassThroughProhibited;
  static constexpr EBoomBarriersAreaDriveMode BoomBarriersAreaDriveMode =
      EBoomBarriersAreaDriveMode::PassThroughProhibited;

  static constexpr bool DisableSearchingThroughNonPavedOrPoorConditionRoads =
      false;

  static constexpr bool DisableTollRoads = false;
};

}

class TReachableSphereFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
public:
  std::vector<TPositionOnEdge> Search(const TGraph& graph, TPositionOnEdge start, std::variant<TTime,TDistance> radius) {
        TFastSearchSettings searchSettings;
        if (std::holds_alternative<TTime>(radius)) {
          searchSettings.MaxTime = std::get<TTime>(radius);
        } else {
          searchSettings.MaxDistance = std::get<TDistance>(radius);
        }
        TTestCallback callback;
        TReachableSphereEdgeProcessor edgeProcessor(std::ref(callback), radius);

        TFastDijkstraEdgeSearcher
            searcher(TForwardSearchTraits{}, NTaxi::NGraph2::TGraphFacadeCommon{graph, graph.GetEdgeStorage()}, searchSettings, edgeProcessor);
        searcher.Search(TArrayRef{&start, 1});

        std::sort(callback.Positions.begin(), callback.Positions.end(),
          [](const auto& first, const auto& second) { return first.GetEdgeId().value() < second.GetEdgeId().value(); }
          );

        return callback.Positions;
  }
};

Y_UNIT_TEST_SUITE_F(reachable_sphere_test, TReachableSphereFixture) {
    Y_UNIT_TEST(TestRhombusDistance) {
        TGraph graph{CreateGiantRhombusGraph()};
        graph.BuildEdgeStorage(32);
        const TPositionOnEdge zeroStart{TEdgeId{0}, 0.5};
        {
          const auto& result = Search(graph, zeroStart, TDistance{1000});

          Y_ASSERT(result.size() == 2);
          Y_ASSERT(result[0].GetEdgeId() == TEdgeId{1});
          Y_ASSERT(result[1].GetEdgeId() == TEdgeId{2});
        }
        {
          const auto& result = Search(graph, zeroStart, TDistance{2000});

          Y_ASSERT(result.size() == 2);
          Y_ASSERT(result[0].GetEdgeId() == TEdgeId{2});
          Y_ASSERT(result[1].GetEdgeId() == TEdgeId{3});
        }
    }
    Y_UNIT_TEST(TestRhombusTime) {
        TGraph graph{CreateGiantRhombusGraph()};
        graph.BuildEdgeStorage(32);
        const TPositionOnEdge zeroStart{TEdgeId{0}, 0.5};
        {
          const auto& result = Search(graph, zeroStart, TTime{1000});

          Y_ASSERT(result.size() == 2);
          Y_ASSERT(result[0].GetEdgeId() == TEdgeId{1});
          Y_ASSERT(result[1].GetEdgeId() == TEdgeId{2});
        }
        {
          const auto& result = Search(graph, zeroStart, TDistance{2000});

          Y_ASSERT(result.size() == 2);
          Y_ASSERT(result[0].GetEdgeId() == TEdgeId{2});
          Y_ASSERT(result[1].GetEdgeId() == TEdgeId{3});
        }
    }
}
