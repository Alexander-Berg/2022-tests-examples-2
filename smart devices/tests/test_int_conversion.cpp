#include <smart_devices/tools/launcher2/lib/utility.h>

#include <library/cpp/testing/unittest/registar.h>

#include <climits>
#include <cstring>

Y_UNIT_TEST_SUITE(TIntToString) {
    Y_UNIT_TEST(Conversion) {
        std::array<char, MAX_INTTOSTRING_RESULT_LENGTH> result;
        memset(result.data(), 0, MAX_INTTOSTRING_RESULT_LENGTH);
        intToString(result, 1);
        UNIT_ASSERT_STRINGS_EQUAL(result.data(), std::to_string(1));
        intToString(result, -1);
        UNIT_ASSERT_STRINGS_EQUAL(result.data(), std::to_string(-1));
        intToString(result, INT_MIN);
        UNIT_ASSERT_STRINGS_EQUAL(result.data(), std::to_string(INT_MIN));
        intToString(result, INT_MAX);
        UNIT_ASSERT_STRINGS_EQUAL(result.data(), std::to_string(INT_MAX));
        intToString(result, 0);
        UNIT_ASSERT_STRINGS_EQUAL(result.data(), std::to_string(0));
    }
}
