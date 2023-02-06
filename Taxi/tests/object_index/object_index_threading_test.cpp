#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>
#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/object_index/object_index_threading.h>

#include <algorithm>
#include <random>

using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TYardId;
using NTaxi::NGraph2::TObjectIndexThreading;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;
using NTaxi::NGraph2::TPositionOnEdge;
using NTaxi::NGraph2::TYardIndex;
using NTaxi::NGraph2::TYardObjectsAtomicCounter;
using NTaxi::NGraph2::TGraphTestData;
using NTaxi::NGraph2::TEmptyThreadingSettings;
using NTaxi::NGraph2::TBaseThreadingSettings;

using namespace NTaxi::NGraph2Literals;

namespace NTaxi::NGraph2 {
  struct TObjectIndexThreadingTester {
    template<typename T>
    static void CheckConsistency(const T& index) {
      std::unordered_set<typename T::TKey, typename T::THash> keysFound;
      TYardObjectsAtomicCounter yardsVerification(index.Graph.get());
      for (auto& bucket: index.EdgeIndex.Buckets) {
        for(const auto& edgeObjs : bucket.GetMap()) {
          for (const auto& obj: edgeObjs.second) {
            const auto& key = obj.first;
            const double edgePos = obj.second;
            const auto edgeId = edgeObjs.first;
            Y_VERIFY(keysFound.insert(key).second); // insert and check that key was not present simultaneously
            // check that key is present in ObjectIndex
            auto& objectIndexBucket = index.ObjectIndex.GetBucketForKey(key);
            auto objectIndexIt = objectIndexBucket.GetMap().find(key);
            Y_VERIFY(objectIndexIt != objectIndexBucket.GetMap().end());

            // And positions should be the same
            Y_VERIFY(objectIndexIt->second == TPositionOnEdge(edgeId, edgePos));

            // add to verification yard
            const auto& yardId = index.Graph.get().GetYardId(edgeId);
            if (yardId != TYardIndex::UNDEFINED_YARD) {
                yardsVerification.AddToYard(yardId);
            }
          }
        }
      }

      // Size of ObjectIndex and EdgeIndex should match
      size_t sizeObjectIndex = 0;
      for (auto& bucket: index.ObjectIndex.Buckets)
          sizeObjectIndex += bucket.GetMap().size();
      size_t sizeEdgeIndex = 0;
      for (auto& bucket: index.EdgeIndex.Buckets)
        for (auto& obj: bucket.GetMap())
          sizeEdgeIndex += obj.second.size();
      //Y_VERIFY(index.ObjectIndex.size() == index.EdgeIndex.size());
      Y_VERIFY(sizeObjectIndex == sizeEdgeIndex);

      // Yards must be equal
      Y_VERIFY(index.YardObjectsCounter == yardsVerification);
    }
  };
}

using NTaxi::NGraph2::TObjectIndexThreadingTester;

template <typename T>
struct TObjectIndexThreadingNoCopy: public TObjectIndexThreading<T> {
    using TObjectIndexThreading<T>::TObjectIndexThreading;

    TObjectIndexThreadingNoCopy(const TObjectIndexThreadingNoCopy&) = delete;
    TObjectIndexThreadingNoCopy& operator=(const TObjectIndexThreadingNoCopy&) = delete;
    TObjectIndexThreadingNoCopy(TObjectIndexThreadingNoCopy&&) = default;
    TObjectIndexThreadingNoCopy& operator=(TObjectIndexThreadingNoCopy&&) = default;
};

namespace {
    template <typename T, typename A>
    IOutputStream& operator<<(IOutputStream& str, const TVector<T, A>& xs) {
        str << "[";
        for (const auto& x : xs)
            str << x << ", ";
        str << "]";
        return str;
    }
#define TEST_DEBUG(x) \
    { Cerr << #x << ": " << x << "\n"; }
}

Y_UNIT_TEST_SUITE(object_index_threading_test) {
    Y_UNIT_TEST(TestAddOne) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);
        TId edge_id1 = 2_eid;
        TId edge_id2 = 3_eid;
        const auto& uuid = 1ull;

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);

        objectIndex.Insert(uuid, TPositionOnEdge{edge_id1, 0.5});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // check that object is added correctly
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 1ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 1ull);

        const auto& pos = objectIndex.GetPosition(uuid);
        UNIT_ASSERT_EQUAL(pos.GetEdgeId(), edge_id1);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.GetPosition(), 0.5, 1e-2);

        auto positions = objectIndex.GetObjectsOnEdge(edge_id1);
        UNIT_ASSERT_EQUAL(positions.size(), 1ull);
        const auto& pos_on_edge = positions.at(uuid);
        UNIT_ASSERT_EQUAL(pos_on_edge.GetEdgeId(), edge_id1);
        UNIT_ASSERT_DOUBLES_EQUAL(pos_on_edge.GetPosition(), 0.5, 1e-2);

        // Add this object to another edge
        objectIndex.Insert(uuid, TPositionOnEdge{edge_id2, 0.5});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);
        Cerr << "EdgeNum: " << objectIndex.GetEdgeNum() << Endl;
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 1ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 1ull);

        // check that object is added correctly
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 1ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 1ull);

        const auto& pos2 = objectIndex.GetPosition(uuid);
        UNIT_ASSERT_EQUAL(pos2.GetEdgeId(), edge_id2);
        UNIT_ASSERT_DOUBLES_EQUAL(pos2.GetPosition(), 0.5, 1e-2);

        auto positions2 = objectIndex.GetObjectsOnEdge(edge_id2);
        UNIT_ASSERT_EQUAL(positions2.size(), 1ull);
        const auto& pos_on_edge2 = positions2.at(uuid);
        UNIT_ASSERT_EQUAL(pos_on_edge2.GetEdgeId(), edge_id2);
        UNIT_ASSERT_DOUBLES_EQUAL(pos_on_edge2.GetPosition(), 0.5, 1e-2);
    }

    Y_UNIT_TEST(TestAddReplace) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);
        TId edge_id1 = 2_eid;
        TId edge_id2 = 3_eid;
        const auto& uuid = 1ull;

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);

        objectIndex.Insert(uuid, TPositionOnEdge{edge_id1, 0.5});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // check that object is added correctly
        {
            UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 1ull);
            UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 1ull);

            const auto& pos = objectIndex.GetPosition(uuid);
            UNIT_ASSERT_EQUAL(pos.GetEdgeId(), edge_id1);
            UNIT_ASSERT_DOUBLES_EQUAL(pos.GetPosition(), 0.5, 1e-2);

            auto positions = objectIndex.GetObjectsOnEdge(edge_id1);
            UNIT_ASSERT_EQUAL(positions.size(), 1ull);
            const auto& pos_on_edge = positions.at(uuid);
            UNIT_ASSERT_EQUAL(pos_on_edge.GetEdgeId(), edge_id1);
            UNIT_ASSERT_DOUBLES_EQUAL(pos_on_edge.GetPosition(), 0.5, 1e-2);
        }

        // Add the same object to new edge
        objectIndex.Insert(uuid, TPositionOnEdge{edge_id2, 0.5});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // Check that it is no longer present on previous edge
        {
            UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 1ull);
            UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 1ull);

            const auto& pos = objectIndex.GetPosition(uuid);
            UNIT_ASSERT_EQUAL(pos.GetEdgeId(), edge_id2);
            UNIT_ASSERT_DOUBLES_EQUAL(pos.GetPosition(), 0.5, 1e-2);

            auto positions = objectIndex.GetObjectsOnEdge(edge_id1);
            UNIT_ASSERT_EQUAL(positions.size(), 0ull);

            auto positions2 = objectIndex.GetObjectsOnEdge(edge_id2);
            UNIT_ASSERT_EQUAL(positions2.size(), 1ull);
        }
    }

    Y_UNIT_TEST(TestAddTwoSameEdge) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);
        TId edge_id = 2_eid;
        double position_on_edge1 = 0.5;
        double position_on_edge2 = 0.1;
        const auto& uuid1 = 1ull;
        const auto& uuid2 = 2ull;

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);

        objectIndex.Insert(uuid1, TPositionOnEdge{edge_id, position_on_edge1});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);
        objectIndex.Insert(uuid2, TPositionOnEdge{edge_id, position_on_edge2});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // check that object is added correctly
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 1ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 2ull);

        const auto& pos1 = objectIndex.GetPosition(uuid1);
        UNIT_ASSERT_EQUAL(pos1.GetEdgeId(), edge_id);
        UNIT_ASSERT_DOUBLES_EQUAL(pos1.GetPosition(), position_on_edge1, 1e-2);

        const auto& pos2 = objectIndex.GetPosition(uuid2);
        UNIT_ASSERT_EQUAL(pos2.GetEdgeId(), edge_id);
        UNIT_ASSERT_DOUBLES_EQUAL(pos2.GetPosition(), position_on_edge2, 1e-2);

        auto positions = objectIndex.GetObjectsOnEdge(edge_id);
        UNIT_ASSERT_EQUAL(positions.size(), 2ull);
        const auto& pos_on_edge1 = positions.at(uuid1);
        UNIT_ASSERT_EQUAL(pos_on_edge1.GetEdgeId(), edge_id);
        UNIT_ASSERT_DOUBLES_EQUAL(pos_on_edge1.GetPosition(), position_on_edge1, 1e-2);

        const auto& pos_on_edge2 = positions.at(uuid2);
        UNIT_ASSERT_EQUAL(pos_on_edge2.GetEdgeId(), edge_id);
        UNIT_ASSERT_DOUBLES_EQUAL(pos_on_edge2.GetPosition(), position_on_edge2, 1e-2);
    }

    Y_UNIT_TEST(TestAddTwo) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);
        TId edge_id1 = 2_eid;
        TId edge_id2 = 3_eid;
        double position_on_edge1 = 0.5;
        double position_on_edge2 = 0.1;
        const auto& uuid1 = 1ull;
        const auto& uuid2 = 2ull;

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);

        objectIndex.Insert(uuid1, TPositionOnEdge{edge_id1, position_on_edge1});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);
        objectIndex.Insert(uuid2, TPositionOnEdge{edge_id2, position_on_edge2});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // check that object is added correctly
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 2ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 2ull);

        const auto& pos1 = objectIndex.GetPosition(uuid1);
        UNIT_ASSERT_EQUAL(pos1.GetEdgeId(), edge_id1);
        UNIT_ASSERT_DOUBLES_EQUAL(pos1.GetPosition(), position_on_edge1, 1e-2);

        auto positions1 = objectIndex.GetObjectsOnEdge(edge_id1);
        UNIT_ASSERT_EQUAL(positions1.size(), 1ull);
        const auto& pos_on_edge1 = positions1.at(uuid1);
        UNIT_ASSERT_EQUAL(pos_on_edge1.GetEdgeId(), edge_id1);
        UNIT_ASSERT_DOUBLES_EQUAL(pos_on_edge1.GetPosition(), position_on_edge1, 1e-2);

        const auto& pos2 = objectIndex.GetPosition(uuid2);
        UNIT_ASSERT_EQUAL(pos2.GetEdgeId(), edge_id2);
        UNIT_ASSERT_DOUBLES_EQUAL(pos2.GetPosition(), position_on_edge2, 1e-2);

        auto positions2 = objectIndex.GetObjectsOnEdge(edge_id2);
        UNIT_ASSERT_EQUAL(positions2.size(), 1ull);
        const auto& pos_on_edge2 = positions2.at(uuid2);
        UNIT_ASSERT_EQUAL(pos_on_edge2.GetEdgeId(), edge_id2);
        UNIT_ASSERT_DOUBLES_EQUAL(pos_on_edge2.GetPosition(), position_on_edge2, 1e-2);
    }

    Y_UNIT_TEST(TestRemove) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);
        TId edge_id1 = 2_eid;
        TId edge_id2 = 3_eid;
        double position_on_edge1 = 0.5;
        double position_on_edge2 = 0.1;
        const auto& uuid1 = 1ull;
        const auto& uuid2 = 2ull;

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);

        objectIndex.Insert(uuid1, TPositionOnEdge{edge_id1, position_on_edge1});
        objectIndex.Insert(uuid2, TPositionOnEdge{edge_id2, position_on_edge2});
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 2ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 2ull);
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // Test removal of non-existent object
        objectIndex.Remove(5ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 2ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 2ull);
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // Test object removal
        objectIndex.Remove(uuid1);
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // check that object is removed
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 1ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 1ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetPosition(uuid1).GetEdgeId(), NTaxi::NGraph2::UNDEFINED);

        objectIndex.Remove(uuid2);
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // check that object is removed
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);
    }

    Y_UNIT_TEST(TestAddFromTPoint) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);
        const TId exp_edge_id = 54319_eid;
        const double exp_position_on_edge = 0.2625766457;
        const auto& uuid = 1ull;

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);

        UNIT_ASSERT(objectIndex.Insert(uuid, TPoint{37.676062, 55.748181}));
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // check that object is added correctly
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 1ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 1ull);

        const auto& pos = objectIndex.GetPosition(uuid);
        UNIT_ASSERT_EQUAL(pos.GetEdgeId(), exp_edge_id);
        UNIT_ASSERT_DOUBLES_EQUAL(pos.GetPosition(), exp_position_on_edge, 1e-6);
    }

    Y_UNIT_TEST(TestFailToAddFromTPoint) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);
        const auto& uuid = 1ull;
        const auto distance = 1.0; // just one meter for failing to find nearest edge

        UNIT_ASSERT(!objectIndex.Insert(uuid, TPoint{37.676062, 55.748181}, distance));

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);
    }

    Y_UNIT_TEST(TestCopy) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);

        TPositionOnEdge positionOnEdge{3_eid, 1.0};

        objectIndex.Insert(1ull, TPositionOnEdge{3_eid, 0.5});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        TObjectIndexThreading<ui64> objectIndexCopy(objectIndex);
        TObjectIndexThreadingTester::CheckConsistency(objectIndexCopy);
        UNIT_ASSERT_EQUAL(positionOnEdge.GetEdgeId(), objectIndexCopy.GetPosition(1ull).GetEdgeId());
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), objectIndexCopy.GetEdgeNum());
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), objectIndexCopy.GetObjectNum());
    }

    Y_UNIT_TEST(TestAssign) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);

        TPositionOnEdge positionOnEdge{3_eid, 1.0};

        objectIndex.Insert(1ull, TPositionOnEdge{3_eid, 0.5});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        TObjectIndexThreading<ui64> objectIndexCopy(graph);
        objectIndexCopy = objectIndex;
        TObjectIndexThreadingTester::CheckConsistency(objectIndexCopy);
        UNIT_ASSERT_EQUAL(positionOnEdge.GetEdgeId(), objectIndexCopy.GetPosition(1ull).GetEdgeId());
        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), objectIndexCopy.GetEdgeNum());
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), objectIndexCopy.GetObjectNum());
    }

    Y_UNIT_TEST(TestCopyMove) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreadingNoCopy<ui64> objectIndex(graph);
        static_assert(std::is_move_constructible_v<TObjectIndexThreadingNoCopy<ui64>>);

        TPositionOnEdge positionOnEdge{3_eid, 1.0};

        objectIndex.Insert(1ull, TPositionOnEdge{3_eid, 0.5});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        TObjectIndexThreadingNoCopy<ui64> objectIndexCopy(std::move(objectIndex));
        TObjectIndexThreadingTester::CheckConsistency(objectIndexCopy);
        UNIT_ASSERT_EQUAL(positionOnEdge.GetEdgeId(), objectIndexCopy.GetPosition(1ull).GetEdgeId());
        UNIT_ASSERT_EQUAL(objectIndexCopy.GetEdgeNum(), 1);
        UNIT_ASSERT_EQUAL(objectIndexCopy.GetObjectNum(), 1);
    }

    Y_UNIT_TEST(TestAssignMove) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);
        static_assert(std::is_move_assignable_v<TObjectIndexThreading<ui64>>);

        TPositionOnEdge positionOnEdge{3_eid, 1.0};

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0);
        objectIndex.Insert(1ull, TPositionOnEdge{3_eid, 0.5});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        TObjectIndexThreading<ui64> objectIndexCopy(graph);
        objectIndexCopy = std::move(objectIndex);
        TObjectIndexThreadingTester::CheckConsistency(objectIndexCopy);
        UNIT_ASSERT_EQUAL(positionOnEdge.GetEdgeId(), objectIndexCopy.GetPosition(1ull).GetEdgeId());
    }

    Y_UNIT_TEST(TestReserve) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64> objectIndex(graph);
        objectIndex.Reserve(20);
    }

    namespace {
        TPositionOnEdge MakePoe(ui32 eid, double pos_on_edge) {
            return TPositionOnEdge{static_cast<TId>(eid), pos_on_edge};
        }

        template <typename T>
        TVector<size_t> GetObjectCountInEachYard(const TObjectIndexThreading<T>& index, const TGraph& graph) {
            TVector<size_t> ret;

            const auto yard_count = graph.GetYardsCount();
            for (size_t i = 0; i < yard_count; ++i) {
                const auto yard_id = static_cast<NTaxi::NGraph2::TYardId>(i);
                ret.push_back(index.GetObjectsCountInYard(yard_id));
            }

            return ret;
        }
    }
    Y_UNIT_TEST(TestYards) {
        ::NTaxi::NGraph2::TGraphTestData test_data;
        const auto& graph = test_data.CreateRhombusGraphWithPasses();

        TObjectIndexThreading<ui64> objectIndex(graph);
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);
        const auto edges_count = graph.EdgesCount();

        // place object on each edge
        for (ui32 i = 0; i < edges_count; ++i) {
            const auto uuid = i * 1000;
            objectIndex.Insert(uuid, MakePoe(i, 0.5));
        }
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        const auto yard_count = graph.GetYardsCount();
        UNIT_ASSERT_EQUAL(2u, yard_count);

        {
            const auto objects_in_yards = GetObjectCountInEachYard(objectIndex, graph);
            const TVector<size_t> expected = {2, 2};
            TEST_DEBUG(objects_in_yards);
            TEST_DEBUG(expected);
            UNIT_ASSERT_EQUAL(expected, objects_in_yards);
        }

        objectIndex.Remove(2000);
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);
        {
            const auto objects_in_yards = GetObjectCountInEachYard(objectIndex, graph);
            const TVector<size_t> expected = {1, 2};
            TEST_DEBUG(objects_in_yards);
            TEST_DEBUG(expected);
            UNIT_ASSERT_EQUAL(expected, objects_in_yards);
        }

        objectIndex.Clear();
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);
        {
            const auto objects_in_yards = GetObjectCountInEachYard(objectIndex, graph);
            const TVector<size_t> expected = {0, 0};
            TEST_DEBUG(objects_in_yards);
            TEST_DEBUG(expected);
            UNIT_ASSERT_EQUAL(expected, objects_in_yards);
        }
    }

    Y_UNIT_TEST(TestMergeAddDifferentKeys) {
        /// Merge two indices with no same keys
        const auto& graph = TGraphTestData{}.CreateRhombusGraphWithPasses();
        TId edge_id1 = 2_eid;
        TId edge_id2 = 3_eid;
        const auto& uuid1 = 1ull;
        const auto& uuid2 = 2ull;

        TObjectIndexThreading<ui64> objectIndex(graph);

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);

        objectIndex.Insert(uuid1, TPositionOnEdge{edge_id1, 0.5});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // Different edges
        {
          auto base{objectIndex};
          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid2, TPositionOnEdge{edge_id2, 0.5});

          base.Merge(std::move(addition));
          // Now, index must contain both keys
          Cerr << "Edge num: " << base.GetEdgeNum() << Endl;
          UNIT_ASSERT_EQUAL(base.GetEdgeNum(), 2ull);
          UNIT_ASSERT_EQUAL(base.GetObjectNum(), 2ull);

          const auto& pos1 = base.GetPosition(uuid1);
          UNIT_ASSERT_EQUAL(pos1.GetEdgeId(), edge_id1);
          UNIT_ASSERT_DOUBLES_EQUAL(pos1.GetPosition(), 0.5, 1e-2);

          const auto& pos2 = base.GetPosition(uuid2);
          UNIT_ASSERT_EQUAL(pos2.GetEdgeId(), edge_id2);
          UNIT_ASSERT_DOUBLES_EQUAL(pos2.GetPosition(), 0.5, 1e-2);
        }

        // Same edge
        {
          auto base{objectIndex};
          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid2, TPositionOnEdge{edge_id1, 0.2});

          base.Merge(std::move(addition));
          // Now, index must contain both keys, both keys are on same edge
          UNIT_ASSERT_EQUAL(base.GetEdgeNum(), 1ull);
          UNIT_ASSERT_EQUAL(base.GetObjectNum(), 2ull);

          const auto& pos1 = base.GetPosition(uuid1);
          UNIT_ASSERT_EQUAL(pos1.GetEdgeId(), edge_id1);
          UNIT_ASSERT_DOUBLES_EQUAL(pos1.GetPosition(), 0.5, 1e-2);

          const auto& pos2 = base.GetPosition(uuid2);
          UNIT_ASSERT_EQUAL(pos2.GetEdgeId(), edge_id1);
          UNIT_ASSERT_DOUBLES_EQUAL(pos2.GetPosition(), 0.2, 1e-2);
        }
    }

    Y_UNIT_TEST(TestMergeAddSameKeys) {
        /// Merge two indices that share one key
        const auto& graph = TGraphTestData{}.CreateRhombusGraphWithPasses();
        TId edge_id1 = 2_eid;
        TId edge_id2 = 3_eid;
        TId edge_id3 = 5_eid;
        const auto& uuid1 = 1ull;
        const auto& uuid2 = 2ull;
        const auto& uuid3 = 3ull;

        TObjectIndexThreading<ui64> objectIndex(graph);

        objectIndex.Insert(uuid1, TPositionOnEdge{edge_id1, 0.5});
        objectIndex.Insert(uuid2, TPositionOnEdge{edge_id2, 0.2});
        TObjectIndexThreadingTester::CheckConsistency(objectIndex);

        // Different edges
        // base index has uuid1 on edge 1 and uui2 on edge 2
        // addition has uuid2 on edge 3 and uuid3 on edge 3
        //
        // result should have uuid1 on edge 1, uuid2 on edge 3, uuid3 on edge 3
        {
          auto base{objectIndex};
          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid2, TPositionOnEdge{edge_id3, 0.7});
          addition.Insert(uuid3, TPositionOnEdge{edge_id3, 0.1});

          base.Merge(std::move(addition));
          // Now, index must contain all keys
          Cerr << base.GetEdgeNum() << Endl;
          // UNIT_ASSERT_EQUAL(base.GetEdgeNum(), 3ull); TODO: RESTORE
          UNIT_ASSERT_EQUAL(base.GetObjectNum(), 3ull);

          const auto& pos1 = base.GetPosition(uuid1);
          UNIT_ASSERT_EQUAL(pos1.GetEdgeId(), edge_id1);
          UNIT_ASSERT_DOUBLES_EQUAL(pos1.GetPosition(), 0.5, 1e-2);

          const auto& pos2 = base.GetPosition(uuid2);
          UNIT_ASSERT_EQUAL(pos2.GetEdgeId(), edge_id3);
          UNIT_ASSERT_DOUBLES_EQUAL(pos2.GetPosition(), 0.7, 1e-2);

          const auto& pos3 = base.GetPosition(uuid3);
          UNIT_ASSERT_EQUAL(pos3.GetEdgeId(), edge_id3);
          UNIT_ASSERT_DOUBLES_EQUAL(pos3.GetPosition(), 0.1, 1e-3);
        }

        // Same edge
        // base index has uuid1 and uui2 on edge 2
        // addition has uuid2 on edge 2 and uuid3
        //
        // result should have uuid1, uuid2 on edge 2, uuid3
        {
          auto base{objectIndex};
          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid2, TPositionOnEdge{edge_id2, 0.7});
          addition.Insert(uuid3, TPositionOnEdge{edge_id3, 0.1});

          base.Merge(std::move(addition));
          // Now, index must contain all keys
          UNIT_ASSERT_EQUAL(base.GetEdgeNum(), 3ull);
          UNIT_ASSERT_EQUAL(base.GetObjectNum(), 3ull);

          const auto& pos1 = base.GetPosition(uuid1);
          UNIT_ASSERT_EQUAL(pos1.GetEdgeId(), edge_id1);
          UNIT_ASSERT_DOUBLES_EQUAL(pos1.GetPosition(), 0.5, 1e-2);

          const auto& pos2 = base.GetPosition(uuid2);
          UNIT_ASSERT_EQUAL(pos2.GetEdgeId(), edge_id2);
          UNIT_ASSERT_DOUBLES_EQUAL(pos2.GetPosition(), 0.7, 1e-2);

          const auto& pos3 = base.GetPosition(uuid3);
          UNIT_ASSERT_EQUAL(pos3.GetEdgeId(), edge_id3);
          UNIT_ASSERT_DOUBLES_EQUAL(pos3.GetPosition(), 0.1, 1e-3);
        }
    }

    Y_UNIT_TEST(TestMergeAddDifferentKeysYards) {
        /// Merge two indices with no same keys
        const auto& graph = TGraphTestData{}.CreateRhombusGraphWithComplexPasses();
        TId edge_id1 = 2_eid; // pass
        TId edge_id2 = 3_eid; // no pass
        TId edge_id3 = 5_eid; // pass
        TYardId edge_id1_yard = graph.GetYardId(edge_id1);
        TYardId edge_id3_yard = graph.GetYardId(edge_id3);
        UNIT_ASSERT_UNEQUAL(TYardIndex::UNDEFINED_YARD, edge_id1_yard);
        UNIT_ASSERT_UNEQUAL(TYardIndex::UNDEFINED_YARD, edge_id3_yard);

        const auto& uuid1 = 1ull;
        const auto& uuid2 = 2ull;


        // Different edges, base has no pass, add pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id2, 0.5});
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id1_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid2, TPositionOnEdge{edge_id1, 0.5});

          base.Merge(std::move(addition));
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));
        }
        // Different edges, base has pass, add without pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id1, 0.5});
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid2, TPositionOnEdge{edge_id2, 0.5});

          base.Merge(std::move(addition));
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));
        }
        // Different edges, base has pass, add another pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id1, 0.5});
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id3_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid2, TPositionOnEdge{edge_id3, 0.5});

          base.Merge(std::move(addition));
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id3_yard));
        }

        // Same edge, with pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id1, 0.5});
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid2, TPositionOnEdge{edge_id1, 0.2});

          base.Merge(std::move(addition));

          // Now, both keys are in the yard
          UNIT_ASSERT_EQUAL(2, base.GetObjectsCountInYard(edge_id1_yard));
        }
        // Same edge, without pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id2, 0.5});
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id1_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid2, TPositionOnEdge{edge_id2, 0.2});

          base.Merge(std::move(addition));

          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id1_yard));
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id3_yard));
        }
    }
    Y_UNIT_TEST(TestMergeAddSameKeysYards) {
        /// Merge two indices with same keys
        const auto& graph = TGraphTestData{}.CreateRhombusGraphWithComplexPasses();
        TId edge_id1 = 2_eid; // pass
        TId edge_id2 = 3_eid; // no pass
        TId edge_id3 = 5_eid; // pass
        TYardId edge_id1_yard = graph.GetYardId(edge_id1);
        TYardId edge_id3_yard = graph.GetYardId(edge_id3);
        UNIT_ASSERT_UNEQUAL(TYardIndex::UNDEFINED_YARD, edge_id1_yard);
        UNIT_ASSERT_UNEQUAL(TYardIndex::UNDEFINED_YARD, edge_id3_yard);

        const auto& uuid1 = 1ull;

        // Different edges, base has no pass, add pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id2, 0.5});
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id1_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid1, TPositionOnEdge{edge_id1, 0.5});

          base.Merge(std::move(addition));
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));
        }
        // Different edges, base has pass, add without pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id1, 0.5});
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid1, TPositionOnEdge{edge_id2, 0.5});

          base.Merge(std::move(addition));
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id1_yard));
        }
        // Different edges, base has pass, add another pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id1, 0.5});
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id3_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid1, TPositionOnEdge{edge_id3, 0.5});

          base.Merge(std::move(addition));
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id1_yard));
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id3_yard));
        }

        // Same edge, with pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id1, 0.5});
          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid1, TPositionOnEdge{edge_id1, 0.2});

          base.Merge(std::move(addition));

          UNIT_ASSERT_EQUAL(1, base.GetObjectsCountInYard(edge_id1_yard));
        }
        // Same edge, without pass
        {
          TObjectIndexThreading<ui64> base(graph);
          base.Insert(uuid1, TPositionOnEdge{edge_id2, 0.5});
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id1_yard));

          TObjectIndexThreading<ui64> addition(graph);
          addition.Insert(uuid1, TPositionOnEdge{edge_id2, 0.2});

          base.Merge(std::move(addition));

          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id1_yard));
          UNIT_ASSERT_EQUAL(0, base.GetObjectsCountInYard(edge_id3_yard));
        }
    }
    Y_UNIT_TEST(TestThreadingInsertion) {
        const auto& graph = TGraphTestData{}.GetTestGraph();
        TObjectIndexThreading<ui64, TBaseThreadingSettings> objectIndex(graph);

        size_t number_of_object_on_edge = 10;
        std::vector<TId> eids2(number_of_object_on_edge, 2_eid);
        std::vector<TId> eids3(number_of_object_on_edge, 3_eid);
        std::vector<TId> edges;
        edges.insert(edges.end(), eids2.begin(), eids2.end());
        edges.insert(edges.end(), eids3.begin(), eids3.end());
        std::vector<std::pair<ui64, TPositionOnEdge>> uuidAndPos;

        for (size_t i = 0; i < edges.size(); i++) {
            uuidAndPos.push_back(std::make_pair(i + 1, TPositionOnEdge{edges[i], 0.5}));
        }

        auto rng = std::default_random_engine {};
        std::shuffle(uuidAndPos.begin(), uuidAndPos.end(), rng);

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 0ull);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), 0ull);

        size_t threadsCount = 2;
        std::vector<std::thread> threads;
        threads.reserve(threadsCount);

        auto insertPositions = [&] (size_t beginPos, size_t endPos) {
            for (size_t i = beginPos; i < endPos; ++i) {
                objectIndex.Insert(uuidAndPos[i].first, uuidAndPos[i].second);
            }
        };

        const size_t positionsPerThread = uuidAndPos.size() / threadsCount;

        size_t begin = 0;
        if (positionsPerThread) {
            for (size_t i = 0; i < threadsCount - 1; ++i) {
                threads.emplace_back(insertPositions, begin, begin + positionsPerThread);
                begin += positionsPerThread;
            }
        }

        const size_t end = std::min(begin + positionsPerThread, uuidAndPos.size());
        threads.emplace_back(insertPositions, begin, end);

        for (auto& thread : threads) {
            thread.join();
        }

        TObjectIndexThreadingTester::CheckConsistency<TObjectIndexThreading<ui64, TBaseThreadingSettings>>(objectIndex);

        UNIT_ASSERT_EQUAL(objectIndex.GetEdgeNum(), 2);
        UNIT_ASSERT_EQUAL(objectIndex.GetObjectNum(), number_of_object_on_edge * 2);

        auto positions2 = objectIndex.GetObjectsOnEdge(2_eid);
        UNIT_ASSERT_EQUAL(positions2.size(), 10ull);

        auto positions3 = objectIndex.GetObjectsOnEdge(3_eid);
        UNIT_ASSERT_EQUAL(positions3.size(), 10ull);

        auto positions4 = objectIndex.GetObjectsOnEdge(4_eid);
        UNIT_ASSERT_EQUAL(positions4.size(), 0ull);

        TObjectIndexThreadingTester::CheckConsistency<TObjectIndexThreading<ui64, TBaseThreadingSettings>>(objectIndex);
    }

}
