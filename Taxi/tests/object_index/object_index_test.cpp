#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/taxi/graph2/object_index.h>
#include <yandex/taxi/graph2/graph.h>

using NTaxiExternal::NGraph2::TEdgeData;
using NTaxiExternal::NGraph2::TPositionOnEdge;
using NTaxiExternal::NGraph2::TGraph;
using NTaxiExternal::NGraph2::TRoadGraphFileLoader;
using NTaxiExternal::NGraph2::TObjectIndex;
using NTaxiExternal::NGraph2::TId;
using NTaxiExternal::NGraph2::TPoint;
using NTaxiExternal::NGraph2::TPolyline;

namespace {
    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }

    const TGraph& GetTestGraph() {
        static TGraph graph(TRoadGraphFileLoader::Create(
            GraphPath("road_graph.fb").c_str(),
            GraphPath("rtree.fb").c_str()));
        return graph;
    }
}

Y_UNIT_TEST_SUITE(external_object_index_test) {
    Y_UNIT_TEST(TestAddAndRemove) {
          const auto& graph = GetTestGraph();
          ::NTaxiExternal::NGraph2::TObjectIndex obj_index(graph);
          TId edge_id1 = 2u;
          TId edge_id2 = 3u;
          double position_on_edge1 = 0.5;
          double position_on_edge2 = 0.1;
          const auto& uuid1 = 1ull;
          const auto& uuid2 = 2ull;

          obj_index.Insert(uuid1, TPositionOnEdge{edge_id1, position_on_edge1});
          obj_index.Insert(uuid2, TPositionOnEdge{edge_id2, position_on_edge2});
          UNIT_ASSERT_EQUAL(2, obj_index.GetObjectNum());

          const auto& pos1 = obj_index.GetPosition(uuid1);
          UNIT_ASSERT_EQUAL(pos1.EdgeId, edge_id1);
          UNIT_ASSERT_DOUBLES_EQUAL(pos1.Position, position_on_edge1, 1e-2);

          auto positions1 = obj_index.GetObjectsOnEdge(edge_id1);
          UNIT_ASSERT_EQUAL(positions1.Size(), 1ull);
          const auto& pos_on_edge1 = positions1[0];
          UNIT_ASSERT_EQUAL(pos_on_edge1.Uuid, uuid1);
          UNIT_ASSERT_EQUAL(pos_on_edge1.Position.EdgeId, edge_id1);
          UNIT_ASSERT_DOUBLES_EQUAL(pos_on_edge1.Position.Position, position_on_edge1, 1e-2);

          const auto& pos2 = obj_index.GetPosition(uuid2);
          UNIT_ASSERT_EQUAL(pos2.EdgeId, edge_id2);
          UNIT_ASSERT_DOUBLES_EQUAL(pos2.Position, position_on_edge2, 1e-2);

          auto positions2 = obj_index.GetObjectsOnEdge(edge_id2);
          UNIT_ASSERT_EQUAL(positions2.Size(), 1ull);
          const auto& pos_on_edge2 = positions2[0];
          UNIT_ASSERT_EQUAL(pos_on_edge2.Uuid, uuid2);
          UNIT_ASSERT_EQUAL(pos_on_edge2.Position.EdgeId, edge_id2);
          UNIT_ASSERT_DOUBLES_EQUAL(pos_on_edge2.Position.Position, position_on_edge2, 1e-2);

          // remove uuid2 and check that it is deleted.
          obj_index.Remove(uuid2);

          const auto& pos3 = obj_index.GetPosition(uuid2);
          auto positions3 = obj_index.GetObjectsOnEdge(edge_id2);
          UNIT_ASSERT(pos3.IsUndefined());
          UNIT_ASSERT_EQUAL(positions3.Size(), 0ull);
    }

    Y_UNIT_TEST(TestAddFromTPoint) {
        const auto &graph = GetTestGraph();
        ::NTaxiExternal::NGraph2::TObjectIndex obj_index(graph);
        const TId exp_edge_id = 54319u;
        const double exp_position_on_edge = 0.2625766457;
        const auto& uuid = 1ull;

        UNIT_ASSERT(obj_index.Insert(uuid, TPoint{37.676062, 55.748181}));

        const auto& pos = obj_index.GetPosition(uuid);
        UNIT_ASSERT_EQUAL(pos.EdgeId, exp_edge_id);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.Position, exp_position_on_edge, 1e-6);
    }

    Y_UNIT_TEST(TestCopy) {
          const auto& graph = GetTestGraph();
          ::NTaxiExternal::NGraph2::TObjectIndex obj_index(graph);
          TId edge_id1 = 2u;
          TId edge_id2 = 3u;
          double position_on_edge1 = 0.5;
          double position_on_edge2 = 0.1;
          const auto& uuid1 = 1ull;
          const auto& uuid2 = 2ull;

          obj_index.Insert(uuid1, TPositionOnEdge{edge_id1, position_on_edge1});

          {
              const auto& pos1 = obj_index.GetPosition(uuid1);
              UNIT_ASSERT_EQUAL(pos1.EdgeId, edge_id1);
              UNIT_ASSERT_DOUBLES_EQUAL(pos1.Position, position_on_edge1, 1e-2);
          }

          // Copy index
          {
              // Copy should have same data
              ::NTaxiExternal::NGraph2::TObjectIndex copy_index(obj_index);
              const auto& pos1 = copy_index.GetPosition(uuid1);
              UNIT_ASSERT_EQUAL(pos1.EdgeId, edge_id1);
              UNIT_ASSERT_DOUBLES_EQUAL(pos1.Position, position_on_edge1, 1e-2);
          }

          {
              // Modifying copy should not interfere with original
              ::NTaxiExternal::NGraph2::TObjectIndex copy_index(obj_index);
              copy_index.Insert(uuid2, TPositionOnEdge{edge_id2, position_on_edge2});

              const auto& pos2 = copy_index.GetPosition(uuid2);
              UNIT_ASSERT_EQUAL(pos2.EdgeId, edge_id2);
              UNIT_ASSERT_DOUBLES_EQUAL(pos2.Position, position_on_edge2, 1e-2);

              UNIT_ASSERT(obj_index.GetPosition(uuid2).IsUndefined());
          }
    }
}
