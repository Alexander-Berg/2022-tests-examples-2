#include <userver/utest/utest.hpp>

#include <boost/regex.hpp>

#include <fmt/format.h>
#include <gtest/gtest.h>
#include <gtest/internal/gtest-param-util.h>
#include <boost/algorithm/string.hpp>

#include <userver/utest/parameter_names.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <events/models.hpp>
#include <events/query.hpp>
#include <events/yql_query.hpp>

using namespace fmt::literals;

namespace coupons::events {

namespace {

const std::string kExpectedQueryTemplate = R"-(
USE chyt.hahn;

PRAGMA chyt.dynamic_table.enable_dynamic_store_read = 0;

SELECT
    moment,
    type,
    phone_id,
    yandex_uid,
    coupon,
    series,
    ConvertYson(extra, 'text') as extra
FROM concatYtTablesRange('//home/taxi/testing/replica/postgres/coupons/events',
                         '{month_from}', '{month_to}')
WHERE
  {predicate}
ORDER BY
    moment DESC
;
)-";

std::string FormatQuery(const std::string& query) {
  boost::regex re("[\\s]+");
  auto single_spaced = boost::regex_replace(query, re, " ");
  return boost::algorithm::trim_copy(single_spaced);
}

void CheckQueriesEqual(const std::string& lhs, const std::string& rhs) {
  EXPECT_EQ(FormatQuery(lhs), FormatQuery(rhs));
}

TimePoint TimePointFromString(const std::string& source) {
  return ::utils::datetime::GuessStringtime(source, "Europe/Moscow");
}

template <typename T>
EventsQuery RangedQuery(const T& params) {
  EventsQuery query;
  query.coupon = "promocode";

  if (params.moment_from) {
    query.moment_from = TimePointFromString(*params.moment_from);
  }
  if (params.moment_to) {
    query.moment_to = TimePointFromString(*params.moment_to);
  }
  return query;
}

}  // namespace

class MockNowTest : public testing::Test {
 protected:
  void SetUp() override {
    static const auto mocked_time = ::utils::datetime::GuessStringtime(
        "2020-11-15T12:00:00+03:00", "Europe/Moscow");
    ::utils::datetime::MockNowSet(mocked_time);
  }

  void TearDown() override { ::utils::datetime::MockNowUnset(); }
};

struct TableSourceValidParams {
  std::string environment;
  std::optional<std::string> moment_from;
  std::optional<std::string> moment_to;

  std::string expected_month_from;
  std::string expected_month_to;

  std::string test_name;
};

class EventsYqlTableSourceValid
    : public MockNowTest,
      public testing::WithParamInterface<TableSourceValidParams> {};

const std::vector<TableSourceValidParams> yql_table_source_valid_params{
    {
        "testing",
        {},
        {},
        "2019-11",
        "2020-11",
        "NoFilterOnMoment",
    },
    {
        "testing",
        "2020-07-11T13:00:00+03:00",
        {},
        "2020-07",
        "2020-11",
        "FromFilterOnMoment",
    },
    {
        "testing",
        {},
        "2020-09-11T13:00:00+03:00",
        "2019-11",
        "2020-09",
        "ToFilterOnMoment",
    },
    {
        "production",
        "2020-07-11T13:00:00+03:00",
        "2020-09-11T13:00:00+03:00",
        "2020-07",
        "2020-09",
        "NarrowFilterOnMoment",
    },
    {
        "production",
        "2015-07-11T13:00:00+03:00",
        "2025-09-11T13:00:00+03:00",
        "2019-11",
        "2020-11",
        "WideFilterOnMoment",
    },
};

TEST_P(EventsYqlTableSourceValid, ) {
  const auto& param = GetParam();

  auto query = RangedQuery(param);

  const auto expected_table = fmt::format(
      "concatYtTablesRange("
      "'//home/taxi/{}/replica/postgres/coupons/events', '{}', '{}')",
      param.environment, param.expected_month_from, param.expected_month_to);

  EXPECT_EQ(BuildYqlSourceTable(query, param.environment), expected_table);
}

INSTANTIATE_TEST_SUITE_P(, EventsYqlTableSourceValid,
                         testing::ValuesIn(yql_table_source_valid_params),
                         ::utest::PrintTestName());

struct TableSourceInvalidParams {
  std::optional<std::string> moment_from;
  std::optional<std::string> moment_to;

  std::string test_name;
};

class EventsYqlTableSourceInvalid
    : public MockNowTest,
      public testing::WithParamInterface<TableSourceInvalidParams> {};

const std::vector<TableSourceInvalidParams> yql_table_source_invalid_params{
    {
        "2025-07-11T13:00:00+03:00",
        "2015-09-11T13:00:00+03:00",
        "ReversedRange",
    },
    {
        "2020-09-11T13:00:00+03:00",
        "2020-07-11T13:00:00+03:00",
        "ReversedRangeInsideDefaultRange",
    },
    {
        "2025-07-11T13:00:00+03:00",
        {},
        "MomentFromAfterDefaultRange",
    },
    {
        {},
        "2015-09-11T13:00:00+03:00",
        "MomentToBeforeDefaultRange",
    },
};

TEST_P(EventsYqlTableSourceInvalid, ) {
  const auto& param = GetParam();

  auto query = RangedQuery(param);

  EXPECT_THROW(BuildYqlSourceTable(query, "production"),
               InvalidMomentException);
}

INSTANTIATE_TEST_SUITE_P(, EventsYqlTableSourceInvalid,
                         testing::ValuesIn(yql_table_source_invalid_params),
                         ::utest::PrintTestName());

class EventsYqlQueryTest : public MockNowTest {};

TEST_F(EventsYqlQueryTest, OnlyCoupon) {
  EventsQuery query;
  query.coupon = "promocode";

  const std::string expected_query = fmt::format(
      kExpectedQueryTemplate, "month_from"_a = "2019-11",
      "month_to"_a = "2020-11", "predicate"_a = "coupon = 'promocode'");

  CheckQueriesEqual(BuildYqlQuery(query, "testing"), expected_query);
}

TEST_F(EventsYqlQueryTest, MultipleFilters) {
  EventsQuery query;
  query.coupon = "promocode";
  query.phone_id = "phone_id";
  query.yandex_uid = "yandex_uid";
  query.event_types = {"activate", "check"};

  const std::string expected_predicate =
      "coupon = 'promocode' AND "
      "phone_id = 'phone_id' AND "
      "yandex_uid = 'yandex_uid' AND "
      "type IN ('activate', 'check')";

  const std::string expected_query =
      fmt::format(kExpectedQueryTemplate, "month_from"_a = "2019-11",
                  "month_to"_a = "2020-11", "predicate"_a = expected_predicate);

  CheckQueriesEqual(BuildYqlQuery(query, "testing"), expected_query);
}

struct MomentFilterParams {
  std::optional<std::string> moment_from;
  std::optional<std::string> moment_to;

  std::string expected_month_from;
  std::string expected_month_to;
  std::optional<std::string> expected_moment_predicate;

  std::string test_name;
};

class EventsYqlMomentFilter
    : public MockNowTest,
      public testing::WithParamInterface<MomentFilterParams> {};

const std::vector<MomentFilterParams> moment_filter_params{
    {
        {},
        {},
        "2019-11",
        "2020-11",
        {},
        "NoFilterOnMoment",
    },
    {
        "2020-07-11T13:00:00+03:00",
        {},
        "2020-07",
        "2020-11",
        "moment >= '2020-07-11T10:00:00.000000'",
        "MomentFrom",
    },
    {
        {},
        "2020-07-11T13:00:00.123+03:00",
        "2019-11",
        "2020-07",
        "moment <= '2020-07-11T10:00:00.123000'",
        "MomentTo",
    },
    {
        "2020-06-11T13:00:00+03:00",
        "2020-07-11T13:00:00.123+03:00",
        "2020-06",
        "2020-07",
        "moment >= '2020-06-11T10:00:00.000000' AND "
        "moment <= '2020-07-11T10:00:00.123000'",
        "MomentRange",
    },
};

TEST_P(EventsYqlMomentFilter, ) {
  const auto& param = GetParam();

  auto query = RangedQuery(param);

  std::string expected_predicate = "coupon = 'promocode'";
  if (param.expected_moment_predicate) {
    expected_predicate += " AND " + *param.expected_moment_predicate;
  }

  const std::string expected_query = fmt::format(
      kExpectedQueryTemplate, "month_from"_a = param.expected_month_from,
      "month_to"_a = param.expected_month_to,
      "predicate"_a = expected_predicate);

  CheckQueriesEqual(BuildYqlQuery(query, "testing"), expected_query);
}

INSTANTIATE_TEST_SUITE_P(, EventsYqlMomentFilter,
                         testing::ValuesIn(moment_filter_params),
                         ::utest::PrintTestName());

}  // namespace coupons::events
