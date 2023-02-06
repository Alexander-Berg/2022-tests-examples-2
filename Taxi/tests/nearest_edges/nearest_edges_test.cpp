#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <maps/libs/geolib/include/distance.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/road_graph_helpers.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#include <taxi/graph/libs/nearest_edges/nearest_edges.h>

#include <unordered_set>

using TaxiGraph = NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TEdgeAccess;
using NTaxi::NGraph2::TEdgeCategory;
using NTaxi::NGraph2::TNearestEdges;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TPositionOnGraph;
using NTaxi::NGraph2::TRoadGraphDataStorage;
using NTaxi::NGraph2::TRoadSideFilter;
using NTaxi::NUtils::ToMapsPoint;

using namespace NTaxi::NGraph2Literals;

struct TNearestEdgesTestFixture: public ::NUnitTest::TBaseTestCase,
                                  public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_interface, TNearestEdgesTestFixture) {
    Y_UNIT_TEST(fb_nearest_edge) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TPositionOnEdge nearestEdge = TNearestEdges{roadGraph}.NearestEdge(point1, NTaxi::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);

        UNIT_ASSERT_EQUAL(nearestEdge.GetEdgeId(), 200519_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(nearestEdge.GetPosition(), 1.0, 1e-2);
    }

    Y_UNIT_TEST(fb_nearest_edge_category) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TPositionOnEdge nearestEdge = TNearestEdges{roadGraph}.NearestEdge(point1, NTaxi::NGraph2::TEdgeAccess::EA_UNKNOWN, NTaxi::NGraph2::TEdgeCategory::EC_DISTRICT_ROADS, 1e2);

        UNIT_ASSERT_EQUAL(nearestEdge.GetEdgeId(), 50691_eid);
    }

    Y_UNIT_TEST(fb_nearest_edge_full_road_side_filter_proper) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        TPositionOnEdge res = TNearestEdges{roadGraph}.NearestEdge(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, TRoadSideFilter::ProperSide);

        UNIT_ASSERT(roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res), point1));
    }

    Y_UNIT_TEST(fb_nearest_edge_full_road_side_filter_wrong) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        TPositionOnEdge res = TNearestEdges{roadGraph}.NearestEdge(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, TRoadSideFilter::WrongSide);

        UNIT_ASSERT(!roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res), point1));
    }

    Y_UNIT_TEST(fb_nearest_edge_full_road_side_filter_proper_of_two) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718099, 55.610995}; // This point is off the road, because otherwise filter is unreliable
        const double maxDistance = 500;
        TPositionOnEdge res = TNearestEdges{roadGraph}.NearestEdge(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, TRoadSideFilter::ProperOfTwo);

        const bool hasReverse = roadGraph.HasReverseEdgeId(res.GetEdgeId());
        UNIT_ASSERT(!hasReverse || roadGraph.IsPointOnProperSideOfEdge(res, point1));
    }

    Y_UNIT_TEST(fb_nearest_edges) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const auto& nearestEdges = TNearestEdges{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2, 2, 2);

        UNIT_ASSERT_EQUAL(nearestEdges.size(), 2);
        UNIT_ASSERT_EQUAL(nearestEdges[0].GetEdgeId(), 238_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(nearestEdges[0].GetPosition(), 0.0, 1e-2);
        UNIT_ASSERT_EQUAL(nearestEdges[1].GetEdgeId(), 239_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(nearestEdges[1].GetPosition(), 0.0, 1e-2);
    }

    Y_UNIT_TEST(fb_nearest_edges_full) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TVector<TPositionOnEdge> res = TNearestEdges{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 100, 1, 1);

        UNIT_ASSERT_EQUAL(res.size(), 1);
        UNIT_ASSERT_EQUAL(res[0].GetEdgeId(), 238_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(res[0].GetPosition(), 0.0, 1e-2);
    }

    Y_UNIT_TEST(fb_nearest_edges_full_2) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TVector<TPositionOnEdge> res = TNearestEdges{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 100, 2);

        UNIT_ASSERT_EQUAL(res.size(), 2);
        UNIT_ASSERT_EQUAL(res[0].GetEdgeId(), 238_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(res[0].GetPosition(), 0.0, 1e-2);
        UNIT_ASSERT_EQUAL(res[1].GetEdgeId(), 239_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(res[1].GetPosition(), 0.0, 1e-2);
    }

    Y_UNIT_TEST(fb_nearest_edges_full_min_count) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        const size_t minCount = 5;
        const size_t maxCount = 10;
        TVector<TPositionOnEdge> res = TNearestEdges{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, maxCount);

        UNIT_ASSERT(res.size() > 5);
    }

    Y_UNIT_TEST(fb_nearest_edges_no_repetitions) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 10'000;
        const size_t minCount = 5'000;
        const size_t maxCount = 10'000;
        TVector<TPositionOnEdge> res = TNearestEdges{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, maxCount);
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
        const size_t maxCount = 2;
        TVector<TPositionOnEdge> res = TNearestEdges{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, maxCount, TRoadSideFilter::ProperSide);

        UNIT_ASSERT_EQUAL(res.size(), 2);
        UNIT_ASSERT(roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[0]), point1));
        UNIT_ASSERT(roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[1]), point1));
    }

    Y_UNIT_TEST(fb_nearest_edges_full_road_side_filter_wrong) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        const size_t minCount = 2;
        const size_t maxCount = 2;
        TVector<TPositionOnEdge> res = TNearestEdges{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, maxCount, TRoadSideFilter::WrongSide);

        UNIT_ASSERT_EQUAL(res.size(), 2);
        UNIT_ASSERT(!roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[0]), point1));
        UNIT_ASSERT(!roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[1]), point1));
    }

    Y_UNIT_TEST(fb_nearest_edges_full_road_side_filter_proper_of_two) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718099, 55.610995}; // This point is off the road, because otherwise filter is unreliable
        const double maxDistance = 500;
        const size_t minCount = 20;
        const size_t maxCount = 20;
        TVector<TPositionOnEdge> res = TNearestEdges{roadGraph}.NearestEdges(point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, maxCount, TRoadSideFilter::ProperOfTwo);

        UNIT_ASSERT_EQUAL(res.size(), 20);
        for (const auto& pos : res) {
            UNIT_ASSERT(!pos.IsUndefined());
            const bool hasReverse = roadGraph.HasReverseEdgeId(pos.GetEdgeId());
            UNIT_ASSERT(!hasReverse || roadGraph.IsPointOnProperSideOfEdge(pos, point1));
        }
    }

    Y_UNIT_TEST(nearest_edge) {
        const auto& graph = GetTestGraph();

        // Test for nearest edge: https://yandex.ru/maps/-/CBuF6Aww~B
        const TPoint pt{37.645995, 55.737224};
        const TPoint canoPoint{37.645646, 55.736541};

        TPositionOnEdge edge = TNearestEdges{graph}.NearestEdge(pt, NTaxi::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);
        const auto& geometry = graph.GetEdgeGeometry(edge.GetEdgeId());

        const TPoint& adjustetPoint = geometry.PointAt(0);
        UNIT_ASSERT_DOUBLES_EQUAL(canoPoint.Lon, adjustetPoint.Lon, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(canoPoint.Lat, adjustetPoint.Lat, 1e-6);

        const auto& edgeData = graph.GetEdgeData(edge.GetEdgeId());
        UNIT_ASSERT_DOUBLES_EQUAL(edgeData.Speed, 15., 1e-6);
    }

    Y_UNIT_TEST(nearest_edge_check_undefined) {
        const auto& graph = GetTestGraph();

        const TPoint pt1{37.645995, 55.737224};
        const TPoint pt2{0, 0};

        TPositionOnEdge edge = TNearestEdges{graph}.NearestEdge(pt1, NTaxi::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);
        UNIT_ASSERT_EQUAL(edge.GetEdgeId(), 220823_eid);

        edge = TNearestEdges{graph}.NearestEdge(pt2, NTaxi::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);
        UNIT_ASSERT_EQUAL(edge.GetEdgeId(), NTaxi::NGraph2::UNDEFINED);
    }
}
