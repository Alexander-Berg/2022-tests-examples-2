#include <userver/utest/utest.hpp>

#include <memory>

#include <accounting/driver_fix/calculator.hpp>
#include <common/types.hpp>
#include <models/subvention_rule.hpp>

namespace accounting = billing_time_events::accounting;
namespace models = billing_time_events::models;
namespace types = billing_time_events::types;

namespace {

class DriverFixCalculatorTest : public ::testing::Test {
  void SetUp() override {
    data_.currency = "USD";
    data_.tariff_classes = {"econom"};
    data_.payment_type_restrictions = models::PaymentTypeRestrictions::kOnline;
    data_.geoarea = "kursk";
    data_.validity = {
        ::utils::datetime::Stringtime("2020-08-01T22:00:00Z", "UTC"),
        ::utils::datetime::Stringtime("2020-08-02T01:00:00Z", "UTC")};

    rate_ = types::Numeric{6};

    event_.payload.tariff_classes = {"econom", "comfort"};
    event_.payload.payment_type_restrictions =
        models::ToString(models::PaymentTypeRestrictions::kOnline);
    event_.payload.geoareas = {"kursk"};
    event_.payload.status = "free";
    event_.amount = std::chrono::minutes{6};
    event_.event_at =
        ::utils::datetime::Stringtime("2020-08-01T23:00:00Z", "UTC");
  }

 protected:
  models::driver_fix::RuleCalcBasis data_;
  types::Numeric rate_;
  models::Event event_{};
};
}  // namespace

TEST_F(DriverFixCalculatorTest, NotMatchingStatus) {
  event_.payload.status = "blocked";
  auto entries =
      accounting::driver_fix::calculator::Calculate(data_, rate_, event_);
  ASSERT_EQ(entries.size(), 1);
  EXPECT_EQ(entries[0].amount, types::Numeric{6});
  EXPECT_EQ(entries[0].currency, "XXX");
  EXPECT_EQ(entries[0].timestamp, event_.event_at);
  EXPECT_EQ(entries[0].sub_account, "unfit/time/free_minutes");

  ASSERT_EQ(entries[0].match_info.size(), 1);
  EXPECT_FALSE(entries[0].match_info[0].matched);
  ASSERT_TRUE(entries[0].match_info[0].reason);
  EXPECT_EQ(entries[0].match_info[0].reason->type,
            models::match_info::Type::kEq);
  EXPECT_EQ(entries[0].match_info[0].reason->code, "status");
  auto details = entries[0].match_info[0].reason->details;
  ASSERT_TRUE(details.HasMember("value"));
  ASSERT_TRUE(details.HasMember("expected"));
  EXPECT_EQ(details["value"].As<std::string>(), "blocked");
  EXPECT_EQ(details["expected"].As<std::string>(), "free");
}

TEST_F(DriverFixCalculatorTest, NotMatchingTariffClasses) {
  event_.payload.tariff_classes = {"business"};
  auto entries =
      accounting::driver_fix::calculator::Calculate(data_, rate_, event_);
  ASSERT_EQ(entries.size(), 1);
  EXPECT_EQ(entries[0].amount, types::Numeric{6});
  EXPECT_EQ(entries[0].currency, "XXX");
  EXPECT_EQ(entries[0].timestamp, event_.event_at);
  EXPECT_EQ(entries[0].sub_account, "unfit/time/free_minutes");

  ASSERT_EQ(entries[0].match_info.size(), 1);
  EXPECT_FALSE(entries[0].match_info[0].matched);
  ASSERT_TRUE(entries[0].match_info[0].reason);
  EXPECT_EQ(entries[0].match_info[0].reason->type,
            models::match_info::Type::kAllIn);
  EXPECT_EQ(entries[0].match_info[0].reason->code, "tariff_classes");
  auto details = entries[0].match_info[0].reason->details;
  ASSERT_TRUE(details.HasMember("values"));
  ASSERT_TRUE(details.HasMember("required_values"));
  EXPECT_EQ(details["required_values"][0].As<std::string>(), "econom");
  EXPECT_EQ(details["values"][0].As<std::string>(), "business");
}

TEST_F(DriverFixCalculatorTest, NotMatchedPaymentType) {
  event_.payload.payment_type_restrictions =
      models::ToString(models::PaymentTypeRestrictions::kCash);

  auto entries =
      accounting::driver_fix::calculator::Calculate(data_, rate_, event_);
  ASSERT_EQ(entries.size(), 1);
  EXPECT_EQ(entries[0].amount, types::Numeric{6});
  EXPECT_EQ(entries[0].currency, "XXX");
  EXPECT_EQ(entries[0].timestamp, event_.event_at);
  EXPECT_EQ(entries[0].sub_account, "unfit/time/free_minutes");

  ASSERT_EQ(entries[0].match_info.size(), 1);
  EXPECT_FALSE(entries[0].match_info[0].matched);
  ASSERT_TRUE(entries[0].match_info[0].reason);
  EXPECT_EQ(entries[0].match_info[0].reason->type,
            models::match_info::Type::kIn);
  EXPECT_EQ(entries[0].match_info[0].reason->code,
            "profile_payment_type_restrictions");
  auto details = entries[0].match_info[0].reason->details;
  ASSERT_TRUE(details.HasMember("allowed_values"));
  ASSERT_TRUE(details.HasMember("value"));
  EXPECT_EQ(details["value"].As<std::string>(), "cash");
  EXPECT_EQ(details["allowed_values"][0].As<std::string>(), "online");
}

TEST_F(DriverFixCalculatorTest, NotMatchedGeoareas) {
  event_.payload.geoareas = {"moscow"};

  auto entries =
      accounting::driver_fix::calculator::Calculate(data_, rate_, event_);
  ASSERT_EQ(entries.size(), 1);
  EXPECT_EQ(entries[0].amount, types::Numeric{6});
  EXPECT_EQ(entries[0].currency, "XXX");
  EXPECT_EQ(entries[0].timestamp, event_.event_at);
  EXPECT_EQ(entries[0].sub_account, "unfit/time/free_minutes");

  ASSERT_EQ(entries[0].match_info.size(), 1);
  EXPECT_FALSE(entries[0].match_info[0].matched);
  ASSERT_TRUE(entries[0].match_info[0].reason);
  EXPECT_EQ(entries[0].match_info[0].reason->type,
            models::match_info::Type::kIntersection);
  EXPECT_EQ(entries[0].match_info[0].reason->code, "geoarea");
  auto details = entries[0].match_info[0].reason->details;
  ASSERT_TRUE(details.HasMember("allowed_values"));
  ASSERT_TRUE(details.HasMember("values"));
  EXPECT_EQ(details["values"][0].As<std::string>(), "moscow");
  EXPECT_EQ(details["allowed_values"][0].As<std::string>(), "kursk");
}

TEST_F(DriverFixCalculatorTest, FitAll) {
  auto entries =
      accounting::driver_fix::calculator::Calculate(data_, rate_, event_);
  ASSERT_EQ(entries.size(), 2);
  EXPECT_EQ(entries[0].amount, types::Numeric{6});
  EXPECT_EQ(entries[0].currency, "XXX");
  EXPECT_EQ(entries[0].timestamp, event_.event_at);
  EXPECT_EQ(entries[0].sub_account, "time/free_minutes");
  ASSERT_EQ(entries[0].match_info.size(), 1);
  EXPECT_TRUE(entries[0].match_info[0].matched);
  EXPECT_FALSE(entries[0].match_info[0].reason);

  EXPECT_EQ(entries[1].amount, types::Numeric{36});
  EXPECT_EQ(entries[1].currency, "USD");
  EXPECT_EQ(entries[1].timestamp, event_.event_at);
  EXPECT_EQ(entries[1].sub_account, "guarantee");
  ASSERT_EQ(entries[1].match_info.size(), 1);
  EXPECT_TRUE(entries[1].match_info[0].matched);
  EXPECT_FALSE(entries[1].match_info[0].reason);
}

TEST_F(DriverFixCalculatorTest, FitAlmostAll) {
  event_.event_at =
      ::utils::datetime::Stringtime("2020-08-01T21:50:00Z", "UTC");
  event_.amount = std::chrono::minutes{10 + 180 + 10};

  auto entries =
      accounting::driver_fix::calculator::Calculate(data_, rate_, event_);
  ASSERT_EQ(entries.size(), 4);

  EXPECT_EQ(entries[0].amount, types::Numeric{180});
  EXPECT_EQ(entries[0].currency, "XXX");
  EXPECT_EQ(entries[0].timestamp, data_.validity.lower());
  EXPECT_EQ(entries[0].sub_account, "time/free_minutes");
  ASSERT_EQ(entries[0].match_info.size(), 1);
  EXPECT_TRUE(entries[0].match_info[0].matched);
  EXPECT_FALSE(entries[0].match_info[0].reason);

  EXPECT_EQ(entries[1].amount, types::Numeric{10});
  EXPECT_EQ(entries[1].currency, "XXX");
  EXPECT_EQ(entries[1].timestamp, event_.event_at);
  EXPECT_EQ(entries[1].sub_account, "unfit/time/free_minutes");
  ASSERT_EQ(entries[1].match_info.size(), 1);
  EXPECT_FALSE(entries[1].match_info[0].matched);
  ASSERT_TRUE(entries[1].match_info[0].reason);
  EXPECT_EQ(entries[1].match_info[0].reason->code, "interval");
  EXPECT_EQ(entries[1].match_info[0].reason->type,
            models::match_info::Type::kIntersection);
  auto details = entries[1].match_info[0].reason->details;
  ASSERT_TRUE(details.HasMember("values"));
  ASSERT_TRUE(details.HasMember("allowed_values"));
  EXPECT_EQ(details["values"][0].As<std::string>(),
            "2020-08-01T21:50:00+00:00");
  EXPECT_EQ(details["values"][1].As<std::string>(),
            "2020-08-01T22:00:00+00:00");
  EXPECT_EQ(details["allowed_values"][0].As<std::string>(),
            "2020-08-01T22:00:00+00:00");
  EXPECT_EQ(details["allowed_values"][1].As<std::string>(),
            "2020-08-02T01:00:00+00:00");

  EXPECT_EQ(entries[2].amount, types::Numeric{10});
  EXPECT_EQ(entries[2].currency, "XXX");
  EXPECT_EQ(entries[2].timestamp, data_.validity.upper());
  EXPECT_EQ(entries[2].sub_account, "unfit/time/free_minutes");
  ASSERT_EQ(entries[2].match_info.size(), 1);
  EXPECT_FALSE(entries[2].match_info[0].matched);
  ASSERT_TRUE(entries[2].match_info[0].reason);
  EXPECT_EQ(entries[2].match_info[0].reason->code, "interval");
  EXPECT_EQ(entries[2].match_info[0].reason->type,
            models::match_info::Type::kIntersection);
  details = entries[2].match_info[0].reason->details;
  ASSERT_TRUE(details.HasMember("values"));
  ASSERT_TRUE(details.HasMember("allowed_values"));
  EXPECT_EQ(details["values"][0].As<std::string>(),
            "2020-08-02T01:00:00+00:00");
  EXPECT_EQ(details["values"][1].As<std::string>(),
            "2020-08-02T01:10:00+00:00");
  EXPECT_EQ(details["allowed_values"][0].As<std::string>(),
            "2020-08-01T22:00:00+00:00");
  EXPECT_EQ(details["allowed_values"][1].As<std::string>(),
            "2020-08-02T01:00:00+00:00");

  EXPECT_EQ(entries[3].amount, types::Numeric{180 * 6});
  EXPECT_EQ(entries[3].currency, "USD");
  EXPECT_EQ(entries[3].timestamp, data_.validity.lower());
  EXPECT_EQ(entries[3].sub_account, "guarantee");
  ASSERT_EQ(entries[3].match_info.size(), 1);
  EXPECT_TRUE(entries[3].match_info[0].matched);
  EXPECT_FALSE(entries[3].match_info[0].reason);
}
