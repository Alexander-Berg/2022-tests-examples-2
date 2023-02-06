#include <library/cpp/testing/unittest/registar.h>
#include <robot/rthub/yql/udfs/turbopages/library/domain_list.h>

using namespace NTurboPages;

Y_UNIT_TEST_SUITE(GetNormalizedHostTestSuite)
{
    Y_UNIT_TEST(PrefixOnly) {
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("www.example.com", true), "example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("m.www.example.com", true), "example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("m.www2.example.com", true), "www2.example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("wwww.www.example.com", true), "wwww.www.example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("www2.m.example.www.com", true), "www2.m.example.www.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("www-2.m.example.www.com", true), "www-2.m.example.www.com");
    }

    Y_UNIT_TEST(EdgeCases) {
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("", false), "");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("", true), "");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("com", false), "com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("com", true), "com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("www.com", false), "www.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("www.com", true), "www.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("www", true), "www");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("www", false), "www");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("example.com", false), "example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("example.com", true), "example.com");
    }

    Y_UNIT_TEST(WholeDomain) {
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("www.example.com", false), "example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("m.www.example.com", false), "example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("m.www2.example.com", false), "www2.example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("m.www2.ru.www.example.com", false), "www2.ru.example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("wwww.example.com", false), "wwww.example.com");
        UNIT_ASSERT_VALUES_EQUAL(GetNormalizedHost("wwww.ru.www.example.com", false), "wwww.ru.example.com");
    }
}
