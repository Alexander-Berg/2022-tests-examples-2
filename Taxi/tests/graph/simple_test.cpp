#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/maps/jams/static_graph2/builder.h>
#include <yandex/maps/jams/static_graph2/graph.h>
#include <maps/libs/geolib/include/point.h>
#include <yandex/maps/mms/cast.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/nearest_edges/nearest_edges.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

#include <util/system/backtrace.h>

using maps::geolib3::Point2;
using GraphBuilder = NTaxi::NGraph2::TRoadGraphDataBuilder;
using TaxiGraph = NTaxi::NGraph2::TGraph;
using TEdgeAccess = NTaxi::NGraph2::TEdgeAccess;
using TEdgeCategory = NTaxi::NGraph2::TEdgeCategory;
using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TNearestEdges;
using NTaxi::NGraph2::TPoint;

using namespace NTaxi::NGraph2Literals;

namespace {

    TaxiGraph BuildGraph(TEdgeAccess access = TEdgeAccess::EA_AUTOMOBILE) {
        const std::vector<TPoint> vertices = {
            {37.5, 55.5},
            {37.0, 55.5},
        };
        const std::vector<NTaxi::NGraph2::TEdge> edges = {
            TEdge{NTaxi::NGraph2::TEdgeId{0}, NTaxi::NGraph2::TVertexId{0}, NTaxi::NGraph2::TVertexId{1}},
        };
        auto builder = std::make_unique<GraphBuilder>(2, 1, 0);
        {
            for (size_t i = 0; i < vertices.size(); i++) {
                builder->SetVertexGeometry(NTaxi::NGraph2::TVertexId(i), vertices[i]);
            }

            for (const auto& edgeInfo : edges) {
                NTaxi::NGraph2::TEdgeData edgeData;
                const auto& pointSource = vertices.at(edgeInfo.Source.value());
                const auto& pointTarget = vertices.at(edgeInfo.Target.value());
                // we need to fill length for rtree search
                edgeData.Length = maps::geolib3::geoDistance(
                    pointSource,
                    pointTarget);
                NTaxi::NGraph2::TPolyline geometry;
                geometry.AddPoint(pointSource);
                geometry.AddPoint(pointTarget);

                edgeData.Access = access;

                builder->SetEdge(NTaxi::NGraph2::TEdge(
                    edgeInfo.Id,
                    edgeInfo.Source,
                    edgeInfo.Target
                ), true);
                builder->SetEdgeData(edgeInfo.Id, edgeData, geometry);
            }
            builder->Build();
        }
        return TaxiGraph(std::move(builder));
    }

}

struct TGraphTestFixture: public ::NUnitTest::TBaseTestCase,
                           public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_load_test, TGraphTestFixture) {
    Y_UNIT_TEST(load_from_file) {
        const auto& graph = GetTestRoadGraph();
        // Test for nearest edge: https://yandex.ru/maps/-/CBuF6Aww~B
        const TPoint pt{37.645995, 55.737224};
        const auto& edge = TNearestEdges{graph}.NearestEdge(pt, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2);
        const auto& geometry = graph.GetEdgeGeometry(edge.GetEdgeId());
        const TPoint& adjustetPoint = geometry.PointAt(0);
        UNIT_ASSERT_DOUBLES_EQUAL(37.645646, adjustetPoint.Lon, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(55.736541, adjustetPoint.Lat, 1e-6);
    }

    Y_UNIT_TEST(simple_build_graph) {
        TaxiGraph graph(BuildGraph());

        // Simple check nearest edge
        const TPoint pt{37.500995, 55.500224};
        const auto& edge = TNearestEdges{graph}.NearestEdge(pt, TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_ROADS, 1e2);
        UNIT_ASSERT_EQUAL(edge.GetEdgeId(), 0_eid);
        const auto& geometry = graph.GetEdgeGeometry(edge.GetEdgeId());
        const TPoint& adjustetPoint = geometry.PointAt(0);
        UNIT_ASSERT_DOUBLES_EQUAL(37.5, adjustetPoint.Lon, 1e-6);
        UNIT_ASSERT_DOUBLES_EQUAL(55.5, adjustetPoint.Lat, 1e-6);

        {
            NTaxi::NGraph2::TPositionOnEdge poe;
            poe = TNearestEdges{graph}.NearestEdge(pt, TEdgeAccess::EA_AUTOMOBILE, TEdgeCategory::EC_PASSES, 100);
            UNIT_ASSERT(poe.GetEdgeId() != NTaxi::NGraph2::UNDEFINED);

            poe = TNearestEdges{graph}.NearestEdge(pt, TEdgeAccess::EA_TRUCK, TEdgeCategory::EC_PASSES, 100);
            UNIT_ASSERT(poe.GetEdgeId() == NTaxi::NGraph2::UNDEFINED);
        }
    }

    Y_UNIT_TEST(test_access_id) {
        const TVector<TEdgeAccess> access_cases{
            TEdgeAccess::EA_UNKNOWN,
            TEdgeAccess::EA_PEDESTRIAN,
            TEdgeAccess::EA_TAXI,
            TEdgeAccess::EA_TRUCK,
            TEdgeAccess::EA_AUTOMOBILE,
            TEdgeAccess::EA_BICYCLE,
            TEdgeAccess::EA_AUTOMOBILE |
                TEdgeAccess::EA_TAXI,
            TEdgeAccess::EA_PEDESTRIAN |
                TEdgeAccess::EA_TRUCK,
            TEdgeAccess::EA_PEDESTRIAN |
                TEdgeAccess::EA_TAXI |
                TEdgeAccess::EA_TRUCK |
                TEdgeAccess::EA_BICYCLE,
            TEdgeAccess::EA_PEDESTRIAN |
                TEdgeAccess::EA_TAXI |
                TEdgeAccess::EA_TRUCK |
                TEdgeAccess::EA_AUTOMOBILE |
                TEdgeAccess::EA_BICYCLE,
        };

        for (const auto& access : access_cases) {
            const TaxiGraph graph{BuildGraph(access)};
            const auto& edgeData = graph.GetEdgeData(0_eid);

            UNIT_ASSERT_EQUAL(edgeData.Access, access);
        }
    }
}
