
#include <fmt/format.h>

#include <userver/utest/utest.hpp>

#include <string>

#include <json-diff/json_diff.hpp>

#include <logics/cancel_rules.hpp>

namespace logics::cancel_rules {

std::optional<std::string> GetTextKey(double cancel_cost,
                                      const std::string& taxi_status,
                                      const std::string& payment_type);

std::string GetTitleKey(const std::string& taxi_status);

const auto kMapForTextTankerKey =
    std::map<std::string, std::optional<std::string>>{
        {"search.free.cash", "cancel_rules.text.search.free"},
        {"search.free.card", "cancel_rules.text.search.free"},

        {"driving.free.cash", "cancel_rules.text.driving.free"},
        {"driving.free.card", "cancel_rules.text.driving.free"},
        {"driving.paid.cash", "cancel_rules.text.driving.paid.cash"},
        {"driving.paid.card", "cancel_rules.text.driving.paid.not_cash"},

        {"waiting.free.cash", "cancel_rules.text.waiting.free"},
        {"waiting.free.card", "cancel_rules.text.waiting.free"},
        {"waiting.paid.cash", "cancel_rules.text.waiting.paid.cash"},
        {"waiting.paid.card", "cancel_rules.text.waiting.paid.not_cash"},

        // There are no texts to cancel in 'transporting'
        {"transporting.free.cash", std::nullopt},
        {"transporting.free.card", std::nullopt},
        {"transporting.paid.cash", std::nullopt},
        {"transporting.paid.card", std::nullopt},

        // Strange situation
        {"search.paid.cash", std::nullopt},
        {"search.paid.card", std::nullopt},
    };

TEST(CancelRules, TitleKeyDefault) {
  const auto& res = GetTitleKey("random_status");
  ASSERT_EQ(res, "cancel_rules.title.default");
}

TEST(CancelRules, TitleKeyDriving) {
  const auto& res = GetTitleKey("driving");
  ASSERT_EQ(res, "cancel_rules.title.driving");
}

TEST(CancelRules, TitleKeyWaiting) {
  const auto& res = GetTitleKey("waiting");
  ASSERT_EQ(res, "cancel_rules.title.waiting");
}

TEST(CancelRules, TextKeys) {
  const std::vector<std::pair<double, std::string>> costs = {
      {0.0, "free"},
      {199.0, "paid"},
  };
  const auto payments = {"cash", "card"};
  const auto taxi_statuses = {"search", "driving", "waiting", "transporting"};

  for (const auto& [cost, cost_str] : costs) {
    for (const auto& payment_type : payments) {
      for (const auto& taxi_status : taxi_statuses) {
        const auto& key =
            fmt::format("{}.{}.{}", taxi_status, cost_str, payment_type);

        const auto& value = GetTextKey(cost, taxi_status, payment_type);
        const auto& expected_value = kMapForTextTankerKey.at(key);
        EXPECT_PRED_FORMAT2(json_diff::AreValuesEqual, value, expected_value);
      }
    }
  }
}

}  // namespace logics::cancel_rules
