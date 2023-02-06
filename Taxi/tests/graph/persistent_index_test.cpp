#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/types.h>
#include <taxi/graph/libs/graph/persistent_index.h>

using NTaxi::NGraph2::TPersistentEdgeId;
using NTaxi::NGraph2::TPersistentIndex;
using NTaxi::NGraph2::TPersistentIndexBuilder;

using namespace NTaxi::NGraph2Literals;

namespace {
    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }

}

Y_UNIT_TEST_SUITE(taxi_graph_persistent_index) {
    Y_UNIT_TEST(load_from_fb_file) {
        TPersistentIndex index(
            GraphPath("edges_persistent_index.fb").data());

        UNIT_ASSERT_UNEQUAL(index.Size(), 0u);
        const NTaxi::NGraph2::TEdgeId shortId = 1234_eid;

        const auto& foundLongId = index.FindLongId(shortId);
        UNIT_ASSERT(foundLongId.has_value());

        const auto& foundShortId = index.FindShortId(foundLongId.value());
        UNIT_ASSERT(foundShortId.has_value());
        UNIT_ASSERT_EQUAL(foundShortId.value(), shortId);

        const auto& version = index.Version();
        UNIT_ASSERT_STRINGS_EQUAL(version.Data(), "3.0.0-0");
    }

    Y_UNIT_TEST(load_from_builder) {
        auto builder = TPersistentIndexBuilder();

        const NTaxi::NGraph2::TId shortId = 1234_eid;
        const NTaxi::NGraph2::TLongId longId = TPersistentEdgeId{(1ll << 40) + 12345};

        builder.Add(longId, shortId);

        char filename[]{"persistent_index.XXXXXX"};
        int fd = mkstemp(filename);
        UNIT_ASSERT_UNEQUAL(-1, fd);
        // filename now contains actual filename

        TPersistentIndex index(builder.Build(filename));

        UNIT_ASSERT_EQUAL(index.Size(), 1u);

        const auto& foundLongId = index.FindLongId(shortId);
        UNIT_ASSERT(foundLongId.has_value());
        UNIT_ASSERT_EQUAL(foundLongId.value(), longId);

        const auto& foundShortId = index.FindShortId(foundLongId.value());
        UNIT_ASSERT(foundShortId.has_value());
        UNIT_ASSERT_EQUAL(foundShortId.value(), shortId);

        const auto& version = index.Version();
        UNIT_ASSERT_STRINGS_EQUAL(version.Data(), "test_version");
    }
}
