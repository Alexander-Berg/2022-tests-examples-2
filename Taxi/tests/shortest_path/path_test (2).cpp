#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/graph/graph_data_storage.h>
#include <taxi/graph/libs/shortest_path/path.h>
#include <taxi/graph/libs/shortest_path/path_on_graph.h>

using NTaxi::NGraph2::TEdge;
using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TPositionOnGraph;
using NTaxi::NGraph2::TRoadGraphDataStorage;
using NTaxi::NGraph2::TSegment;
using NTaxi::NGraph2::TRoadGraphDataBuilder;
using NTaxi::NGraph2::TVertexId;

using namespace NTaxi::NShortestPath2;
using namespace NTaxi::NGraph2Literals;

namespace {
    const TFsPath GRAPH_PATH = BinaryPath("taxi/graph/data/graph3");

    TGraph& GetGraph() {
        static std::unique_ptr<TGraph> graph;
        if (graph) {
            return *graph;
        }

        auto builder = std::make_unique<TRoadGraphDataBuilder>(16, 14, 0);

        TVector<TPoint> points;
        for (int i = 0; i < 16; i++) {
            const auto& point = TPoint{
                static_cast<double>(i),
                static_cast<double>(i)};
            points.push_back(point);
            builder->SetVertexGeometry(TVertexId(i), point);
        };

        TEdgeData edgeData;
        for (size_t i = 2; i < points.size(); i++) {
            TPolyline polyline;
            polyline.AddPoint(points.at(0));
            polyline.AddPoint(points.at(i - 1));
            polyline.AddPoint(points.at(i));

            TEdge edge(TEdgeId{static_cast<unsigned int>(i) - 2},
                       TVertexId{0}, TVertexId{static_cast<unsigned int>(i)});
            builder->SetEdge(edge, true);
            builder->SetEdgeData(TEdgeId{static_cast<unsigned int>(i) - 2}, edgeData, polyline);
        }
        builder->Build();
        graph.reset(new TGraph{std::move(builder)});
        return *graph;
    }

    bool IsEqual(const TPoint& point1, const TPoint& point2) {
        return (point1.Lon == point2.Lon) && (point2.Lat == point2.Lat);
    }

    bool IsEqual(const TSegment& seg1, const TSegment& seg2) {
        return IsEqual(seg1.Start, seg2.Start) && IsEqual(seg1.End, seg2.End);
    }

    bool IsEqual(const TPolyline& pol1, const TPolyline& pol2) {
        /// check segments
        {
            if (pol1.SegmentsSize() != pol2.SegmentsSize())
                return false;

            const auto seg_size = pol1.SegmentsSize();
            for (size_t i = 0; i < seg_size; i++) {
                if (!IsEqual(pol1.SegmentAt(i), pol2.SegmentAt(i)))
                    return false;
            }
        }

        /// check points
        {
            if (pol1.PointsSize() != pol2.PointsSize())
                return false;

            const auto points_size = pol1.PointsSize();
            for (size_t i = 0; i < points_size; i++) {
                if (!IsEqual(pol1.PointAt(i), pol2.PointAt(i)))
                    return false;
            }
        }

        return true;
    }

    const TGraph& GetTestRoadGraph() {
        static const TGraph graph(std::make_unique<TRoadGraphDataStorage>(
            GRAPH_PATH, EMappingMode::Precharged));
        return graph;
    }
}

bool operator==(const TPositionOnEdge& first, const TPositionOnEdge& second) noexcept {
    return first.GetEdgeId() == second.GetEdgeId() && first.GetPosition() == second.GetPosition();
}

bool operator==(const TPositionOnGraph& first, const TPositionOnGraph& second) noexcept {
    return second.GetSegmentPosition() == first.GetSegmentPosition() && second.GetEdgeId() == first.GetEdgeId() && second.GetSegmentIdx() == first.GetSegmentIdx();
}

Y_UNIT_TEST_SUITE(shortest_path_test) {
    Y_UNIT_TEST(BaseInterface) {
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.info.length = 10.;
        TPath path(mapsPath, graph);
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
        TPath path(mapsPath, graph);

        // Check source point
        UNIT_ASSERT_EQUAL(path.GetSourcePoint().GetEdgeId(), TEdgeId{edgeId});
        UNIT_ASSERT_EQUAL(path.GetSourcePoint().GetSegmentIdx(), 2);
        UNIT_ASSERT_DOUBLES_EQUAL(path.GetSourcePoint().GetSegmentPosition(), 0.5, 1e-2);

        // Check target point
        UNIT_ASSERT_EQUAL(path.GetTargetPoint().GetEdgeId(), TEdgeId{edgeId});
        UNIT_ASSERT_EQUAL(path.GetTargetPoint().GetSegmentIdx(), 2);
        UNIT_ASSERT_DOUBLES_EQUAL(path.GetTargetPoint().GetSegmentPosition(), 0.5, 1e-2);
    }

    Y_UNIT_TEST(Edges) {
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.trace->edges.emplace_back(5);
        mapsPath.trace->edges.emplace_back(10);
        TPath path(mapsPath, graph);
        UNIT_ASSERT_EQUAL(path.GetEdges().size(), 2);
        UNIT_ASSERT_EQUAL(path.GetEdges()[0], 5_eid);
        UNIT_ASSERT_EQUAL(path.GetEdges()[1], 10_eid);
    }

    Y_UNIT_TEST(Interpolation1) {
        const auto& graph = GetGraph();

        // Path has only one segment
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

        TPath path(mapsPath, graph);
        TPathOnGraph pathOnGraph(path, graph);

        TPositionOnGraph middlePos = pathOnGraph.GetPointAt(0.5);

        UNIT_ASSERT_EQUAL(middlePos.GetEdgeId(), TEdgeId{edgeId});
        UNIT_ASSERT_EQUAL(middlePos.GetSegmentIdx(), segmentId.value());
        UNIT_ASSERT_DOUBLES_EQUAL(middlePos.GetSegmentPosition(), 0.5, 1e-2);
    }

    Y_UNIT_TEST(Interpolation2) {
        // Path has only two segments:
        // one from [0,0] to [4,4] and second from [4,4] to [5,5]
        // Path is from 0.1 of first segment to 0.8 of second one
        // Total len is 0.9 * 4*sqrt(2) + 0.8 * 1 = 5.8911 (truncated)
        // Middle point is path Start + 2.94555 along it = 3.5112 alongh the
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
        // segment from Start point to End of segment (thus 0.1 to 1.0)
        routeFromSource.push_back(SegmentPart({edgeId, maps::road_graph::SegmentIndex{0}}, 0.1, 1.0));
        // segment from Start of next segment to End point
        routeFromSource.push_back(SegmentPart({edgeId, maps::road_graph::SegmentIndex{1}}, 0.0, 0.8));

        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.trace->fromSource = routeFromSource;

        TPath path(mapsPath, graph);
        TPathOnGraph pathOnGraph(path, graph);

        TPositionOnGraph middlePos = pathOnGraph.GetPointAt(0.5);

        UNIT_ASSERT_EQUAL(middlePos.GetEdgeId(), TEdgeId{edgeId});
        UNIT_ASSERT_EQUAL(middlePos.GetSegmentIdx(), 0);
        UNIT_ASSERT_DOUBLES_EQUAL(middlePos.GetSegmentPosition(), 0.62, 1e-1);
    }

    Y_UNIT_TEST(TPathNewConstructorSameEdge) {
        // Path has only two segments.
        const maps::road_graph::EdgeId edgeId{5};
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.source = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{0}}, 0.1};
        mapsPath.target = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{1}}, 0.8};
        maps::analyzer::shortest_path::Route routeFromSource;
        using SegmentPart = maps::road_graph::SegmentPart;
        // segment from Start point to End of segment (thus 0.1 to 1.0)
        routeFromSource.push_back(SegmentPart({edgeId, maps::road_graph::SegmentIndex{0}}, 0.1, 1.0));
        // segment from Start of next segment to End point
        routeFromSource.push_back(SegmentPart({edgeId, maps::road_graph::SegmentIndex{1}}, 0.0, 0.8));

        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.trace->fromSource = routeFromSource;

        TPath path(mapsPath, graph);
        TPath pathFromData(path.GetSourcePoint(), path.GetTargetPoint(), path.GetEdges(), graph);

        TPathOnGraph pathOnGraph(path, graph);
        TPathOnGraph pathOnGraphFromData(pathFromData, graph);

        UNIT_ASSERT_EQUAL(pathOnGraphFromData.Exists(), true);

        UNIT_ASSERT_EQUAL(pathOnGraph.GetSourcePoint(), pathOnGraphFromData.GetSourcePoint());
        UNIT_ASSERT_EQUAL(pathOnGraph.GetTargetPoint(), pathOnGraphFromData.GetTargetPoint());
        UNIT_ASSERT_DOUBLES_EQUAL(pathOnGraph.GetFastGeoLength(), pathOnGraphFromData.GetFastGeoLength(), 1e-1);

        TPositionOnGraph middlePos1 = pathOnGraph.GetPointAt(0.5);
        TPositionOnGraph middlePos2 = pathOnGraphFromData.GetPointAt(0.5);
        UNIT_ASSERT_EQUAL(middlePos1, middlePos2);

        UNIT_ASSERT_EQUAL(IsEqual(pathOnGraph.GetGeometry(), pathOnGraphFromData.GetGeometry()), true);

        // check edge ids.
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetEdgeIds().size(), 1);
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetEdgeIds()[0], TEdgeId{edgeId});

        // edge geometry is the same as all path, because only one edge in path.
        UNIT_ASSERT_EQUAL(IsEqual(pathOnGraphFromData.GetGeometryForEdge(0), pathOnGraphFromData.GetGeometry()), true);
    }

    Y_UNIT_TEST(TPathNewConstructorSameEdgeSameSegment) {
        // Path has only one segment.
        const maps::road_graph::EdgeId edgeId{5};
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.source = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{0}}, 0.1};
        mapsPath.target = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{0}}, 0.7};
        maps::analyzer::shortest_path::Route routeFromSource;
        using SegmentPart = maps::road_graph::SegmentPart;
        // segment from Start point to End of segment (thus 0.1 to 0.7)
        routeFromSource.push_back(SegmentPart({edgeId, maps::road_graph::SegmentIndex{0}}, 0.1, 0.7));

        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.trace->fromSource = routeFromSource;

        TPath path(mapsPath, graph);
        TPath pathFromData(path.GetSourcePoint(), path.GetTargetPoint(), path.GetEdges(), graph);

        TPathOnGraph pathOnGraph(path, graph);
        TPathOnGraph pathOnGraphFromData(pathFromData, graph);

        UNIT_ASSERT_EQUAL(pathOnGraphFromData.Exists(), true);

        UNIT_ASSERT_EQUAL(pathOnGraph.GetSourcePoint(), pathOnGraphFromData.GetSourcePoint());
        UNIT_ASSERT_EQUAL(pathOnGraph.GetTargetPoint(), pathOnGraphFromData.GetTargetPoint());
        UNIT_ASSERT_DOUBLES_EQUAL(pathOnGraph.GetFastGeoLength(), pathOnGraphFromData.GetFastGeoLength(), 1e-1);

        TPositionOnGraph middlePos1 = pathOnGraph.GetPointAt(0.5);
        TPositionOnGraph middlePos2 = pathOnGraphFromData.GetPointAt(0.5);
        UNIT_ASSERT_EQUAL(middlePos1, middlePos2);

        UNIT_ASSERT_EQUAL(IsEqual(pathOnGraph.GetGeometry(), pathOnGraphFromData.GetGeometry()), true);

        // check edge ids.
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetEdgeIds().size(), 1);
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetEdgeIds()[0], TEdgeId{edgeId});

        // edge geometry is the same as all path, because only one edge in path.
        UNIT_ASSERT_EQUAL(IsEqual(pathOnGraphFromData.GetGeometryForEdge(0), pathOnGraphFromData.GetGeometry()), true);
    }

    Y_UNIT_TEST(TPathNewConstructorDifferentEdge) {
        using SegmentPart = maps::road_graph::SegmentPart;

        // Path has 2 segments(not full) on first edge, next edge, and one segment from third edge.
        const maps::road_graph::EdgeId edgeId1{5};
        const maps::road_graph::EdgeId edgeId2{6};
        const maps::road_graph::EdgeId edgeId3{7};
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.source = maps::analyzer::shortest_path::PointOnGraph{{edgeId1, maps::road_graph::SegmentIndex{0}}, 0.1};
        mapsPath.trace->edges.push_back(edgeId2);
        mapsPath.target = maps::analyzer::shortest_path::PointOnGraph{{edgeId3, maps::road_graph::SegmentIndex{0}}, 0.1};

        maps::analyzer::shortest_path::Route routeFromSource;
        // segment from Start point to End of segment (thus 0.1 to 1.0)
        routeFromSource.push_back(SegmentPart({edgeId1, maps::road_graph::SegmentIndex{0}}, 0.1, 1.0));
        // two more full segments until End of edge.
        routeFromSource.push_back(SegmentPart({edgeId1, maps::road_graph::SegmentIndex{1}}));
        mapsPath.trace->fromSource = routeFromSource;

        maps::analyzer::shortest_path::Route routeToTarget;
        // segment Start to target (thus 0.0 to 0.1)
        routeToTarget.push_back(SegmentPart({edgeId2, maps::road_graph::SegmentIndex{0}}, 0.0, 0.1));
        mapsPath.trace->toTarget = routeToTarget;

        TPath path(mapsPath, graph);
        TPath pathFromData(path.GetSourcePoint(), path.GetTargetPoint(), path.GetEdges(), graph);

        TPathOnGraph pathOnGraph(path, graph);
        TPathOnGraph pathOnGraphFromData(pathFromData, graph);

        UNIT_ASSERT_EQUAL(pathOnGraphFromData.Exists(), true);

        UNIT_ASSERT_EQUAL(pathOnGraph.GetSourcePoint(), pathOnGraphFromData.GetSourcePoint());
        UNIT_ASSERT_EQUAL(pathOnGraph.GetTargetPoint(), pathOnGraphFromData.GetTargetPoint());
        UNIT_ASSERT_DOUBLES_EQUAL(pathOnGraph.GetFastGeoLength(), pathOnGraphFromData.GetFastGeoLength(), 1e-1);

        TPositionOnGraph middlePos1 = pathOnGraph.GetPointAt(0.5);
        TPositionOnGraph middlePos2 = pathOnGraphFromData.GetPointAt(0.5);
        UNIT_ASSERT_EQUAL(middlePos1, middlePos2);

        UNIT_ASSERT_EQUAL(IsEqual(pathOnGraph.GetGeometry(), pathOnGraphFromData.GetGeometry()), true);

        // check edge ids.
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetEdgeIds().size(), 3);
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetEdgeIds()[0], edgeId1);
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetEdgeIds()[1], edgeId2);
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetEdgeIds()[2], edgeId3);

        // check all edges geometry segment sizes.
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetGeometryForEdge(0).SegmentsSize(), 2);
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetGeometryForEdge(1).SegmentsSize(), 2);
        UNIT_ASSERT_EQUAL(pathOnGraphFromData.GetGeometryForEdge(2).SegmentsSize(), 1);
    }

    Y_UNIT_TEST(TPathNewConstructorSameTargetAndSourcePoint) {
        // Path has only one segment.
        const maps::road_graph::EdgeId edgeId{5};
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.source = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{0}}, 0.1};
        mapsPath.target = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{0}}, 0.7};
        maps::analyzer::shortest_path::Route routeFromSource;
        using SegmentPart = maps::road_graph::SegmentPart;
        // segment from Start point to End of segment (thus 0.1 to 0.7)
        routeFromSource.push_back(SegmentPart({edgeId, maps::road_graph::SegmentIndex{0}}, 0.1, 0.7));

        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.trace->fromSource = routeFromSource;

        TPath path(mapsPath, graph);
        TPath pathFromData(path.GetSourcePoint(), path.GetSourcePoint(), path.GetEdges(), graph);

        UNIT_ASSERT_EQUAL(pathFromData.Exists(), false);
    }

    Y_UNIT_TEST(TPathNewConstructorTargetLessThanSource) {
        // Path has only one segment.
        const maps::road_graph::EdgeId edgeId{5};
        const auto& graph = GetGraph();
        maps::analyzer::shortest_path::Path mapsPath;
        mapsPath.source = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{0}}, 0.1};
        mapsPath.target = maps::analyzer::shortest_path::PointOnGraph{{edgeId, maps::road_graph::SegmentIndex{0}}, 0.7};
        maps::analyzer::shortest_path::Route routeFromSource;
        using SegmentPart = maps::road_graph::SegmentPart;
        // segment from Start point to End of segment (thus 0.1 to 0.7)
        routeFromSource.push_back(SegmentPart({edgeId, maps::road_graph::SegmentIndex{0}}, 0.1, 0.7));

        mapsPath.trace = maps::analyzer::shortest_path::PathTrace();
        mapsPath.trace->fromSource = routeFromSource;

        TPath path(mapsPath, graph);
        TPath pathFromData(path.GetTargetPoint(), path.GetSourcePoint(), path.GetEdges(), graph);

        UNIT_ASSERT_EQUAL(pathFromData.Exists(), false);
    }
}

Y_UNIT_TEST_SUITE(shortest_path_road_graph_test) {
    Y_UNIT_TEST(TPathNewConstructorOneEdge) {
        // Path has only one segment.
        const NTaxi::NGraph2::TId edgeId = 90_eid;
        const auto& graph = GetTestRoadGraph();

        const auto startPos = graph.GetPositionOnGraph(NTaxi::NGraph2::TPositionOnEdge(edgeId, 0.1));
        const auto endPos = graph.GetPositionOnGraph(NTaxi::NGraph2::TPositionOnEdge(edgeId, 0.7));

        // just empty, because there is no edges between Start and finish edge.
        TVector<NTaxi::NGraph2::TId> edgeIds;

        TPath path(startPos, endPos, edgeIds, graph);

        UNIT_ASSERT_EQUAL(path.Exists(), true);

        TPathOnGraph pathOnGraph(path, graph);

        // check edge ids.
        UNIT_ASSERT_EQUAL(pathOnGraph.GetEdgeIds().size(), 1);
        UNIT_ASSERT_EQUAL(pathOnGraph.GetEdgeIds()[0], edgeId);

        // check all edges geometry segment sizes.
        UNIT_ASSERT_EQUAL(pathOnGraph.GetGeometryForEdge(0).SegmentsSize(), 1);
    }

    Y_UNIT_TEST(TPathNewConstructorTwoEdges) {
        // Path has only one segment.
        const NTaxi::NGraph2::TId startEdgeId = 276_eid;
        const NTaxi::NGraph2::TId endEdgeId = 239_eid;
        const auto& graph = GetTestRoadGraph();

        const auto startPos = graph.GetPositionOnGraph(NTaxi::NGraph2::TPositionOnEdge(startEdgeId, 0.1));
        const auto endPos = graph.GetPositionOnGraph(NTaxi::NGraph2::TPositionOnEdge(endEdgeId, 0.7));

        // just empty, because there is no edges between Start and finish edge.
        TVector<NTaxi::NGraph2::TId> edgeIds;

        TPath path(startPos, endPos, edgeIds, graph);

        UNIT_ASSERT_EQUAL(path.Exists(), true);

        TPathOnGraph pathOnGraph(path, graph);

        // check edge ids.
        UNIT_ASSERT_EQUAL(pathOnGraph.GetEdgeIds().size(), 2);
        UNIT_ASSERT_EQUAL(pathOnGraph.GetEdgeIds()[0], startEdgeId);
        UNIT_ASSERT_EQUAL(pathOnGraph.GetEdgeIds()[1], endEdgeId);

        // check all edges geometry segment sizes.
        UNIT_ASSERT_EQUAL(pathOnGraph.GetGeometryForEdge(0).SegmentsSize(), 1);
        UNIT_ASSERT_EQUAL(pathOnGraph.GetGeometryForEdge(1).SegmentsSize(), 1);
    }
}
