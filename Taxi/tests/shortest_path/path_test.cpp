#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/taxi/graph2/graph.h>
#include <yandex/taxi/graph2/shortest_path/path.h>

#include <taxi/graph/external/graph2/lib/shortest_path/path_impl.h>
#include <taxi/graph/external/graph2/lib/graph_impl.h>

using NTaxiExternal::NGraph2::TEdge;
using NTaxiExternal::NGraph2::TEdgeData;
using NTaxiExternal::NGraph2::TId;
using NTaxiExternal::NGraph2::TGraph;
using NTaxiExternal::NGraph2::TRoadGraphBuilder;
using NTaxiExternal::NGraph2::TPoint;
using NTaxiExternal::NGraph2::TPolyline;
using NTaxiExternal::NGraph2::TPolylineRef;
using NTaxiExternal::NGraph2::TPositionOnEdge;
using NTaxiExternal::NGraph2::TPositionOnGraph;
using NTaxiExternal::NGraph2::TRoadGraphFileLoader;
using NTaxiExternal::NGraph2::TSegment;
using NTaxiExternal::NShortestPath2::TPath;
using NTaxiExternal::NShortestPath2::TPathOnGraph;

bool operator==(const TPositionOnEdge& first, const TPositionOnEdge& second) noexcept {
    return first.EdgeId == second.EdgeId && first.Position == second.Position;
}

bool operator==(const TPositionOnGraph& first, const TPositionOnGraph& second) noexcept {
    return second.Position == first.Position && second.EdgeId == first.EdgeId && second.SegmentIndex == first.SegmentIndex;
}

namespace {
    TGraph& GetGraph() {
        static std::unique_ptr<TGraph> graph;
        if (graph)
            return *graph;
        auto builder = TRoadGraphBuilder::Create(16, 14, 0);

        TVector<TPoint> points;
        for (int i = 0; i < 16; i++) {
            const auto& point = TPoint{
                static_cast<double>(i),
                static_cast<double>(i)};
            points.push_back(point);
            builder->SetVertexGeometry(TId(i), point);
        };

        TEdgeData edgeData;
        for (size_t i = 2; i < points.size(); i++) {
            TPolyline polyline;
            polyline.AddPoint(points.at(0));
            polyline.AddPoint(points.at(i - 1));
            polyline.AddPoint(points.at(i));

            TEdge edge{TId{static_cast<unsigned int>(i) - 2},
                       TId{0}, TId{static_cast<unsigned int>(i)}};
            builder->SetEdge(edge, true);
            builder->SetEdgeData(TId{static_cast<unsigned int>(i) - 2}, edgeData, polyline);
        }

        builder->Build();
        graph.reset(new TGraph{std::move(builder)});
        return *graph;
    }
}

Y_UNIT_TEST_SUITE(shortest_path_test) {
    using TPath = NTaxiExternal::NShortestPath2::TPath;
    Y_UNIT_TEST(BaseInterface) {
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.info.length = 10.;
        TPath path(new TPath::TImpl(mapsPath, graph.Impl()));
        UNIT_ASSERT(path.Exists());
    }

    Y_UNIT_TEST(SourceAndTarget) {
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        const maps::road_graph::EdgeId edgeId{10};
        const maps::road_graph::SegmentIndex segmentId{2};
        const double position = 0.5;
        maps::analyzer::shortest_path::PointOnGraph mapsPoint{{edgeId, segmentId}, position};
        mapsPath.source = mapsPoint;
        mapsPath.target = mapsPoint;
        TPath path(new TPath::TImpl(mapsPath, graph.Impl()));
        // Check source point
        UNIT_ASSERT_EQUAL(path.GetSourcePoint().EdgeId, 10);
        UNIT_ASSERT_EQUAL(path.GetSourcePoint().SegmentIndex, 2);
        UNIT_ASSERT_DOUBLES_EQUAL(path.GetSourcePoint().Position, 0.5, 1e-2);
        // Check target point
        UNIT_ASSERT_EQUAL(path.GetTargetPoint().EdgeId, 10);
        UNIT_ASSERT_EQUAL(path.GetTargetPoint().SegmentIndex, 2);
        UNIT_ASSERT_DOUBLES_EQUAL(path.GetTargetPoint().Position, 0.5, 1e-2);
    }

    Y_UNIT_TEST(Edges) {
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.trace->edges.emplace_back(5);
        mapsPath.trace->edges.emplace_back(10);
        TPath path(new TPath::TImpl(mapsPath, graph.Impl()));
        Cout << path.GetEdges()[0] << ", " << path.GetEdges()[1] << Endl;
        UNIT_ASSERT_EQUAL(path.GetEdges().Size, 2);
        UNIT_ASSERT_EQUAL(path.GetEdges()[0], 5);
        UNIT_ASSERT_EQUAL(path.GetEdges()[1], 10);
    }

    Y_UNIT_TEST(Interpolation1) {
        // Path has only one segment
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        const maps::road_graph::EdgeId edgeId{5};
        const maps::road_graph::SegmentIndex segmentId{0};
        mapsPath.source = maps::analyzer::shortest_path::PointOnGraph{{edgeId, segmentId}, 0.0};
        mapsPath.target = maps::analyzer::shortest_path::PointOnGraph{{edgeId, segmentId}, 1.0};
        maps::analyzer::shortest_path::Route routeFromSource;
        using SegmentPart = maps::road_graph::SegmentPart;
        routeFromSource.push_back(SegmentPart({edgeId, segmentId}, 0.0, 1.0));

        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.trace->fromSource = routeFromSource;

        TPath path(new TPath::TImpl(mapsPath, graph.Impl()));
        TPathOnGraph pathOnGraph(path, graph);

        TPositionOnGraph middlePos = pathOnGraph.GetPointAt(0.5);

        UNIT_ASSERT_EQUAL(middlePos.EdgeId, 5);
        UNIT_ASSERT_EQUAL(middlePos.SegmentIndex, 0);
        UNIT_ASSERT_DOUBLES_EQUAL(middlePos.Position, 0.5, 1e-2);
    }

    Y_UNIT_TEST(Interpolation2) {
        // Path has only two segments:
        // one from [0,0] to [4,4] and second from [4,4] to [5,5]
        // Path is from 0.1 of first segment to 0.8 of second one
        // Total len is 0.9 * 4*sqrt(2) + 0.8 * 1 = 5.8911 (truncated)
        // Middle point is path start + 2.94555 along it = 3.5112 alongh the
        // path = 0.62 alongh the segment
        // The middle point is still strictly inside segment one
        // The middle point is approx [2.4828, 2.4828]
        const maps::road_graph::EdgeId edgeId{5};
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.source = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{0}}, 0.1};
        mapsPath.target = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{1}}, 0.8};
        // Because we have non-full segments, we can't simply use insertEdgeId
        // mapsPath.insertEdgeId(5);
        // instead we use routeFromSource and routeToTarget
        // And because we have only 1 edge with 2 segments, there is no need
        // for insertEdgeId at all
        // And we can use only routeFromSource
        maps::analyzer::shortest_path::Route routeFromSource;
        using SegmentPart = maps::road_graph::SegmentPart;
        // segment from start point to end of segment (thus 0.1 to 1.0)
        routeFromSource.push_back(SegmentPart({edgeId, maps::road_graph::SegmentIndex{0}}, 0.1, 1.0));
        // segment from start of next segment to end point
        routeFromSource.push_back(SegmentPart({edgeId, maps::road_graph::SegmentIndex{1}}, 0.0, 0.8));

        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.trace->fromSource = routeFromSource;

        TPath path(new TPath::TImpl(mapsPath, graph.Impl()));
        TPathOnGraph pathOnGraph(path, graph);

        TPositionOnGraph middlePos = pathOnGraph.GetPointAt(0.5);

        UNIT_ASSERT_EQUAL(middlePos.EdgeId, 5);
        UNIT_ASSERT_EQUAL(middlePos.SegmentIndex, 0);
        UNIT_ASSERT_DOUBLES_EQUAL(middlePos.Position, 0.62, 1e-1);
    }
}
