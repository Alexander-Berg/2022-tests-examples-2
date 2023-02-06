#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/persistent_index.h>
#include <taxi/graph/libs/graph/closures.h>

#include <yandex/maps/jams/static_graph2/persistent_index.h>
#include <maps/libs/edge_persistent_index/include/persistent_index.h>

#include <yandex/maps/jams/router/closures.h>

using NTaxi::NGraph2::TClosureInfo;
using NTaxi::NGraph2::TClosures;
using NTaxi::NGraph2::TEdgeId;
using NTaxi::NGraph2::TId;
using NTaxi::NGraph2::TPersistentIndex;
using namespace NTaxi::NGraph2Literals;

using namespace std::chrono_literals;

namespace {
    const time_t NOW = 1'548'110'622;
    const auto SCNOW = std::chrono::system_clock::from_time_t(NOW);

    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }

    template <typename PersistentIndexType>
    void CreateAndSaveClosures(const PersistentIndexType& index) {
        using maps::jams::router::proto::ClosureType;
        maps::jams::router::Closures closures(index, NOW);

        const int region = 0;
        closures.addClosure(65'035_eid, region, NOW - 600, NOW + 1'000, ClosureType::REGULAR);
        closures.addClosure(218'120_eid, region, NOW - 10'000, NOW - 2'600, ClosureType::REGULAR);
        closures.addClosure(218'120_eid, region, NOW + 1'200, NOW + 8'700, ClosureType::REGULAR);
        closures.addClosure(97'508_eid, region, NOW - 200'000, NOW + 100, ClosureType::REGULAR);

        closures.save(GraphPath("test_closures.pb"));
    }

}

Y_UNIT_TEST_SUITE(taxi_graph_closures) {
    Y_UNIT_TEST(load_from_file_with_new_index) {
        CreateAndSaveClosures(maps::road_graph::PersistentIndex(
            GraphPath("edges_persistent_index.fb")));

        TPersistentIndex newIndex(
            GraphPath("edges_persistent_index.fb").data());

        TClosures closures(
            newIndex, GraphPath("test_closures.pb").data());

        UNIT_ASSERT(!closures.IsClosedAtMoment(12'803_eid, SCNOW));
        UNIT_ASSERT(!closures.IsClosedAtMoment(218'120_eid, SCNOW));

        auto closedIds = closures.ClosuresActiveAtMoment(SCNOW);
        UNIT_ASSERT(closedIds.Size() == 2);

        TClosureInfo closureInfo(std::chrono::system_clock::time_point::min(), std::chrono::system_clock::time_point::min());
        UNIT_ASSERT(!closures.FetchClosureInfo(closureInfo, closedIds, 12'803_eid));

        for (const auto& [id, ignore] : closedIds) {
            UNIT_ASSERT(closures.IsClosedAtMoment(TEdgeId{id}, SCNOW));
            UNIT_ASSERT(closures.FetchClosureInfo(closureInfo, closedIds, TEdgeId{id}));
        }
    }

    Y_UNIT_TEST(test_closures_builder) {
        TPersistentIndex newIndex(
            GraphPath("edges_persistent_index.fb").data());

        auto builder = TClosures(newIndex, SCNOW);

        const int region = 0;
        builder.AddClosure(65'035_eid, region, SCNOW - 600s, SCNOW + 1'000s);
        builder.AddClosure(218'120_eid, region, SCNOW - 10'000s, SCNOW - 2'600s);
        builder.AddClosure(218'120_eid, region, SCNOW + 1'200s, SCNOW + 8'700s);
        builder.AddClosure(97'508_eid, region, SCNOW - 200'000s, SCNOW + 100s);

        TClosures closures(std::move(builder));

        UNIT_ASSERT(!closures.IsClosedAtMoment(12'803_eid, SCNOW));
        UNIT_ASSERT(!closures.IsClosedAtMoment(218'120_eid, SCNOW));

        auto closedIds = closures.ClosuresActiveAtMoment(SCNOW);
        UNIT_ASSERT(closedIds.Size() == 2);

        TClosureInfo closureInfo(std::chrono::system_clock::time_point::min(), std::chrono::system_clock::time_point::min());
        UNIT_ASSERT(!closures.FetchClosureInfo(closureInfo, closedIds, 2'803_eid));

        for (const auto& [id, ignore] : closedIds) {
            UNIT_ASSERT(closures.IsClosedAtMoment(TEdgeId{id}, SCNOW));
            UNIT_ASSERT(closures.FetchClosureInfo(closureInfo, closedIds, TEdgeId{id}));
        }
    }
}
