#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <maps/libs/geolib/include/distance.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/road_graph_helpers.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#include <taxi/graph/libs/nearest_edges2/nearest_edges.h>

#include <unordered_set>

using TaxiGraph = NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TEdgeAccess;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TEdgeCategory;
using NTaxi::NGraph2::TEdgeStructType;
using NTaxi::NGraph2::TEdgeStructTypeSet;
using NTaxi::NGraph2::TNearestEdges2;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TPositionOnGraph;
using NTaxi::NGraph2::TRoadGraphDataStorage;
using NTaxi::NGraph2::TRoadSideFilter;
using NTaxi::NGraph2::ToMapsEdgeId;
using NTaxi::NUtils::ToMapsPoint;

using namespace NTaxi::NGraph2Literals;

struct TNearestEdges2TestFixture: public ::NUnitTest::TBaseTestCase,
                                  public NTaxi::NGraph2::TGraphTestData {

    /// There are four edges, that stems from point
    /// {37.718083, 55.611021};
    /// We can't guarantee which one will be picked up
    static inline const std::vector<TPositionOnEdge> ReferenceResults {
      TPositionOnEdge{239_eid, 0.0},
      TPositionOnEdge{ 276_eid, 1.0 },
      TPositionOnEdge{ 238_eid, 0.0 },
      TPositionOnEdge{ 200519_eid, 1.0 }
    };

    static bool IsInReferenceResults(const TPositionOnEdge& test) {
      for(const auto& ref : ReferenceResults) {
        if(ref.GetEdgeId() != test.GetEdgeId()) {
          continue;
        }
        if(std::fabs(ref.GetPosition() - test.GetPosition()) < 1e-2) {
          return true;
        }
      }

      return false;
    }
};

Y_UNIT_TEST_SUITE_F(graph_interface, TNearestEdges2TestFixture) {
    Y_UNIT_TEST(fb_nearest_edge) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TPositionOnEdge nearestEdge = TNearestEdges2{roadGraph}.NearestEdge(point1, NTaxi::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);

        UNIT_ASSERT(IsInReferenceResults(nearestEdge));
    }

    Y_UNIT_TEST(fb_nearest_edge_category) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TPositionOnEdge nearestEdge = TNearestEdges2{roadGraph}.NearestEdge(point1, NTaxi::NGraph2::TEdgeAccess::EA_UNKNOWN, NTaxi::NGraph2::TEdgeCategory::EC_DISTRICT_ROADS, 1e2);

        UNIT_ASSERT_EQUAL(nearestEdge.GetEdgeId(), 50691_eid);
    }

    Y_UNIT_TEST(fb_nearest_edge_full_road_side_filter_proper) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        TPositionOnEdge res = TNearestEdges2{roadGraph}.NearestEdge(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, TRoadSideFilter::ProperSide);

        UNIT_ASSERT(roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res), point1));
    }

    Y_UNIT_TEST(fb_nearest_edge_full_road_side_filter_wrong) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        TPositionOnEdge res = TNearestEdges2{roadGraph}.NearestEdge(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, TRoadSideFilter::WrongSide);

        UNIT_ASSERT(!roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res), point1));
    }

    Y_UNIT_TEST(fb_nearest_edge_full_road_side_filter_proper_of_two) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718099, 55.610995}; // This point is off the road, because otherwise filter is unreliable
        const double maxDistance = 500;
        TPositionOnEdge res = TNearestEdges2{roadGraph}.NearestEdge(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, TRoadSideFilter::ProperOfTwo);

        const bool hasReverse = roadGraph.HasReverseEdgeId(res.GetEdgeId());
        UNIT_ASSERT(!hasReverse || roadGraph.IsPointOnProperSideOfEdge(res, point1));
    }

    Y_UNIT_TEST(fb_nearest_edges) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const auto& nearestEdges = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2, 2, 2);

        UNIT_ASSERT_EQUAL(nearestEdges.size(), 2);
        for(auto x : nearestEdges) {
          UNIT_ASSERT(IsInReferenceResults(x));
        }
    }

    Y_UNIT_TEST(fb_nearest_edges_full) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TVector<TPositionOnEdge> res = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 100, 1, 1);

        UNIT_ASSERT_EQUAL(res.size(), 1);
        UNIT_ASSERT(IsInReferenceResults(res[0]));
    }

    Y_UNIT_TEST(fb_nearest_edges_full_2) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TVector<TPositionOnEdge> res = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 100, 2);

        std::cerr << "Res size: " << res.size() << std::endl;
        UNIT_ASSERT_EQUAL(res.size(), 2);
        for(auto x : res) {
          UNIT_ASSERT(IsInReferenceResults(x));
        }
    }

    Y_UNIT_TEST(fb_nearest_edges_full_min_count) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        const size_t minCount = 5;
        TVector<TPositionOnEdge> res = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount);

        UNIT_ASSERT(res.size() >= 5);
    }

    Y_UNIT_TEST(fb_nearest_edges_no_repetitions) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 10'000;
        const size_t minCount = 5'000;
        TVector<TPositionOnEdge> res = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount);
        UNIT_ASSERT(res.size() > 5);

        // Check that every edge is present only once
        std::unordered_set<unsigned int> edges;
        for (auto poe : res) {
            const auto edge_id = poe.GetEdgeId().value();
            auto insertion_result = edges.insert(edge_id);
            UNIT_ASSERT(insertion_result.second); // check that insertion take place -> no duplicates
        }
    }

    Y_UNIT_TEST(fb_nearest_edges_full_road_side_filter_proper) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        const size_t minCount = 2;
        TVector<TPositionOnEdge> res = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, TRoadSideFilter::ProperSide);

        UNIT_ASSERT_EQUAL(res.size(), 2);
        UNIT_ASSERT(roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[0]), point1));
        UNIT_ASSERT(roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[1]), point1));
    }

    Y_UNIT_TEST(fb_nearest_edges_full_road_side_filter_wrong) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        const size_t minCount = 2;
        TVector<TPositionOnEdge> res = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, TRoadSideFilter::WrongSide);

        UNIT_ASSERT_EQUAL(res.size(), 2);
        UNIT_ASSERT(!roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[0]), point1));
        UNIT_ASSERT(!roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[1]), point1));
    }

    Y_UNIT_TEST(fb_nearest_edges_full_road_side_filter_proper_of_two) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718099, 55.610995}; // This point is off the road, because otherwise filter is unreliable
        const double maxDistance = 500;
        const size_t minCount = 20;
        TVector<TPositionOnEdge> res = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, TRoadSideFilter::ProperOfTwo);

        UNIT_ASSERT_EQUAL(res.size(), 20);
        for (const auto& pos : res) {
            UNIT_ASSERT(!pos.IsUndefined());
            const bool hasReverse = roadGraph.HasReverseEdgeId(pos.GetEdgeId());
            UNIT_ASSERT(!hasReverse || roadGraph.IsPointOnProperSideOfEdge(pos, point1));
        }
    }

    Y_UNIT_TEST(fb_nearest_edges_bridge) {
        const auto& roadGraph = GetTestRoadGraph();

        // near Krymskiy Most bridge
        const TPoint point1{37.597922, 55.734611};
        const auto& nearestEdges = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 300, 200 /*yes, large number */
          , std::nullopt, TRoadSideFilter::NoFilter, static_cast<TEdgeStructTypeSet>(TEdgeStructType::EST_BRIDGE) );

        // There aren't 200 segments in this bridge.
        UNIT_ASSERT(nearestEdges.size() > 2);
        for(auto x : nearestEdges) {
          const auto edgeId = x.GetEdgeId();
          const auto& data = roadGraph.GetRoadGraph().RoadGraph->edgeData(ToMapsEdgeId(edgeId));
          UNIT_ASSERT(data.structType() == maps::road_graph::EdgeStructType::Bridge);
        }
    }
    Y_UNIT_TEST(fb_nearest_edges_tunnel) {
        const auto& roadGraph = GetTestRoadGraph();

        // near Leningradsky tunnel
        const TPoint point1{ 37.510664, 55.806105};
        const auto& nearestEdges = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 300, 200 /*yes, large number */
          , std::nullopt, TRoadSideFilter::NoFilter, static_cast<TEdgeStructTypeSet>(TEdgeStructType::EST_TUNNEL ));

        // There aren't 200 segments in this tunnel.
        UNIT_ASSERT(nearestEdges.size() > 2);
        for(auto x : nearestEdges) {
          const auto edgeId = x.GetEdgeId();
          const auto& data = roadGraph.GetRoadGraph().RoadGraph->edgeData(ToMapsEdgeId(edgeId));
          UNIT_ASSERT(data.structType() == maps::road_graph::EdgeStructType::Tunnel);
        }
    }

    Y_UNIT_TEST(fb_nearest_edges_no_tunnel_no_bridge) {
        const auto& roadGraph = GetTestRoadGraph();

        // near Leningradsky tunnel
        const TPoint point1{ 37.510664, 55.806105};
        const auto& nearestEdges = TNearestEdges2{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 300, 200 /*yes, large number */
          , std::nullopt, TRoadSideFilter::NoFilter, static_cast<TEdgeStructTypeSet>(TEdgeStructType::EST_ROAD | TEdgeStructType::EST_BRIDGE ));

        // There aren't 200 segments in this tunnel.
        UNIT_ASSERT(nearestEdges.size() > 2);
        for(auto x : nearestEdges) {
          const auto edgeId = x.GetEdgeId();
          const auto& data = roadGraph.GetRoadGraph().RoadGraph->edgeData(ToMapsEdgeId(edgeId));
          UNIT_ASSERT(data.structType() != maps::road_graph::EdgeStructType::Tunnel);
        }
    }

}
