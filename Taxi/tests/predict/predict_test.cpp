#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <util/stream/file.h>

#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/graph_data_builder.h>
#include <taxi/graph/libs/graph/possible_position_on_edge.h>
#include <taxi/graph/libs/predict/probability_table.h>
#include <taxi/graph/libs/predict/writer_dijkstra_actions.h>
#include <taxi/graph/libs/predict/predict_search_actions.h>

#include <util/folder/path.h>

#include <iostream>
#include <fstream>
#include <filesystem>

using namespace std;
using namespace NTaxi::NGraph2Literals;

struct TPredictTestFixture: public ::NUnitTest::TBaseTestCase {
    /* A mix of taxi/graph wrappers and classes from original
     * maps/analyzer/libs/deprecated/mapmatcher library is used.
     * As such, it is easier to put necessary typedefs
     * directly inside class body
     *
     */
    using TGraph = NTaxi::NGraph2::TGraph;
    using TRoadGraphDataBuilder = NTaxi::NGraph2::TRoadGraphDataBuilder;
    using TEdge = NTaxi::NGraph2::TEdge;
    using TEdgeData = NTaxi::NGraph2::TEdgeData;
    using TPolyline = NTaxi::NGraph2::TPolyline;
    using TPersistentIndex = NTaxi::NGraph2::TPersistentIndex;
    using TPersistentIndexBuilder = NTaxi::NGraph2::TPersistentIndexBuilder;
    using TPositionOnEdge = NTaxi::NGraph2::TPositionOnEdge;
    using TPossiblePositionOnEdge = NTaxi::NGraph2::TPossiblePositionOnEdge;
    using TTableWriter = NTaxi::NPredict::TTableWriter;
    using TTableWriterActions = NTaxi::NPredict::TTableWriterActions;
    using TPredictSearchActions = NTaxi::NPredict::TPredictSearchActions;
    using TProbabilityTable = NTaxi::NPredict::TProbabilityTable;
    using TDijkstraSearcher = NTaxi::NGraphSearch2::TDijkstraSearcher;
    using TId = NTaxi::NGraph2::TId;
    using TEdgeId = NTaxi::NGraph2::TEdgeId;
    using TPersistentEdgeId = NTaxi::NGraph2::TPersistentEdgeId;
    using TVertexId = NTaxi::NGraph2::TVertexId;

    const size_t TESTS_NUMBER = 5;

    class TTestPredictActions: public NTaxi::NPredict::IPredictActions {
    public:
        TTestPredictActions(TVector<TPossiblePositionOnEdge>& outputVector)
            : Output(outputVector)
        {
        }

        void OnStartPredict(const TPositionOnEdge& startPosition) final {
        }

        void OnFoundPosition(const TPossiblePositionOnEdge& pos) final {
            Output.push_back(pos);
        }

    private:
        TVector<TPossiblePositionOnEdge>& Output;
    };

    TPredictTestFixture()
        : Graph(PrepareGraph())
        , Index(PrepareIndex())
        , ProbabilityTable(PrepareTable())
    {
    }

    void UnitAssertEdgeProbability(TPersistentEdgeId from) {
        auto probList = ProbabilityTable->GetProbabilityList(from);
        UNIT_ASSERT(probList.size() != 0);
        double probability = 1.0 / static_cast<double>(probList.size());
        for (auto& item : probList) {
            UNIT_ASSERT_DOUBLES_EQUAL(item.Probability, probability, 1e-2);
        }
    }

    static TPersistentIndex PrepareIndex() {
        TPersistentIndexBuilder indexBuilder;
        for (size_t i = 0; i < 6; ++i) {
            indexBuilder.Add(TPersistentEdgeId{i}, TEdgeId{static_cast<unsigned int>(i)});
        }

        return indexBuilder.Build("persistent_index.fb");
    }

    static std::unique_ptr<NTaxi::NGraph2::TGraphDataStorage> PrepareGraph() {
        std::unique_ptr<TRoadGraphDataBuilder> graphBuilder = std::make_unique<TRoadGraphDataBuilder>(6, 6, 0);
        TEdgeData edgeData;
        edgeData.Speed = 1.;
        edgeData.Length = 15.;

        TPolyline geometry1;
        geometry1.AddPoint({0., 0.});
        geometry1.AddPoint({1., 1.});

        TPolyline geometry2;
        geometry2.AddPoint({1., 1.});
        geometry2.AddPoint({2., 2.});

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
        graphBuilder->SetEdgeData(TEdgeId{1}, edgeData, geometry2);

        graphBuilder->SetEdge(TEdge(TEdgeId{2}, TVertexId{1}, TVertexId{3}), true);
        graphBuilder->SetEdgeData(TEdgeId{2}, edgeData, geometry3);

        graphBuilder->SetEdge(TEdge(TEdgeId{3}, TVertexId{2}, TVertexId{4}), true);
        graphBuilder->SetEdgeData(TEdgeId{3}, edgeData, geometry4);

        graphBuilder->SetEdge(TEdge(TEdgeId{4}, TVertexId{3}, TVertexId{4}), true);
        graphBuilder->SetEdgeData(TEdgeId{4}, edgeData, geometry5);

        graphBuilder->SetEdge(TEdge(TEdgeId{5}, TVertexId{4}, TVertexId{5}), true);
        graphBuilder->SetEdgeData(TEdgeId{5}, edgeData, geometry6);

        graphBuilder->Build();
        return graphBuilder;
    }

    std::unique_ptr<TProbabilityTable> PrepareTable() {
        TTableWriter tableWriter;
        TTableWriterActions writerActions(Index, tableWriter, 4);
        TDijkstraSearcher searcher(Graph, writerActions);
        searcher.Search(0_eid);
        return tableWriter.Finish("test.fb");
    }

public:
    NTaxi::NGraph2::TGraph Graph;
    NTaxi::NGraph2::TPersistentIndex Index;
    std::unique_ptr<TProbabilityTable> ProbabilityTable = nullptr;
};

Y_UNIT_TEST_SUITE_F(predict_test, TPredictTestFixture) {
    Y_UNIT_TEST(table_writer_test) {
        for (size_t i = 0; i < 5; ++i) {
            UnitAssertEdgeProbability(TPersistentEdgeId{i});
        }
    }

    Y_UNIT_TEST(vanga_test_1) {
        TVector<TPossiblePositionOnEdge> possiblePositions;
        TTestPredictActions testPredictActions(possiblePositions);
        TPredictSearchActions predictActions(Graph, {0_eid, 1.0}, Index, *ProbabilityTable, 15, testPredictActions);
        TDijkstraSearcher searcher(Graph, predictActions);
        searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(possiblePositions.size(), 2);
        for (size_t i = 0; i < possiblePositions.size(); ++i) {
            UNIT_ASSERT_DOUBLES_EQUAL(possiblePositions[i].GetProbability(), 0.5, 1e-3);
            UNIT_ASSERT_DOUBLES_EQUAL(possiblePositions[i].GetPosition(), 1.0, 1e-3);
        }
    }

    Y_UNIT_TEST(vanga_test_2) {
        TVector<TPossiblePositionOnEdge> possiblePositions;
        TTestPredictActions testPredictActions(possiblePositions);
        TPredictSearchActions predictActions(Graph, {0_eid, 1.0}, Index, *ProbabilityTable, 31, testPredictActions);
        TDijkstraSearcher searcher(Graph, predictActions);
        searcher.Search(0_eid);
        UNIT_ASSERT_EQUAL(possiblePositions.size(), 1);
        UNIT_ASSERT_DOUBLES_EQUAL(possiblePositions[0].GetProbability(), 1.0, 1e-3);
        UNIT_ASSERT_EQUAL(possiblePositions[0].GetEdgeId(), 5_eid);
    }
}
