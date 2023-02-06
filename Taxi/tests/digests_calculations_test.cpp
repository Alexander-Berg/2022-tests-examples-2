#include <components/digests.hpp>
#include <models/digests/digests_calculations.hpp>
#include <userver/utest/utest.hpp>

namespace eats_report_storage::models::digests {

components::CurrencyRules currency_rules(
    "EATS_ORDERS_INFO_CURRENCY_RULES",
    {{"BYN", {"BYN", "руб.", "$VALUE$ $SIGN$$CURRENCY$", "руб."}},
     {"KZT", {"KZT", "₸", "$VALUE$ $SIGN$$CURRENCY$", "тнг."}},
     {"RUB", {"RUB", "₽", "$VALUE$ $SIGN$$CURRENCY$", "руб."}},
     {"__default__", {"RUB", "₽", "$VALUE$ $SIGN$$CURRENCY$", "руб."}}});

struct DigestMetricWithCurrencyData {
  double value;
  std::string currency_code;
  std::string expected_result;
};

class GetDigestMetricInCurrencyTest
    : public ::testing::TestWithParam<DigestMetricWithCurrencyData> {};

const std::vector<DigestMetricWithCurrencyData> kDigestMetricWithCurrencyData{
    {100, "RUB", "100₽"},
    {100.15, "RUB", "100₽"},
    {100.2, "RUB", "100₽"},
    {100.5, "RUB", "101₽"},
    {100.75, "RUB", "101₽"},
    {100000, "RUB", "100 000₽"},
    {100000.75, "RUB", "100 001₽"},
    {100.153214, "RUB", "100₽"},
    {100, "KZT", "100₸"},
    {100.15, "KZT", "100₸"},
    {100.2, "KZT", "100₸"},
    {100000, "BYN", "100 000руб."},
    {100.151214, "BYN", "100руб."}};

INSTANTIATE_TEST_SUITE_P(KDigestMetricWithCurrencyData,
                         GetDigestMetricInCurrencyTest,
                         ::testing::ValuesIn(kDigestMetricWithCurrencyData));

TEST_P(GetDigestMetricInCurrencyTest,
       should_return_correct_values_with_currency_sign) {
  const auto param = GetParam();
  ASSERT_EQ(GetDigestMetricInCurrency(param.value, param.currency_code,
                                      currency_rules),
            param.expected_result);
}

struct DigestMetricDeltaPercentageData {
  double value;
  double delta;
  std::string expected_result;
};

class GetDigestMetricDeltaPercentageTest
    : public ::testing::TestWithParam<DigestMetricDeltaPercentageData> {};

const std::vector<DigestMetricDeltaPercentageData>
    kDigestMetricDeltaPercentageData{
        {100, 100, "(+ >300%)"}, {100, 90, "(+ >300%)"},
        {100, 10, "(+11%)"},     {0, 0, "(0%)"},
        {100, 0, "(0%)"},        {90, -10, "(-10%)"},
        {10, -90, "(-90%)"},     {0, -100, "(-100%)"},
        {-90, -100, "(- >300%)"}};

INSTANTIATE_TEST_SUITE_P(kDigestMetricDeltaPercentageData,
                         GetDigestMetricDeltaPercentageTest,
                         ::testing::ValuesIn(kDigestMetricDeltaPercentageData));

TEST_P(GetDigestMetricDeltaPercentageTest,
       should_calculate_correct_delta_percentage) {
  const auto param = GetParam();
  ASSERT_EQ(GetDeltaPercentage(param.value, param.delta),
            param.expected_result);
}

struct DigestAverageCheckData {
  double revenue_earned_lcy;
  int orders_success_cnt;
  std::string currency_code;
  std::string expected_result;
};

class DigestAverageCheckTest
    : public ::testing::TestWithParam<DigestAverageCheckData> {};

const std::vector<DigestAverageCheckData> kDigestAverageCheckData{
    {100, 5, "RUB", "20₽"}, {100, 3, "RUB", "33₽"},
    {0, 0, "RUB", "0₽"},    {100, 0, "RUB", "0₽"},
    {0, 100, "RUB", "0₽"},  {99, 2, "RUB", "50₽"}};

INSTANTIATE_TEST_SUITE_P(kDigestAverageCheckData, DigestAverageCheckTest,
                         ::testing::ValuesIn(kDigestAverageCheckData));

TEST_P(DigestAverageCheckTest, should_return_correct_average_cheque) {
  const auto param = GetParam();
  ASSERT_EQ(GetAverageCheck(param.revenue_earned_lcy, param.orders_success_cnt,
                            param.currency_code, currency_rules),
            param.expected_result);
}

struct AverageCheckDeltaPercentageData {
  double revenue_earned_lcy;
  double revenue_earned_lcy_delta;
  int orders_success_cnt;
  int orders_success_cnt_delta;
  std::string expected_result;
};

class GetAverageCheckDeltaPercentageTest
    : public ::testing::TestWithParam<AverageCheckDeltaPercentageData> {};

const std::vector<AverageCheckDeltaPercentageData>
    kGetAverageCheckDeltaPercentageData{{100, 100, 20, 20, "(+ >300%)"},
                                        {100, 50, 20, 10, "(0%)"},
                                        {200, 50, 20, 10, "(-33%)"},
                                        {400, 100, 20, 2, "(+20%)"},
                                        {100, 0, 0, 0, "(0%)"}};

INSTANTIATE_TEST_SUITE_P(
    kGetAverageCheckDeltaPercentageData, GetAverageCheckDeltaPercentageTest,
    ::testing::ValuesIn(kGetAverageCheckDeltaPercentageData));

TEST_P(GetAverageCheckDeltaPercentageTest,
       should_return_correct_average_cheque_delta_percentage) {
  const auto param = GetParam();
  ASSERT_EQ(GetAverageCheckDeltaPercentage(
                param.revenue_earned_lcy, param.revenue_earned_lcy_delta,
                param.orders_success_cnt, param.orders_success_cnt_delta),
            param.expected_result);
}

struct CancelationsPercentage {
  int orders_total_cnt;
  int orders_success_cnt;
  std::string expected_result;
};

class GetCancelationsPercentageTest
    : public ::testing::TestWithParam<CancelationsPercentage> {};

const std::vector<CancelationsPercentage> kCancelationsPercentageData{
    {100, 80, "20%"},
    {100, 100, "0%"},
    {0, 100, "0%"},
    {100, 0, "100%"},
    {100, 33, "67%"}};

INSTANTIATE_TEST_SUITE_P(kCancelationsPercentageData,
                         GetCancelationsPercentageTest,
                         ::testing::ValuesIn(kCancelationsPercentageData));

TEST_P(GetCancelationsPercentageTest,
       should_return_correct_cancellations_percentage) {
  const auto param = GetParam();
  ASSERT_EQ(GetCancelationsPercentage(param.orders_total_cnt,
                                      param.orders_success_cnt),
            param.expected_result);
}

struct CancelationsDeltaPercentageData {
  int orders_total_cnt;
  int orders_total_cnt_delta;
  int orders_success_cnt;
  int orders_success_cnt_delta;
  std::string expected_result;
};

class GetCancelationsDeltaPercentageTest
    : public ::testing::TestWithParam<CancelationsDeltaPercentageData> {};

const std::vector<CancelationsDeltaPercentageData>
    kGetCancelationsDeltaPercentageTest{{100, 20, 50, 10, "(0%)"},
                                        {100, 10, 50, 10, "(-6%)"},
                                        {100, 100, 50, 50, "(+50%)"},
                                        {0, -25, 0, 0, "(-100%)"},
                                        {100, 50, 50, 0, "(+50%)"}};

INSTANTIATE_TEST_SUITE_P(
    kGetCancelationsDeltaPercentageTest, GetCancelationsDeltaPercentageTest,
    ::testing::ValuesIn(kGetCancelationsDeltaPercentageTest));

TEST_P(GetCancelationsDeltaPercentageTest,
       should_return_correct_cancellations_delta_percentage) {
  const auto param = GetParam();
  ASSERT_EQ(GetCancelationsDeltaPercentage(
                param.orders_total_cnt, param.orders_total_cnt_delta,
                param.orders_success_cnt, param.orders_success_cnt_delta),
            param.expected_result);
}

struct DelayMinData {
  int delay_min;
  std::string expected_result;
};

class GetDelayMinTest : public ::testing::TestWithParam<DelayMinData> {};

const std::vector<DelayMinData> kGetDelayMinTest{
    {10, "10 мин"},
    {0, "0 мин"},
};

INSTANTIATE_TEST_SUITE_P(kGetDelayMinTest, GetDelayMinTest,
                         ::testing::ValuesIn(kGetDelayMinTest));

TEST_P(GetDelayMinTest, should_return_correct_delay_min) {
  const auto param = GetParam();
  ASSERT_EQ(GetDelayMin(param.delay_min), param.expected_result);
}

struct RatingData {
  double rating;
  std::string expected_result;
};

class GetRatingTest : public ::testing::TestWithParam<RatingData> {};

const std::vector<RatingData> kGetRatingTest{
    {4.5, "4.5"},
    {4.75, "4.8"},
    {3.123, "3.1"},
};

INSTANTIATE_TEST_SUITE_P(kGetRatingTest, GetRatingTest,
                         ::testing::ValuesIn(kGetRatingTest));

TEST_P(GetRatingTest, should_return_correct_rating) {
  const auto param = GetParam();
  ASSERT_EQ(GetRating(param.rating), param.expected_result);
}

struct RatingDeltaData {
  double rating_delta;
  std::string expected_result;
};

class GetRatingDeltaTest : public ::testing::TestWithParam<RatingDeltaData> {};

const std::vector<RatingDeltaData> kRatingDeltaData{
    {0, "(0.0)"},
    {0.25, "(+0.3)"},
    {-1.1, "(-1.1)"},
    {-0.333, "(-0.3)"},
};

INSTANTIATE_TEST_SUITE_P(kRatingDeltaData, GetRatingDeltaTest,
                         ::testing::ValuesIn(kRatingDeltaData));

TEST_P(GetRatingDeltaTest, should_return_correct_rating_delta) {
  const auto param = GetParam();
  ASSERT_EQ(GetRatingDelta(param.rating_delta), param.expected_result);
}

struct AvailabilityPercentageData {
  int fact_work_time_min;
  int plan_work_time_min;
  std::string expected_result;
};

class GetAvailabilityPercentageTest
    : public ::testing::TestWithParam<AvailabilityPercentageData> {};

const std::vector<AvailabilityPercentageData> kGetAvailabilityPercentageTest{
    {80, 100, "80%"},
    {100, 100, "100%"},
    {0, 100, "0%"},
    {100, 0, "0%"},
    {33, 100, "33%"}};

INSTANTIATE_TEST_SUITE_P(kGetAvailabilityPercentageTest,
                         GetAvailabilityPercentageTest,
                         ::testing::ValuesIn(kGetAvailabilityPercentageTest));

TEST_P(GetAvailabilityPercentageTest,
       should_return_correct_availability_percentage) {
  const auto param = GetParam();
  ASSERT_EQ(GetAvailabilityPercentage(param.fact_work_time_min,
                                      param.plan_work_time_min),
            param.expected_result);
}

struct AvailabilityDeltaPercentageData {
  int fact_work_time_min;
  int fact_work_time_delta_min;
  int plan_work_time_min;
  int plan_work_time_delta_min;
  std::string expected_result;
};

class GetAvailabilityDeltaPercentageTest
    : public ::testing::TestWithParam<AvailabilityDeltaPercentageData> {};

const std::vector<AvailabilityDeltaPercentageData>
    kGetAvailabilityDeltaPercentageTest{
        {50, 10, 100, 20, "(0%)"},    {50, 10, 100, 10, "(+6%)"},
        {50, 50, 100, 100, "(+50%)"}, {100, 10, 200, 40, "(-6%)"},
        {50, 50, 100, 0, "(+50%)"},   {50, 0, 0, 0, "(0%)"},
        {50, 25, 50, 50, "(+100%)"}};

INSTANTIATE_TEST_SUITE_P(
    kGetAvailabilityDeltaPercentageTest, GetAvailabilityDeltaPercentageTest,
    ::testing::ValuesIn(kGetAvailabilityDeltaPercentageTest));

TEST_P(GetAvailabilityDeltaPercentageTest,
       should_return_correct_availability_delta_percentage) {
  const auto param = GetParam();
  ASSERT_EQ(GetAvailabilityDeltaPercentage(
                param.fact_work_time_min, param.fact_work_time_delta_min,
                param.plan_work_time_min, param.plan_work_time_delta_min),
            param.expected_result);
}

}  // namespace eats_report_storage::models::digests
