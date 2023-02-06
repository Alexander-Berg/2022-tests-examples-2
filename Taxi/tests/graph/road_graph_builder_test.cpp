#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/nearest_edges/nearest_edges.h>
#include <taxi/graph/libs/graph/graph_data_builder.h>

using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TEdgeAccess;
using NTaxi::NGraph2::TEdgeCategory;
using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TNearestEdges;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TRoadGraphDataBuilder;

using namespace NTaxi::NGraph2Literals;

namespace {
    const TVector<TPoint> POINTS = {
        {1.5, 1.5},
        {2.5, 2.5},
    };

    /// @brief Generate simplest graph with only two vertices and one edge
    TGraph GetBaseGraph(TEdgeAccess access = TEdgeAccess::EA_AUTOMOBILE) {
        auto builder = std::make_unique<TRoadGraphDataBuilder>(2, 1, 0);

        TEdgeData edgeData;
        TPolyline geometry;
        TEdge edge;

        edge.Id = 0_eid;
        edge.Source = 0_vid;
        edge.Target = 1_vid;
        edgeData.Length = 10.0;
        edgeData.Access = access;
        geometry.AddPoint(POINTS[0]);
        geometry.AddPoint(POINTS[1]);

        builder->SetVertexGeometry(0_vid, POINTS[0]);
        builder->SetVertexGeometry(1_vid, POINTS[1]);
        builder->SetEdge(edge, true);
        builder->SetEdgeData(0_eid, edgeData, geometry);
        builder->Build();

        return TGraph(std::move(builder));
    }

}

Y_UNIT_TEST_SUITE(graph_builder_test) {
    Y_UNIT_TEST(test_build_version) {
        const auto& graph = GetBaseGraph();
        UNIT_ASSERT_STRINGS_EQUAL(graph.GetVersion().Data(), "test_version");
    }

    Y_UNIT_TEST(test_build_one_edge) {
        const auto& graph = GetBaseGraph();
        const auto& edgeData = graph.GetEdgeData(0_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(edgeData.Length, 10., 1e-2);

        const auto& edge = graph.GetEdge(0_eid);
        UNIT_ASSERT_EQUAL(edge.Id, 0_eid);
        UNIT_ASSERT_EQUAL(edge.Target, 1_vid);
        UNIT_ASSERT_EQUAL(edge.Source, 0_vid);

        const auto& geometry = graph.GetEdgeGeometry(0_eid);
        UNIT_ASSERT_EQUAL(geometry.PointsSize(), 2);
        UNIT_ASSERT_DOUBLES_EQUAL(geometry.PointAt(1).Lat, POINTS[1].Lat, 1e-2);
    }

    Y_UNIT_TEST(test_build_nearest_edge) {
        const auto& graph = GetBaseGraph();
        const auto position = TNearestEdges{graph}.NearestEdge(POINTS[1], TEdgeAccess::EA_UNKNOWN, TEdgeCategory::EC_UNKNOWN, 100.);
        UNIT_ASSERT(!position.IsUndefined());
        UNIT_ASSERT_EQUAL(position.GetEdgeId(), 0_eid);
        UNIT_ASSERT_DOUBLES_EQUAL(position.GetPosition(), 1., 1e-2);
    }

    Y_UNIT_TEST(test_access) {
        const TVector<TEdgeAccess> access_cases{
            TEdgeAccess::EA_UNKNOWN,
            TEdgeAccess::EA_PEDESTRIAN,
            TEdgeAccess::EA_TAXI,
            TEdgeAccess::EA_TRUCK,
            TEdgeAccess::EA_AUTOMOBILE,
            TEdgeAccess::EA_BICYCLE,
            TEdgeAccess::EA_BUS,
            TEdgeAccess::EA_AUTOMOBILE |
                TEdgeAccess::EA_TAXI,
            TEdgeAccess::EA_BUS |
                TEdgeAccess::EA_PEDESTRIAN |
                TEdgeAccess::EA_TRUCK,
            TEdgeAccess::EA_PEDESTRIAN |
                TEdgeAccess::EA_TAXI |
                TEdgeAccess::EA_TRUCK |
                TEdgeAccess::EA_BICYCLE |
                TEdgeAccess::EA_BUS,
            TEdgeAccess::EA_PEDESTRIAN |
                TEdgeAccess::EA_TAXI |
                TEdgeAccess::EA_TRUCK |
                TEdgeAccess::EA_AUTOMOBILE |
                TEdgeAccess::EA_BICYCLE |
                TEdgeAccess::EA_BUS};

        for (const auto& access : access_cases) {
            const auto& graph = GetBaseGraph(access);
            const auto& edgeData = graph.GetEdgeData(0_eid);

            UNIT_ASSERT_EQUAL(edgeData.Access, access);
        }
    }
}
