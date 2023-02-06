#include <gtest/gtest.h>

#include <string>

#include <views/driver_polling_subventions_status.cpp>

#include <clients/billing_subventions.hpp>
#include <models/driver/payment_type.hpp>
#include <utils/helpers/json.hpp>

namespace ss = views::driver_polling_subventions_status;
namespace bs = clients::billing_subventions;

static constexpr auto kRuleTemplateBegin = R"JSON({
    "tariff_zones": [
        "moscow"
    ],
    "status": "enabled",
    "start": "2019-01-10T21:00:00.000000+00:00",
    "end": "2019-05-29T21:00:00.000000+00:00",
    "type": "geo_booking",
    "is_personal": false,
    "taxirate": "",
    "subvention_rule_id": "geo_booking_rule1",
    "cursor": "2019-05-29T21:00:00.000000+00:00/5c4ecf2aca0d42561986b84f",
    "week_days": [
    ],
    "geoareas": [
        "msk-big"
    ],
    "tags": [
    ],
    "time_zone": {
        "id": "Asia/Yekaterinburg",
        "offset": "+05:00"
    },
    "visible_to_driver": true,
    "workshift": {
        "start": "10:00",
        "end": "17:00"
    },
    "min_activity_points": 10,
    "min_online_minutes": 10,
    "rate_on_order_per_minute": "5",
    "rate_free_per_minute": "10",
    "currency": "RUB",
    "hours": [
        1,
        2
    ],
    "profile_payment_type_restrictions": ")JSON";

static constexpr auto kRuleTemplateEnd = "\"\n}";

Json::Value ReadJson(const std::string& json) {
  Json::Value doc;
  if (!utils::helpers::TryParseJson(json, doc, {})) {
    throw utils::helpers::JsonMemberTypeError("Failed to parse json ");
  }
  return doc;
}

struct Param {
  std::string billing_payment;
  std::string driver_payment;
  bool expected_result;
};

class SubventionStatusPaymentCheck : public ::testing::TestWithParam<Param> {};

TEST_P(SubventionStatusPaymentCheck, Test) {
  const auto& param = GetParam();
  const auto& doc =
      ReadJson(kRuleTemplateBegin + param.billing_payment + kRuleTemplateEnd);
  std::shared_ptr<bs::GeoBookingSubvention> rule;
  ASSERT_NO_THROW(
      rule = std::make_shared<bs::GeoBookingSubvention>(doc, LogExtra()));

  ASSERT_EQ(ss::IsSatisfiedPaymentType(*rule, param.driver_payment),
            param.expected_result);
}

using namespace views::driver_polling_subventions_status;

INSTANTIATE_TEST_CASE_P(
    , SubventionStatusPaymentCheck,
    ::testing::Values(Param{"none", payment_type::kNone, true},
                      Param{"online", payment_type::kNone, true},
                      Param{"cash", payment_type::kNone, true},
                      Param{"any", payment_type::kNone, true},
                      Param{"none", payment_type::kCash, false},
                      Param{"online", payment_type::kCash, false},
                      Param{"cash", payment_type::kCash, true},
                      Param{"any", payment_type::kCash, true},
                      Param{"none", payment_type::kOnline, false},
                      Param{"online", payment_type::kOnline, true},
                      Param{"cash", payment_type::kOnline, false},
                      Param{"any", payment_type::kOnline, true}),
    /**/);
