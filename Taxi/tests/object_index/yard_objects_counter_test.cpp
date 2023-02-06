#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph-test/graph_test_data.h>
#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/object_index/object_index.h>

using NTaxi::NGraph2::TEdgeData;
using NTaxi::NGraph2::TGraph;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TYardId;
using NTaxi::NGraph2::TYardIndex;
using NTaxi::NGraph2::TYardObjectsCounter;
using NTaxi::NGraph2::TObjectIndex;
using NTaxi::NGraph2::TPoint;
using NTaxi::NGraph2::TPolyline;
using NTaxi::NGraph2::TPositionOnEdge;

using namespace NTaxi::NGraph2Literals;

namespace {
      template <typename T>
      TVector<size_t> GetObjectCountInEachYard(const TObjectIndex<T>& index, const TGraph& graph) {
          TVector<size_t> ret;

          const auto yard_count = graph.GetYardsCount();
          for (size_t i = 0; i < yard_count; ++i) {
              const auto yard_id = static_cast<NTaxi::NGraph2::TYardId>(i);
              ret.push_back(index.GetObjectsCountInYard(yard_id));
          }

          return ret;
      }
}

Y_UNIT_TEST_SUITE(yard_objects_counter_test) {

    Y_UNIT_TEST(TestYards) {
        ::NTaxi::NGraph2::TGraphTestData test_data;
        const auto& graph = test_data.CreateRhombusGraphWithPasses();

        TYardObjectsCounter yard_counter(graph);

        const TYardId zeroYard{0};
        const TYardId oneYard{1};

        yard_counter.AddToYard(zeroYard);

        UNIT_ASSERT_EQUAL(1u, yard_counter.CountInYard(zeroYard));

        yard_counter.AddToYard(zeroYard);

        UNIT_ASSERT_EQUAL(2u, yard_counter.CountInYard(zeroYard));
        UNIT_ASSERT_EQUAL(0u, yard_counter.CountInYard(oneYard));

        yard_counter.AddToYard(oneYard);
        UNIT_ASSERT_EQUAL(1u, yard_counter.CountInYard(oneYard));

        yard_counter.DelFromYard(zeroYard);
        UNIT_ASSERT_EQUAL(1u, yard_counter.CountInYard(zeroYard));

        yard_counter.DelFromYard(zeroYard);
        UNIT_ASSERT_EQUAL(0u, yard_counter.CountInYard(zeroYard));

        // Del from yard should have no effect now
        yard_counter.DelFromYard(zeroYard);
        UNIT_ASSERT_EQUAL(0u, yard_counter.CountInYard(zeroYard));
    }

    Y_UNIT_TEST(TestYardsMerge) {
        ::NTaxi::NGraph2::TGraphTestData test_data;
        const auto& graph = test_data.CreateRhombusGraphWithPasses();
        TYardObjectsCounter yard_counter1(graph);
        TYardObjectsCounter yard_counter2(graph);

        const TYardId zeroYard{0};
        const TYardId oneYard{1};

        yard_counter1.AddToYard(zeroYard);
        yard_counter1.AddToYard(zeroYard);
        yard_counter1.AddToYard(oneYard);
        UNIT_ASSERT_EQUAL(2u, yard_counter1.CountInYard(zeroYard));
        UNIT_ASSERT_EQUAL(1u, yard_counter1.CountInYard(oneYard));

        yard_counter2.AddToYard(oneYard);
        yard_counter2.AddToYard(oneYard);
        yard_counter2.AddToYard(zeroYard);
        UNIT_ASSERT_EQUAL(1u, yard_counter2.CountInYard(zeroYard));
        UNIT_ASSERT_EQUAL(2u, yard_counter2.CountInYard(oneYard));

        yard_counter2.Merge(yard_counter1);
        UNIT_ASSERT_EQUAL(3u, yard_counter2.CountInYard(zeroYard));
        UNIT_ASSERT_EQUAL(3u, yard_counter2.CountInYard(oneYard));
    }

}
