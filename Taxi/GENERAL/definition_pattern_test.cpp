#include <userver/utest/utest.hpp>

#include <userver/formats/json/value_builder.hpp>

#include <discounts/defs/all_definitions.hpp>

namespace {

template <typename String>
void Parse(const std::string& test_string) {
  formats::json::ValueBuilder data;
  data["value"] = test_string;
  handlers::libraries::discounts::Parse(data.ExtractValue(),
                                        formats::parse::To<String>{});
}

template <typename T>
void CheckBad(const std::string& test_string) {
  ASSERT_THROW(Parse<T>(test_string), formats::json::Value::ParseException);
}

template <typename T>
void CheckGood(const std::string& test_string) {
  ASSERT_NO_THROW(Parse<T>(test_string));
}

constexpr auto CheckBadDecimalString =
    CheckBad<handlers::libraries::discounts::TestNonNegativeDecimalString>;

constexpr auto CheckGoodDecimalString =
    CheckGood<handlers::libraries::discounts::TestNonNegativeDecimalString>;

constexpr auto CheckBadPercentString =
    CheckBad<handlers::libraries::discounts::TestDecimalPercentString>;

constexpr auto CheckGoodPercentString =
    CheckGood<handlers::libraries::discounts::TestDecimalPercentString>;

constexpr auto CheckBadDateTimeNoTzString =
    CheckBad<handlers::libraries::discounts::TestDateTimeNoTzString>;

constexpr auto CheckGoodDateTimeNoTzString =
    CheckGood<handlers::libraries::discounts::TestDateTimeNoTzString>;
}  // namespace

TEST(StringPattern, NonNegativeDecimalString) {
  CheckBadDecimalString("");
  CheckBadDecimalString("+1");
  CheckBadDecimalString("-1");
  CheckBadDecimalString("1,0");
  CheckBadDecimalString("1.1.0");
  CheckBadDecimalString("01");
  CheckBadDecimalString("0.1.1");
  CheckBadDecimalString("text");
  CheckGoodDecimalString("1000.0");
  CheckGoodDecimalString("2020");
  CheckGoodDecimalString("100500.1231234112341234123412");
  CheckGoodDecimalString("100.0000000000000000000000001");
  CheckGoodDecimalString("100.0000000000000000000000000");
  CheckGoodDecimalString("100");
  CheckGoodDecimalString("0");
  CheckGoodDecimalString("0.000");
  CheckGoodDecimalString("0.1");
  CheckGoodDecimalString("1");
  CheckGoodDecimalString("10.5");
}

TEST(StringPattern, DecimalPercentString) {
  CheckBadPercentString("");
  CheckBadPercentString("+1");
  CheckBadPercentString("-1");
  CheckBadPercentString("1,0");
  CheckBadPercentString("1.1.0");
  CheckBadPercentString("01");
  CheckBadPercentString("0.1.1");
  CheckBadPercentString("text");
  CheckBadPercentString("1000.0");
  CheckBadPercentString("2020");
  CheckBadPercentString("100500.1231234112341234123412");
  CheckBadPercentString("100.0000000000000000000000001");
  CheckGoodPercentString("100.0000000000000000000000000");
  CheckGoodPercentString("100");
  CheckGoodPercentString("0");
  CheckGoodPercentString("0.000");
  CheckGoodPercentString("0.1");
  CheckGoodPercentString("1");
  CheckGoodPercentString("10.5");
  CheckGoodPercentString("99.999999999999999999999999999999999");
}

TEST(StringPattern, TestDateTimeNoTzString) {
  CheckBadDateTimeNoTzString("");
  CheckBadDateTimeNoTzString("10000-01-01T00:00:00");
  CheckBadDateTimeNoTzString("100-01-01T00:00:00");
  CheckBadDateTimeNoTzString("1000-0-01T00:00:00");
  CheckBadDateTimeNoTzString("1000-100-01T00:00:00");
  CheckBadDateTimeNoTzString("1000-00-01T00:00:00");
  CheckBadDateTimeNoTzString("1000-13-01T00:00:00");
  CheckBadDateTimeNoTzString("1000-01-0T00:00:00");
  CheckBadDateTimeNoTzString("1000-01-100T00:00:00");
  CheckBadDateTimeNoTzString("1000-01-00T00:00:00");
  CheckBadDateTimeNoTzString("1000-01-32T00:00:00");
  CheckBadDateTimeNoTzString("1000-01-31T0:00:00");
  CheckBadDateTimeNoTzString("1000-01-31T100:00:00");
  CheckBadDateTimeNoTzString("1000-01-31T24:00:00");
  CheckBadDateTimeNoTzString("1000-01-31T00:0:00");
  CheckBadDateTimeNoTzString("1000-01-31T00:100:00");
  CheckBadDateTimeNoTzString("1000-01-31T00:60:00");
  CheckBadDateTimeNoTzString("1000-01-31T00:00:0");
  CheckBadDateTimeNoTzString("1000-01-31T00:00:100");
  CheckBadDateTimeNoTzString("1000-01-31T00:00:60");
  CheckBadDateTimeNoTzString("2020-03-18T23:59:00+0000");
  CheckBadDateTimeNoTzString("2020-03-18T23:59:00+00:00");
  CheckGoodDateTimeNoTzString("2020-03-18T23:59:00");
  CheckGoodDateTimeNoTzString("2020-02-31T23:59:00");
  CheckGoodDateTimeNoTzString("0000-02-31T23:59:00");
  CheckGoodDateTimeNoTzString("9999-02-31T23:59:00");
  CheckGoodDateTimeNoTzString("2020-01-31T23:59:00");
  CheckGoodDateTimeNoTzString("2020-12-31T23:59:00");
  CheckGoodDateTimeNoTzString("2020-12-01T23:59:00");
  CheckGoodDateTimeNoTzString("2020-12-01T00:59:00");
  CheckGoodDateTimeNoTzString("2020-12-01T00:00:00");
  CheckGoodDateTimeNoTzString("2020-12-01T00:00:59");
}
