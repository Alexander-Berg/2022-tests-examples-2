#include <boost/lexical_cast.hpp>
#include <boost/uuid/uuid_io.hpp>
#include <models/rule/rule.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

class MoreSpecificRule
    : public testing::TestWithParam<std::tuple<
          std::tuple<std::optional<std::string>, std::optional<std::string>,
                     std::optional<std::string>, std::optional<std::string>>,
          std::tuple<std::optional<std::string>, std::optional<std::string>,
                     std::optional<std::string>, std::optional<std::string>>,
          int>> {};

TEST_P(MoreSpecificRule, Test) {
  auto tp = ::utils::datetime::Stringtime("2019-12-16 23:35:00",
                                          "Europe/Moscow", "%Y-%m-%d %H:%M:%S");
  utils::datetime::MockNowSet(tp);
  auto uuid_left = boost::lexical_cast<boost::uuids::uuid>(
      "1cb1263b-6341-4182-b500-d646621ccf9d");
  auto uuid_right = boost::lexical_cast<boost::uuids::uuid>(
      "2cb1263b-6341-4182-b500-d646621ccf9d");
  const auto [rule_left_opt, rule_right_opt, result] = GetParam();
  models::rule::Rule rule_left{uuid_left,
                               "test",
                               std::get<0>(rule_left_opt).value(),
                               std::get<1>(rule_left_opt).value_or(""),
                               tp,
                               std::nullopt,
                               std::nullopt,
                               std::shared_ptr<models::rule::Fees>{},
                               std::get<3>(rule_left_opt),
                               std::get<2>(rule_left_opt),
                               models::category::Category{},
                               models::rule::Options{},
                               std::nullopt,
                               std::nullopt};
  models::rule::Rule rule_right{uuid_right,
                                "test",
                                std::get<0>(rule_right_opt).value(),
                                std::get<1>(rule_right_opt).value_or(""),
                                tp,
                                std::nullopt,
                                std::nullopt,
                                std::shared_ptr<models::rule::Fees>{},
                                std::get<3>(rule_right_opt),
                                std::get<2>(rule_right_opt),
                                models::category::Category{},
                                models::rule::Options{},
                                std::nullopt,
                                std::nullopt};
  ASSERT_EQ(rule_left.Compare(rule_right), result);
}

INSTANTIATE_TEST_SUITE_P(
    MoreSpecificRuleBase, MoreSpecificRule,
    ::testing::Values(
        std::make_tuple(
            std::make_tuple("msk", "econom", std::nullopt, "tag"),
            std::make_tuple("msk", "econom", std::nullopt, std::nullopt), 1),
        std::make_tuple(
            std::make_tuple("msk", "econom", std::nullopt, std::nullopt),
            std::make_tuple("msk", "econom", std::nullopt, "tag"), -1),
        std::make_tuple(std::make_tuple("msk", "econom", "cash", std::nullopt),
                        std::make_tuple("msk", "econom", std::nullopt, "tag"),
                        1),
        std::make_tuple(std::make_tuple("msk", "econom", "cash", "t"),
                        std::make_tuple("msk", "econom", std::nullopt, "tag"),
                        1),
        std::make_tuple(std::make_tuple("msk", "econom", "cash", "t"),
                        std::make_tuple("msk", "econom", std::nullopt, "tag"),
                        1),
        std::make_tuple(std::make_tuple("msk", "suv", "corp", std::nullopt),
                        std::make_tuple("msk", "", "corp",
                                        "reposition_rollout_extracoms_9"),
                        1),
        std::make_tuple(std::make_tuple("msk", "suv", "corp", std::nullopt),
                        std::make_tuple("msk", "sub", "corp",
                                        "reposition_rollout_extracoms_9"),
                        -1),
        std::make_tuple(std::make_tuple("msk", "suv", "corp",
                                        "reposition_rollout_extracoms_9"),
                        std::make_tuple("msk", "suv", "corp", std::nullopt), 1),
        std::make_tuple(std::make_tuple("msk", "suv", "corp",
                                        "reposition_rollout_extracoms_9"),
                        std::make_tuple("msk", "suv", "corp",
                                        "reposition_rollout_extracoms_9"),
                        0),
        std::make_tuple(std::make_tuple("msk", "suv", "corp", std::nullopt),
                        std::make_tuple("msk", "suv", "corp", std::nullopt),
                        0)));
