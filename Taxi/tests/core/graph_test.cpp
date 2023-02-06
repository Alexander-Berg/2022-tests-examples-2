#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <maps/libs/geolib/include/distance.h>
#include <yandex/taxi/graph2/container.h>
#include <yandex/taxi/graph2/graph.h>
#include <yandex/taxi/graph2/api_version.h>

#include <taxi/graph/libs/graph/geolib3_helpers.h>

#include <taxi/graph/external/graph2/lib/conversion.h>

using TaxiGraph = NTaxiExternal::NGraph2::TGraph;
using NTaxi::NUtils::ToMapsPoint;
using NTaxiExternal::NGraph2::TContainer;
using NTaxiExternal::NGraph2::TEdgeAccess;
using NTaxiExternal::NGraph2::TEdgeCategory;
using NTaxiExternal::NGraph2::TEdgeStructType;
using NTaxiExternal::NGraph2::TEdgeStructTypeSet;
using NTaxiExternal::NGraph2::TEdgeData;
using TRoadSideFilter = NTaxiExternal::NGraph2::TGraph::TRoadSideFilter;
using NTaxiExternal::NGraph2::TPoint;
using NTaxiExternal::NGraph2::TPolyline;
using NTaxiExternal::NGraph2::TPositionOnEdge;
using NTaxiExternal::NGraph2::TPositionOnGraph;
using NTaxiExternal::NGraph2::TRoadGraphFileLoader;

namespace {
    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }
    TString GraphInvalidPath(const TStringBuf& str) {
        static const TString prefix = "missing/directory/on/any/host";
        return BinaryPath(prefix + str);
    }

    const TaxiGraph& TestRoadGraph() {
        static const TaxiGraph graph(TRoadGraphFileLoader::Create(
            GraphPath("road_graph.fb").c_str(),
            GraphPath("rtree.fb").c_str()));
        return graph;
    }

    double SegmentDirection(const TaxiGraph& graph, const TPoint& point) {
        TPositionOnEdge posOnEdge;
        Y_VERIFY(graph.NearestEdge(posOnEdge, point, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 100));
        const TPositionOnGraph posOnGraph = graph.GetPositionOnGraph(posOnEdge);
        return graph.GetSegmentDirection(posOnGraph);
    }

}

struct TGraphTestFixture: public ::NUnitTest::TBaseTestCase {
    /// There are four edges, that stems from point
    /// {37.718083, 55.611021};
    /// We can't guarantee which one will be picked up
    static inline const std::vector<TPositionOnEdge> NearestEdgesReferenceResults {
      TPositionOnEdge{ 239, 0.0 },
      TPositionOnEdge{ 276, 1.0 },
      TPositionOnEdge{ 238, 0.0 },
      TPositionOnEdge{ 200519, 1.0 }
    };

    static bool IsInNearestEdgesReferenceResults(const TPositionOnEdge& test) {
      for(const auto& ref : NearestEdgesReferenceResults) {
        if(ref.EdgeId != test.EdgeId) {
          continue;
        }
        if(std::fabs(ref.Position - test.Position) < 1e-2) {
          return true;
        }
      }

      return false;
    }
};

Y_UNIT_TEST_SUITE_F(graph_interface, TGraphTestFixture) {
    Y_UNIT_TEST(invalid_road_graph_path) {
        auto graph_holder = TRoadGraphFileLoader::Create(
            GraphPath("road_graph.fb").c_str(),
            GraphInvalidPath("rtree.fb").c_str());
        UNIT_ASSERT_EQUAL(graph_holder.Get(), nullptr);
    }

    Y_UNIT_TEST(invalid_mapped_road_graph_path) {
        auto graph_holder = TRoadGraphFileLoader::CreateMapped(
            GraphInvalidPath("road_graph.fb").c_str(),
            GraphPath("rtree.fb").c_str());
        UNIT_ASSERT_EQUAL(graph_holder.Get(), nullptr);
    }

    Y_UNIT_TEST(fb_nearest_edge) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TPositionOnEdge nearestEdge;
        roadGraph.NearestEdge(nearestEdge, point1, NTaxiExternal::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);

        UNIT_ASSERT(IsInNearestEdgesReferenceResults(nearestEdge));
    }

    Y_UNIT_TEST(fb_nearest_edge_category) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TPositionOnEdge nearestEdge;
        roadGraph.NearestEdge(nearestEdge, point1, NTaxiExternal::NGraph2::TEdgeAccess::EA_UNKNOWN, NTaxiExternal::NGraph2::TEdgeCategory::EC_DISTRICT_ROADS, 1e2);

        UNIT_ASSERT_EQUAL(nearestEdge.EdgeId, 50691);
    }

    Y_UNIT_TEST(fb_nearest_edges_full) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TContainer<TPositionOnEdge> res;
        bool nearestEdges = roadGraph.NearestEdges(res, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 100, 1);

        UNIT_ASSERT(nearestEdges);
        UNIT_ASSERT_EQUAL(res.Size(), 1);
        UNIT_ASSERT(IsInNearestEdgesReferenceResults(res[0]));
    }

    Y_UNIT_TEST(fb_nearest_edges_full_2) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TContainer<TPositionOnEdge> res;
        const size_t minCount = 2;
        const size_t maxCount = 2;
        bool nearestEdges = roadGraph.NearestEdges(res, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 100, minCount, maxCount, TRoadSideFilter::NoFilter);

        UNIT_ASSERT(nearestEdges);
        UNIT_ASSERT_EQUAL(res.Size(), 2);
        UNIT_ASSERT(IsInNearestEdgesReferenceResults(res[0]));
        UNIT_ASSERT(IsInNearestEdgesReferenceResults(res[1]));
    }

    Y_UNIT_TEST(fb_nearest_edges_full_min_count) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TContainer<TPositionOnEdge> res;
        const double maxDistance = 100;
        const size_t minCount = 5;
        const size_t maxCount = 10;
        bool nearestEdges = roadGraph.NearestEdges(res, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, maxCount, TRoadSideFilter::NoFilter);

        UNIT_ASSERT(nearestEdges);
        UNIT_ASSERT(res.size() >= 5);
    }

    Y_UNIT_TEST(fb_nearest_edges_full_min_distance_zero) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TContainer<TPositionOnEdge> res;
        const double maxDistance = 100;
        const size_t minCount = 5;
        const size_t maxCount = 10;
        bool nearestEdges = roadGraph.NearestEdges(res, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, maxCount, TRoadSideFilter::NoFilter);

        UNIT_ASSERT(nearestEdges);
        UNIT_ASSERT(res.size() >= 5);
    }

    Y_UNIT_TEST(fb_nearest_edges_full_road_side_filter_proper) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        const double maxDistance = 100;
        const size_t minCount = 2;
        const size_t maxCount = 2;
        TContainer<TPositionOnEdge> res;
        bool nearestEdges = roadGraph.NearestEdges(res, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, maxCount, TRoadSideFilter::ProperSide);

        UNIT_ASSERT(nearestEdges);
        UNIT_ASSERT_EQUAL(res.size(), 2);
        UNIT_ASSERT(roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[0]), point1).value);
        UNIT_ASSERT(roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[1]), point1).value);
    }

    Y_UNIT_TEST(fb_nearest_edges_full_road_side_filter_wrong) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TContainer<TPositionOnEdge> res;
        const double maxDistance = 100;
        const size_t minCount = 2;
        const size_t maxCount = 2;
        bool nearestEdges = roadGraph.NearestEdges(res, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, maxDistance, minCount, maxCount, TRoadSideFilter::WrongSide);

        UNIT_ASSERT(nearestEdges);
        UNIT_ASSERT_EQUAL(res.size(), 2);
        UNIT_ASSERT(!roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[0]), point1).value);
        UNIT_ASSERT(!roadGraph.IsPointOnProperSideOfEdge(roadGraph.GetPositionOnGraph(res[1]), point1).value);
    }

    Y_UNIT_TEST(fb_nearest_edges_full_50) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TContainer<TPositionOnEdge> res;
        const auto MAX_EDGES = 50;
        const auto MAX_DISTANCE = 500;
        const bool nearestEdges = roadGraph.NearestEdges(res, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS,
                                                         MAX_DISTANCE, MAX_EDGES, MAX_EDGES, TRoadSideFilter::NoFilter);

        UNIT_ASSERT(nearestEdges);
        UNIT_ASSERT_EQUAL(res.Size(), MAX_EDGES);
    }

    Y_UNIT_TEST(fb_nearest_edges_full_min_max_20) {
        const auto& roadGraph = TestRoadGraph();

        TContainer<TPositionOnEdge> res;
        const TPoint point1{37.718083, 55.611021};
        const auto MAX_EDGES = 50;
        const auto MAX_DISTANCE = 500;

        /// Calculate expected edge count
        const auto tmp = roadGraph.NearestEdges(res, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS,
                                                MAX_DISTANCE, MAX_EDGES);
        UNIT_ASSERT(tmp);
        const auto EXPECTED_EDGE_COUNT = res.Size();
        UNIT_ASSERT_GT(EXPECTED_EDGE_COUNT, 0);

        /// Stop search edges if found any using distance less than MAX_DISTANCE
        const bool nearestEdges = roadGraph.NearestEdges(res, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS,
                                                         MAX_DISTANCE, MAX_EDGES);
        UNIT_ASSERT(nearestEdges);
        UNIT_ASSERT_EQUAL(res.Size(), EXPECTED_EDGE_COUNT);
    }

    Y_UNIT_TEST(fb_nearest_edges_bridge) {
        const auto& roadGraph = TestRoadGraph();

        TContainer<TPositionOnEdge> res;
        const TPoint point1{37.597922, 55.734611};
        const auto MAX_DISTANCE = 500;

        /// Calculate expected edge count
        const auto tmp = roadGraph.NearestEdges(res, point1,
          TEdgeAccess::EA_UNKNOWN,
          TEdgeCategory::EC_ROADS,
          MAX_DISTANCE,
          500, 500,
          TRoadSideFilter::NoFilter,
          TEdgeStructTypeSet{TEdgeStructType::EST_BRIDGE} );
        UNIT_ASSERT(tmp);
        const auto edges_count = res.Size();
        UNIT_ASSERT_GT(edges_count, 0);
        // Not so many tunnel segments in 500m radius
        UNIT_ASSERT_LE(edges_count, 30);
    }

    Y_UNIT_TEST(fb_nearest_edges_visualization) {
        const auto& roadGraph = TestRoadGraph();

        const TPoint point1{37.718083, 55.611021};
        TContainer<TPositionOnEdge> res;
        NTaxiExternal::NGraph2::TString visualization;
        bool nearestEdges = roadGraph.NearestEdges(res, visualization, point1, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 100, 10, 10,
          TRoadSideFilter::NoFilter);

        UNIT_ASSERT(nearestEdges);
        UNIT_ASSERT_EQUAL(res.Size(), 10);
        UNIT_ASSERT(visualization.size() > 1);
    }

    Y_UNIT_TEST(fb_version) {
        const auto& roadGraph = TestRoadGraph();
        const auto& version = roadGraph.GetVersion();

        UNIT_ASSERT_STRINGS_EQUAL(version.Data(), "3.0.0-0");
    }

    Y_UNIT_TEST(pos_edge_graph_conversion) {
        const auto& roadGraph = TestRoadGraph();
        TPoint sourcePoint{37.533547, 55.700951};
        TPositionOnEdge posOnEdge;
        bool nearestEdgeResult = roadGraph.NearestEdge(posOnEdge, sourcePoint, NTaxiExternal::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);
        UNIT_ASSERT(nearestEdgeResult);

        TPositionOnGraph posOnGraph = roadGraph.GetPositionOnGraph(posOnEdge);

        TPositionOnEdge posOnEdge2 = roadGraph.GetPositionOnEdge(posOnGraph);

        UNIT_ASSERT_EQUAL(posOnEdge.EdgeId, posOnGraph.EdgeId);
        UNIT_ASSERT(maps::geolib3::distance(
                        ToMapsPoint(ToInternal(roadGraph.GetCoords(posOnGraph))),
                        ToMapsPoint(ToInternal(roadGraph.GetCoords(posOnEdge2)))) < 0.001);
        UNIT_ASSERT(maps::geolib3::distance(
                        ToMapsPoint(ToInternal(sourcePoint)),
                        ToMapsPoint(ToInternal(roadGraph.GetCoords(posOnEdge2)))) < 0.001);

        TPositionOnGraph posOnGraph2 = roadGraph.GetPositionOnGraph(posOnEdge2);
        UNIT_ASSERT(maps::geolib3::distance(
                        ToMapsPoint(ToInternal(roadGraph.GetCoords(posOnGraph2))),
                        ToMapsPoint(ToInternal(roadGraph.GetCoords(posOnEdge2)))) < 0.001);
        UNIT_ASSERT(maps::geolib3::distance(
                        ToMapsPoint(ToInternal(sourcePoint)),
                        ToMapsPoint(ToInternal(roadGraph.GetCoords(posOnGraph2)))) < 0.001);
    }

    Y_UNIT_TEST(fb_segment_direction) {
        const auto& roadGraph = TestRoadGraph();

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

    Y_UNIT_TEST(fb_check_version) {
        const auto& graph = TestRoadGraph();

        const auto& version = graph.GetVersion();

        UNIT_ASSERT_STRINGS_EQUAL(version.Data(), "3.0.0-0");
    }

    Y_UNIT_TEST(get_reverse_edge_id_road) {
        const auto& roadGraph = TestRoadGraph();

        // point without reverse edge.
        TPoint sourcePoint{37.533547, 55.700951};
        TPositionOnEdge posOnEdge;
        bool nearestEdgeResult = roadGraph.NearestEdge(posOnEdge, sourcePoint, NTaxiExternal::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);
        UNIT_ASSERT(nearestEdgeResult);
        const auto& reverseEdgeId = roadGraph.GetReverseEdgeId(posOnEdge.EdgeId);
        UNIT_ASSERT_EQUAL(reverseEdgeId.isInitialized, false);

        // point with reverse edge.
        TPoint sourcePoint2{37.637338, 55.732212};
        TPositionOnEdge posOnEdge2;
        nearestEdgeResult = roadGraph.NearestEdge(posOnEdge2, sourcePoint2, NTaxiExternal::NGraph2::TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_ROADS, 1e2);
        UNIT_ASSERT(nearestEdgeResult);
        const auto& reverseEdgeId2 = roadGraph.GetReverseEdgeId(posOnEdge2.EdgeId);
        UNIT_ASSERT_EQUAL(reverseEdgeId2.isInitialized, true);
    }

    Y_UNIT_TEST(api_version) {
      UNIT_ASSERT(NTaxiExternal::NGraph2::ApiVersion() > 0);
    }

    Y_UNIT_TEST(IsPointOnRightSideOfEdge) {
        // Check that exception is catched
        const auto& roadGraph = TestRoadGraph();
        UNIT_ASSERT(!roadGraph.IsPointOnRightSideOfEdge(TPositionOnGraph{}, TPoint{}).isInitialized);
    }

}
