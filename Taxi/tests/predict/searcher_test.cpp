#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/search2/dijkstra_edge_searcher.h>
#include <taxi/graph/libs/predict/predictor_provider.h>

#include <iostream>

#include <taxi/graph/libs/graph-test/graph_test_data.h>

using namespace NTaxi::NGraph2Literals;

namespace {
    enum class ETestGraphType {
        BoomBarriers,
        ResidentialAreas
    };

    struct TTestFastDijkstraEdgeSearcher {
        using TGraph = NTaxi::NGraph2::TGraph;
        using TRoadGraphDataBuilder = NTaxi::NGraph2::TRoadGraphDataBuilder;
        using TEdge = NTaxi::NGraph2::TEdge;
        using TEdgeData = NTaxi::NGraph2::TEdgeData;
        using TPolyline = NTaxi::NGraph2::TPolyline;
        using TPositionOnEdge = NTaxi::NGraph2::TPositionOnEdge;
        using TId = NTaxi::NGraph2::TId;
        using TEdgeId = NTaxi::NGraph2::TEdgeId;
        using TVertexId = NTaxi::NGraph2::TVertexId;
        using TTime = NTaxi::NGraphSearch2::TTime;
        using TDistance = NTaxi::NGraphSearch2::TDistance;
        using TEdgeCategory = NTaxi::NGraph2::TEdgeCategory;

        using TTestSearchTraits = NTaxi::NPredict::NPredictorConsumerDetails::TPredictEdgesSearchTraits<NTaxi::NGraph2::TGraphFacadeCommon>;
        using TTestEdgeProcessor = NTaxi::NPredict::NPredictorConsumerDetails::TPredictEdgeProcessor;
        using TSearcher = NTaxi::NGraphSearch2::TFastDijkstraEdgeSearcher<
            NTaxi::NGraph2::TGraphFacadeCommon,
            TTestSearchTraits,
            TTestEdgeProcessor>;

        TTestFastDijkstraEdgeSearcher(ETestGraphType type)
            : Graph(PrepareGraph(type))
            , SearchSettings{
                  TTime{1 << 15},
                  TDistance{100000.0},
                  100000,
                  {}}
            , EdgeProcessor()
            , Searcher({Graph, Graph.GetEdgeStorage()}, SearchSettings, EdgeProcessor)
        {
        }

        template <typename... Args>
        auto Search(Args&&... args) {
            return Searcher.Search(std::forward<Args>(args)...);
        }

        size_t GetVisitedEdgesCount() const {
            return Searcher.GetVisitedEdgesInfo().size();
        }

        ///               edges
        ///                 x
        ///                 |
        ///                 |0
        ///                 x
        ///  pass/barrier 1/ \2 pass/barrier
        ///               /   \
        ///              x     x
        ///               \   /
        ///               3\ /4
        ///                 x
        ///                 |
        ///                 |5
        ///                 x
        static TGraph PrepareGraph(ETestGraphType type) {
            std::unique_ptr<TRoadGraphDataBuilder> graphBuilder = std::make_unique<TRoadGraphDataBuilder>(6, 6, 0);
            TEdgeData edgeData;
            edgeData.Speed = 1.;
            edgeData.Length = 15.;

            TPolyline geometry1;
            geometry1.AddPoint({0., 0.});
            geometry1.AddPoint({1., 1.});

            TEdgeData edgeData2 = edgeData;
            if (type == ETestGraphType::ResidentialAreas)
                edgeData2.Category = TEdgeCategory::EC_PASSES;
            TPolyline geometry2;
            geometry2.AddPoint({1., 1.});
            geometry2.AddPoint({2., 2.});

            TEdgeData edgeData3 = edgeData;
            if (type == ETestGraphType::ResidentialAreas)
                edgeData3.Category = TEdgeCategory::EC_PASSES;
            TPolyline geometry3;
            geometry3.AddPoint({1., 1.});
            geometry3.AddPoint({3., 3.});

            TPolyline geometry4;
            geometry4.AddPoint({2., 2.});
            geometry4.AddPoint({4., 4.});

            TPolyline geometry5;
            geometry5.AddPoint({3., 3.});
            geometry5.AddPoint({4., 4.});

            TPolyline geometry6;
            geometry6.AddPoint({4., 4.});
            geometry6.AddPoint({5., 5.});

            for (size_t i = 0; i < 6; ++i) {
                graphBuilder->SetVertexGeometry(maps::road_graph::VertexId(i), {static_cast<double>(i), static_cast<double>(i)});
            }

            graphBuilder->SetEdge(TEdge(TEdgeId{0}, TVertexId{0}, TVertexId{1}), true);
            graphBuilder->SetEdgeData(TEdgeId{0}, edgeData, geometry1);

            graphBuilder->SetEdge(TEdge(TEdgeId{1}, TVertexId{1}, TVertexId{2}), true);
            graphBuilder->SetEdgeData(TEdgeId{1}, edgeData2, geometry2);

            graphBuilder->SetEdge(TEdge(TEdgeId{2}, TVertexId{1}, TVertexId{3}), true);
            graphBuilder->SetEdgeData(TEdgeId{2}, edgeData3, geometry3);

            graphBuilder->SetEdge(TEdge(TEdgeId{3}, TVertexId{2}, TVertexId{4}), true);
            graphBuilder->SetEdgeData(TEdgeId{3}, edgeData, geometry4);

            graphBuilder->SetEdge(TEdge(TEdgeId{4}, TVertexId{3}, TVertexId{4}), true);
            graphBuilder->SetEdgeData(TEdgeId{4}, edgeData, geometry5);

            graphBuilder->SetEdge(TEdge(TEdgeId{5}, TVertexId{4}, TVertexId{5}), true);
            graphBuilder->SetEdgeData(TEdgeId{5}, edgeData, geometry6);

            if (type == ETestGraphType::BoomBarriers) {
                graphBuilder->AddAccessPass(TEdgeId{0}, TEdgeId{1});
                graphBuilder->AddAccessPass(TEdgeId{0}, TEdgeId{2});
            }

            graphBuilder->Build();
            auto ret = TGraph(std::move(graphBuilder));
            ret.BuildEdgeStorage(32);
            return ret;
        }

        TGraph Graph;
        NTaxi::NGraphSearch2::TFastSearchSettings SearchSettings;
        TTestEdgeProcessor EdgeProcessor;
        TSearcher Searcher;
    };
}

class TPredictSearcherFixture: public ::NUnitTest::TBaseTestCase, public NTaxi::NGraph2::TGraphTestData {
};

Y_UNIT_TEST_SUITE_F(graph_dijkstra_edge_search, TPredictSearcherFixture) {
    Y_UNIT_TEST(predict_search_rhombus_with_boom_barriers_entry_disabled) {
        TTestFastDijkstraEdgeSearcher testSearcherWithGraph(ETestGraphType::BoomBarriers);
        testSearcherWithGraph.Search(0_eid);

        UNIT_ASSERT_EQUAL(testSearcherWithGraph.GetVisitedEdgesCount(), 0);
    }
    Y_UNIT_TEST(predict_search_rhombus_with_residential_area_entry_disabled) {
        TTestFastDijkstraEdgeSearcher testSearcherWithGraph(ETestGraphType::ResidentialAreas);
        testSearcherWithGraph.Search(0_eid);

        UNIT_ASSERT_EQUAL(testSearcherWithGraph.GetVisitedEdgesCount(), 0);
    }
}
