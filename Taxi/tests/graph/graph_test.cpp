#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <maps/libs/geolib/include/distance.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/road_graph_helpers.h>
#include <taxi/graph/libs/nearest_edges/nearest_edges.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

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

namespace {

    double SegmentDirection(const TaxiGraph& graph, const TPoint& point) {
        const TPositionOnEdge posOnEdge = TNearestEdges{graph}.NearestEdge(point, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2);
        const TPositionOnGraph posOnGraph = graph.GetPositionOnGraph(posOnEdge);
        return graph.GetSegmentDirection(posOnGraph);
    }

}

struct TGraphTestFixture: public ::NUnitTest::TBaseTestCase,
                           public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_interface, TGraphTestFixture) {
    Y_UNIT_TEST(edge_data) {
        const auto& graph = GetTestRoadGraph();
        const auto& edgeData = graph.GetEdgeData(239_eid);

        UNIT_ASSERT_EQUAL(edgeData.IsTollRoad, false);
        UNIT_ASSERT_DOUBLES_EQUAL(edgeData.Speed, 8., 1e-6);
    }

    Y_UNIT_TEST(fb_category) {
        const auto& roadGraph = GetTestRoadGraph();
        const auto category = roadGraph.GetCategory(239_eid);

        UNIT_ASSERT_EQUAL(category, TEdgeCategory::EC_LOCAL_ROADS);
    }

    Y_UNIT_TEST(fb_edge) {
        const auto& roadGraph = GetTestRoadGraph();
        const auto edge = roadGraph.GetEdge(239_eid);

        UNIT_ASSERT_EQUAL(edge.Id, 239_eid);
        UNIT_ASSERT_EQUAL(edge.Source, 90_vid);
        UNIT_ASSERT_EQUAL(edge.Target, 85435_vid);
    }

    Y_UNIT_TEST(fb_edge_geometry) {
        const auto& roadGraph = GetTestRoadGraph();
        const auto edgeGeometry = roadGraph.GetEdgeGeometry(239_eid);

        UNIT_ASSERT_EQUAL(edgeGeometry.PointsSize(), 2);

        const auto& point0 = edgeGeometry.PointAt(0);
        UNIT_ASSERT_DOUBLES_EQUAL(point0.Lon, 37.718083, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(point0.Lat, 55.611021, 1e-6);

        const auto& point1 = edgeGeometry.PointAt(1);
        UNIT_ASSERT_DOUBLES_EQUAL(point1.Lon, 37.718236, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(point1.Lat, 55.611045, 1e-6);
    }

    Y_UNIT_TEST(fb_edge_data) {
        const auto& roadGraph = GetTestRoadGraph();
        const auto& edgeData = roadGraph.GetEdgeData(239_eid);

        UNIT_ASSERT_DOUBLES_EQUAL(edgeData.Speed, 8., 1e-6);

        const auto& speedLimit = edgeData.SpeedLimit;
        UNIT_ASSERT_EQUAL(static_cast<bool>(speedLimit), false);
    }

    Y_UNIT_TEST(fb_out_edges) {
        const auto& roadGraph = GetTestRoadGraph();
        const auto& outEdges = roadGraph.GetOutEdges(90_vid);

        const auto& size = outEdges.size();
        UNIT_ASSERT_EQUAL(size, 2u);

        UNIT_ASSERT_EQUAL(outEdges[0], 238_eid);
        UNIT_ASSERT_EQUAL(outEdges[1], 239_eid);
    }

    Y_UNIT_TEST(fb_in_edges) {
        const auto& roadGraph = GetTestRoadGraph();
        const auto& inEdges = roadGraph.GetInEdges(90_vid);

        const auto& size = inEdges.size();
        UNIT_ASSERT_EQUAL(size, 2u);

        UNIT_ASSERT_EQUAL(inEdges[0], 276_eid);
        UNIT_ASSERT_EQUAL(inEdges[1], 200519_eid);
    }

    Y_UNIT_TEST(fb_edge_non_alloc) {
        const auto& roadGraph = GetTestRoadGraph();
        NTaxi::NGraph2::TEdge edge;
        UNIT_ASSERT(roadGraph.GetEdge(edge, 239_eid));

        UNIT_ASSERT_EQUAL(edge.Id, 239_eid);
        UNIT_ASSERT_EQUAL(edge.Source, 90_vid);
        UNIT_ASSERT_EQUAL(edge.Target, 85435_vid);
    }

    Y_UNIT_TEST(fb_edge_geometry_non_alloc) {
        const auto& roadGraph = GetTestRoadGraph();
        NTaxi::NGraph2::TPolyline edgeGeometry;
        UNIT_ASSERT(roadGraph.GetEdgeGeometry(edgeGeometry, 239_eid));

        UNIT_ASSERT_EQUAL(edgeGeometry.PointsSize(), 2);

        const auto& point0 = edgeGeometry.PointAt(0);
        UNIT_ASSERT_DOUBLES_EQUAL(point0.Lon, 37.718083, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(point0.Lat, 55.611021, 1e-6);

        const auto& point1 = edgeGeometry.PointAt(1);
        UNIT_ASSERT_DOUBLES_EQUAL(point1.Lon, 37.718236, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(point1.Lat, 55.611045, 1e-6);
    }

    Y_UNIT_TEST(fb_edge_data_non_alloc) {
        const auto& roadGraph = GetTestRoadGraph();
        NTaxi::NGraph2::TEdgeData edgeData;
        UNIT_ASSERT(roadGraph.GetEdgeData(edgeData, 239_eid));

        UNIT_ASSERT_DOUBLES_EQUAL(edgeData.Speed, 8., 1e-6);

        const auto& speedLimit = edgeData.SpeedLimit;
        UNIT_ASSERT_EQUAL(speedLimit.has_value(), false);
    }

    Y_UNIT_TEST(fb_out_edges_non_alloc) {
        const auto& roadGraph = GetTestRoadGraph();
        TVector<NTaxi::NGraph2::TId> outEdges;
        UNIT_ASSERT(roadGraph.GetOutEdges(outEdges, 90_vid));

        const auto& size = outEdges.size();
        UNIT_ASSERT_EQUAL(size, 2u);

        UNIT_ASSERT_EQUAL(outEdges[0], 238_eid);
        UNIT_ASSERT_EQUAL(outEdges[1], 239_eid);
    }

    Y_UNIT_TEST(fb_in_edges_non_alloc) {
        const auto& roadGraph = GetTestRoadGraph();
        TVector<NTaxi::NGraph2::TId> inEdges;
        UNIT_ASSERT(roadGraph.GetInEdges(inEdges, 90_vid));

        const auto& size = inEdges.size();
        UNIT_ASSERT_EQUAL(size, 2u);

        UNIT_ASSERT_EQUAL(inEdges[0], 276_eid);
        UNIT_ASSERT_EQUAL(inEdges[1], 200519_eid);
    }

    Y_UNIT_TEST(fb_calculate_position_on_edge) {
        const auto& roadGraph = GetTestRoadGraph();

        const double resultWhenPointIsBegin = roadGraph.CalculatePositionOnEdge(
            TPoint(37.718083, 55.611021), 239_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(resultWhenPointIsBegin, 0.0, 1e-2);

        const double resultWhenPointIsEnd = roadGraph.CalculatePositionOnEdge(
            TPoint(37.718236, 55.611045), 239_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(resultWhenPointIsEnd, 1.0, 1e-2);

        const double resultWhenPointIsMiddle = roadGraph.CalculatePositionOnEdge(
            TPoint(37.718160, 55.611033), 239_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(resultWhenPointIsMiddle, 0.5, 1e-2);
    }

    Y_UNIT_TEST(fb_find_closest_point) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint resultWhenPointIsBegin_c = TPoint(37.718083, 55.611021);
        const TPoint resultWhenPointIsBegin = roadGraph.FindClosestPoint(
            TPoint(37.718083, 55.611021), 239_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(resultWhenPointIsBegin_c.Lon, resultWhenPointIsBegin.Lon, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(resultWhenPointIsBegin_c.Lat, resultWhenPointIsBegin.Lat, 1e-6);

        const TPoint resultWhenPointIsEnd_c = TPoint(37.718236, 55.611045);
        const TPoint resultWhenPointIsEnd = roadGraph.FindClosestPoint(
            TPoint(37.718236, 55.611045), 239_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(resultWhenPointIsEnd_c.Lon, resultWhenPointIsEnd.Lon, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(resultWhenPointIsEnd_c.Lat, resultWhenPointIsEnd.Lat, 1e-6);

        const TPoint resultWhenPointIsMiddle_c = TPoint(37.718160, 55.611033);
        const TPoint resultWhenPointIsMiddle = roadGraph.FindClosestPoint(
            TPoint(37.718160, 55.611033), 239_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(resultWhenPointIsMiddle_c.Lon, resultWhenPointIsMiddle.Lon, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(resultWhenPointIsMiddle_c.Lat, resultWhenPointIsMiddle.Lat, 1e-6);
    }

    Y_UNIT_TEST(fb_adjust_point) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const auto& adjusted1 = roadGraph.AdjustPoint(point1);
        UNIT_ASSERT_DOUBLES_EQUAL(adjusted1.Lon, 37.718083, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(adjusted1.Lat, 55.611021, 1e-2);
    }

    Y_UNIT_TEST(fb_adjust_track) {
        const auto& roadGraph = GetTestRoadGraph();

        TPolyline track;
        track.ReservePoints(2u);
        track.AddPoint({37.718083, 55.611021});
        track.AddPoint({37.718160, 55.611033});

        const auto& result = roadGraph.AdjustTrack(track);

        UNIT_ASSERT_EQUAL(result.PointsSize(), 2);
        const auto& point0 = result.PointAt(0u);
        UNIT_ASSERT_DOUBLES_EQUAL(point0.Lon, 37.718083, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(point0.Lat, 55.611021, 1e-2);
        const auto& point1 = result.PointAt(1u);
        UNIT_ASSERT_DOUBLES_EQUAL(point1.Lon, 37.71860, 1e-2);
        UNIT_ASSERT_DOUBLES_EQUAL(point1.Lat, 55.611033, 1e-2);
    }

    Y_UNIT_TEST(fb_version) {
        const auto& roadGraph = GetTestRoadGraph();
        const auto& version = roadGraph.GetVersion();

        UNIT_ASSERT_STRINGS_EQUAL(version.Data(), "3.0.0-0");
    }

    Y_UNIT_TEST(turn_info) {
        const auto& roadGraph = GetTestRoadGraph();

        // route: 55.7219; 37.6661 -> 55.7128; 37.6654 -> 55.7138; 37.6652
        const auto firstTurnInfo = roadGraph.GetTurnInfo(231'415_eid, 8'782_eid);

        UNIT_ASSERT_EQUAL(firstTurnInfo.Weight, 0);
    }

    Y_UNIT_TEST(forbidden_turn) {
        const auto& roadGraph = GetTestRoadGraph();

        UNIT_ASSERT_EQUAL(roadGraph.IsForbiddenTurn(117'746_eid, 4'372_eid), true);
        UNIT_ASSERT_EQUAL(roadGraph.IsForbiddenTurn(88'848_eid, 4'687_eid), false);
    }

    Y_UNIT_TEST(nearest_edge) {
        const auto& graph = GetTestRoadGraph();

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
        const auto& graph = GetTestRoadGraph();

        const TPoint pt1{37.645995, 55.737224};
        const TPoint pt2{0, 0};

        TPositionOnEdge edge = TNearestEdges{graph}.NearestEdge(pt1, NTaxi::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);
        UNIT_ASSERT(!edge.IsUndefined());
        UNIT_ASSERT_EQUAL(edge.GetEdgeId(), 220823_eid);

        edge = TNearestEdges{graph}.NearestEdge(pt2, NTaxi::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);
        UNIT_ASSERT(edge.IsUndefined());
        UNIT_ASSERT_EQUAL(edge.GetEdgeId(), NTaxi::NGraph2::UNDEFINED);
    }

    Y_UNIT_TEST(pos_edge_graph_conversion) {
        const auto& roadGraph = GetTestRoadGraph();
        TPoint sourcePoint{37.533547, 55.700951};
        TPositionOnEdge posOnEdge = TNearestEdges{roadGraph}.NearestEdge(sourcePoint, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2);

        TPositionOnGraph posOnGraph = roadGraph.GetPositionOnGraph(posOnEdge);

        TPositionOnEdge posOnEdge2 = roadGraph.GetPositionOnEdge(posOnGraph);

        UNIT_ASSERT_EQUAL(posOnEdge.GetEdgeId(), posOnGraph.GetEdgeId());
        UNIT_ASSERT(maps::geolib3::distance(
                        ToMapsPoint(roadGraph.GetCoords(posOnGraph)),
                        ToMapsPoint(roadGraph.GetCoords(posOnEdge2))) < 0.001);
        UNIT_ASSERT(maps::geolib3::distance(
                        ToMapsPoint(sourcePoint),
                        ToMapsPoint(roadGraph.GetCoords(posOnEdge2))) < 0.001);

        TPositionOnGraph posOnGraph2 = roadGraph.GetPositionOnGraph(posOnEdge2);
        UNIT_ASSERT(maps::geolib3::distance(
                        ToMapsPoint(roadGraph.GetCoords(posOnGraph2)),
                        ToMapsPoint(roadGraph.GetCoords(posOnEdge2))) < 0.001);
        UNIT_ASSERT(maps::geolib3::distance(
                        ToMapsPoint(sourcePoint),
                        ToMapsPoint(roadGraph.GetCoords(posOnGraph2))) < 0.001);
    }

    Y_UNIT_TEST(fb_segment_direction) {
        const auto& roadGraph = GetTestRoadGraph();

        const TPoint point1{37.562824, 55.754468};
        const double direction1 = SegmentDirection(roadGraph, point1);
        UNIT_ASSERT_DOUBLES_EQUAL(direction1, 259.9083445, 0.001);

        const TPoint point2{37.566591, 55.754551};
        const double direction2 = SegmentDirection(roadGraph, point2);
        UNIT_ASSERT_DOUBLES_EQUAL(direction2, 278.9357867, 0.001);

        const TPoint point3{37.572781, 55.753066};
        const double direction3 = SegmentDirection(roadGraph, point3);
        UNIT_ASSERT_DOUBLES_EQUAL(direction3, 307.1361473, 0.001);
    }

    Y_UNIT_TEST(check_version) {
        const auto& graph = GetTestRoadGraph();

        const auto& version = graph.GetVersion();

        UNIT_ASSERT_STRINGS_EQUAL(version.Data(), "3.0.0-0");
    }

    Y_UNIT_TEST(get_reverse_edge_id_road) {
        const auto& roadGraph = GetTestRoadGraph();

        // point without reverse edge.
        TPoint sourcePoint{37.533547, 55.700951};
        TPositionOnEdge posOnEdge = TNearestEdges{roadGraph}.NearestEdge(sourcePoint, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2);
        const auto& reverseEdgeId = roadGraph.GetReverseEdgeId(posOnEdge.GetEdgeId());
        UNIT_ASSERT_EQUAL(reverseEdgeId.has_value(), false);

        // point with reverse edge.
        TPoint sourcePoint2{37.637338, 55.732212};
        TPositionOnEdge posOnEdge2 = TNearestEdges{roadGraph}.NearestEdge(sourcePoint2, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2);
        const auto& reverseEdgeId2 = roadGraph.GetReverseEdgeId(posOnEdge2.GetEdgeId());
        UNIT_ASSERT_EQUAL(reverseEdgeId2.has_value(), true);

        // check reverse edge source and target points.
        const auto& edge = roadGraph.GetEdge(posOnEdge2.GetEdgeId());
        const auto& reverseEdge = roadGraph.GetEdge(reverseEdgeId2.value());
        UNIT_ASSERT_EQUAL(edge.Source, reverseEdge.Target);
        UNIT_ASSERT_EQUAL(edge.Target, reverseEdge.Source);
    }

    Y_UNIT_TEST(get_reverse_edge_id_static) {
        const auto& graph = GetTestRoadGraph();

        // point without reverse edge.
        TPoint sourcePoint{37.533547, 55.700951};
        TPositionOnEdge posOnEdge = TNearestEdges{graph}.NearestEdge(sourcePoint, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2);
        const auto& reverseEdgeId = graph.GetReverseEdgeId(posOnEdge.GetEdgeId());
        UNIT_ASSERT_EQUAL(reverseEdgeId.has_value(), false);

        // point with reverse edge.
        TPoint sourcePoint2{37.637338, 55.732212};
        TPositionOnEdge posOnEdge2 = TNearestEdges{graph}.NearestEdge(sourcePoint2, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2);
        const auto& reverseEdgeId2 = graph.GetReverseEdgeId(posOnEdge2.GetEdgeId());
        UNIT_ASSERT_EQUAL(reverseEdgeId2.has_value(), true);

        // check reverse edge source and target points.
        const auto& edge = graph.GetEdge(posOnEdge2.GetEdgeId());
        const auto& reverseEdge = graph.GetEdge(reverseEdgeId2.value());
        UNIT_ASSERT_EQUAL(edge.Source, reverseEdge.Target);
        UNIT_ASSERT_EQUAL(edge.Target, reverseEdge.Source);
    }
}
