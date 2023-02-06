#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex/taxi/graph2/persistent_index.h>

using NTaxiExternal::NGraph2::TPersistentIndex;

namespace {
    TString GraphPath(const TStringBuf& str) {
        static const TString prefix = "taxi/graph/data/graph3/";
        return BinaryPath(prefix + str);
    }

}

Y_UNIT_TEST_SUITE(taxi_graph_persistent_index) {

    Y_UNIT_TEST(load_from_fb_file) {
        TPersistentIndex index(
            TPersistentIndex::TFBLoader::Create(
                GraphPath("edges_persistent_index.fb").data())
                .Release());

        UNIT_ASSERT_UNEQUAL(index.Size(), 0u);
        const NTaxiExternal::NGraph2::TId shortId = 1234;

        const auto& foundLongId = index.FindLongId(shortId);
        UNIT_ASSERT(foundLongId.isInitialized);

        const auto& foundShortId = index.FindShortId(foundLongId.value);
        UNIT_ASSERT(foundShortId.isInitialized);
        UNIT_ASSERT_EQUAL(foundShortId.value, shortId);

        const auto& version = index.Version();
        UNIT_ASSERT_STRINGS_EQUAL(version.Data(), "3.0.0-0");
    }

}
