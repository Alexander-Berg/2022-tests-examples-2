#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <taxi/graph/libs/graph/conversions.h>

using NTaxi::NGraph2::ConvertToString;
using NTaxi::NGraph2::TEdgeCategory;

Y_UNIT_TEST_SUITE(EdgeCategoryConversion) {
    Y_UNIT_TEST(Conversions) {
        TEdgeCategory category = TEdgeCategory::EC_UNKNOWN;
        UNIT_ASSERT_STRINGS_EQUAL(ConvertToString(category).Data(), "unknown");

        category = TEdgeCategory::EC_PASSES;
        UNIT_ASSERT_STRINGS_EQUAL(ConvertToString(category).Data(), "passes");

        category = TEdgeCategory::EC_FEDERAL_ROADS;
        UNIT_ASSERT_STRINGS_EQUAL(ConvertToString(category).Data(), "federal_roads");
    }
}
