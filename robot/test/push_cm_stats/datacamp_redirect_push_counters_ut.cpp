#include <library/cpp/testing/unittest/registar.h>
#include <robot/blrt/tools/push_cm_stats/lib/datacamp_redirect_push_counters.h>

Y_UNIT_TEST_SUITE(RedirectUrlStatsTest) {

    Y_UNIT_TEST(GetOfferAgeCategory) {
        UNIT_ASSERT_EQUAL(NBlrt::GetOfferAgeCategory(TDuration::Zero()),    NBlrt::EOAC_3_HOURS);
        UNIT_ASSERT_EQUAL(NBlrt::GetOfferAgeCategory(TDuration::Hours(3)),  NBlrt::EOAC_3_HOURS);
        UNIT_ASSERT_EQUAL(NBlrt::GetOfferAgeCategory(TDuration::Hours(6)),  NBlrt::EOAC_6_HOURS);
        UNIT_ASSERT_EQUAL(NBlrt::GetOfferAgeCategory(TDuration::Hours(10)), NBlrt::EOAC_12_HOURS);
        UNIT_ASSERT_EQUAL(NBlrt::GetOfferAgeCategory(TDuration::Hours(16)), NBlrt::EOAC_24_HOURS);
        UNIT_ASSERT_EQUAL(NBlrt::GetOfferAgeCategory(TDuration::Hours(36)), NBlrt::EOAC_48_HOURS);
        UNIT_ASSERT_EQUAL(NBlrt::GetOfferAgeCategory(TDuration::Hours(99)), NBlrt::EOAC_INFINITE);
    }

    Y_UNIT_TEST(GetRedirectResolvingTimeBucket) {
        UNIT_ASSERT_EQUAL(NBlrt::GetRedirectResolvingTimeBucket(TDuration::Hours(3)), 3);
        UNIT_ASSERT_EQUAL(NBlrt::GetRedirectResolvingTimeBucket(TDuration::Days(3)), 72);
        UNIT_ASSERT_EQUAL(NBlrt::GetRedirectResolvingTimeBucket(TDuration::Days(7)), 168);
    }

}
