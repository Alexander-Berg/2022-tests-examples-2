#include <userver/utest/utest.hpp>

#include <userver/utils/datetime.hpp>

#include <discounts/utils/utils.hpp>

TEST(Datetime, CheckTimeShift) {
  using TimePoint = std::chrono::system_clock::time_point;
  const TimePoint tp = utils::datetime::Stringtime("2010-01-01T12:00:00+0000");
  const std::optional<std::string> request_timezone("Europe/Moscow");
  const TimePoint shifted_tp =
      discounts::utils::MakeRequestTime(tp, request_timezone);
  auto timediff =
      std::chrono::duration_cast<std::chrono::seconds>(shifted_tp - tp);
  ASSERT_EQ(timediff.count(), 10800u);
}

TEST(ConvertToDataId, Error) {
  EXPECT_THROW(discounts::utils::ConvertToDataId("123f"),
               discounts::models::Error)
      << "invalid";
  EXPECT_THROW(discounts::utils::ConvertToDataId("aaa"),
               discounts::models::Error)
      << "invalid";
  EXPECT_THROW(discounts::utils::ConvertToDataId("9223372036854775808"),
               discounts::models::Error)
      << "More than int64 max";
}

TEST(ConvertToDataId, Ok) {
  EXPECT_EQ(discounts::utils::ConvertToDataId("123"),
            rules_match::RulesMatchBase::DataId(123));
}
