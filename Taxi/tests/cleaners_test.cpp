#include <userver/utest/utest.hpp>

#include <optional>

#include <taxi_config/taxi_config.hpp>

#include "constants.hpp"
#include "utils/cleaners.hpp"

namespace ivr_dispatcher::unit_tests {

class NormalizeCarNumber : public ::testing::Test {
 protected:
  virtual void SetUp() {
    taxi_config::ivr_car_number_formatting_rules::OutputSettings rus_output;
    rus_output.sms = "$2";
    rus_output.call = "$2";
    taxi_config::ivr_car_number_formatting_rules::FormattingRule rus_rule{
        "^(\\D)(\\d{3})(\\D{2})(\\d{2,3})$", rus_output, false};
    taxi_config::ivr_car_number_formatting_rules::CountryFormattingRules
        rus_rules;
    rus_rules.push_back(rus_rule);
    ::std::unordered_map<
        std::string,
        ::std::vector<
            taxi_config::ivr_car_number_formatting_rules::FormattingRule>>
        extra;
    extra["rus"] = rus_rules;
    rules.extra = extra;
  }
  taxi_config::ivr_car_number_formatting_rules::IvrCarNumberFormattingRules
      rules;
};

class LowerCarNumber : public ::testing::Test {
 protected:
  virtual void SetUp() {
    taxi_config::ivr_car_number_formatting_rules::OutputSettings rus_output;
    rus_output.sms = "$1 $2 $3 $4";
    rus_output.call = "$1 $2 $3 $4";
    taxi_config::ivr_car_number_formatting_rules::FormattingRule rus_rule{
        "^(\\D)(\\d{3})(\\D{2})(\\d{2,3})$", rus_output, true};
    taxi_config::ivr_car_number_formatting_rules::CountryFormattingRules
        rus_rules;
    rus_rules.push_back(rus_rule);
    ::std::unordered_map<
        std::string,
        ::std::vector<
            taxi_config::ivr_car_number_formatting_rules::FormattingRule>>
        extra;
    extra["rus"] = rus_rules;
    rules.extra = extra;
  }
  taxi_config::ivr_car_number_formatting_rules::IvrCarNumberFormattingRules
      rules;
};

// Normalize phone
TEST(NormalizePhone, WithAlphas) {
  ASSERT_EQ(ivr_dispatcher::utils::NormalizePhone("a123"),
            std::make_optional("+123"));
}
TEST(NormalizePhone, OnlyAlphas) {
  ASSERT_EQ(ivr_dispatcher::utils::NormalizePhone("abc"), std::nullopt);
}
TEST(NormalizePhone, Change8) {
  ASSERT_EQ(ivr_dispatcher::utils::NormalizePhone("89152223344"),
            std::make_optional("+79152223344"));
}

// Split big integers
TEST(SplitBigIntegers, SplitMiddleTokenNoBorders) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("AH1236GH23", false),
            "AH1 2 3 6GH23");
}
TEST(SplitBigIntegers, SplitMiddleTokenWithBorders) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("AH1236GH23", true),
            "AH 1 2 3 6 GH23");
}

TEST(SplitBigIntegers, SplitMiddleAloneShortTokenNoBorders) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("23", false), "23");
}
TEST(SplitBigIntegers, SplitMiddleAloneShortTokenWithBorders) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("23", true), "23");
}

TEST(SplitBigIntegers, SplitMiddleAloneLongTokenNoBorders) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("2356", false), "2 3 5 6");
}
TEST(SplitBigIntegers, SplitMiddleAloneLongTokenWithBorders) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("2356", true), " 2 3 5 6 ");
}

TEST(SplitBigIntegers, SplitRightToken) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("asd2356", false),
            "asd2 3 5 6");
}
TEST(SplitBigIntegers, SplitLeftToken) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("2356asd", false),
            "2 3 5 6asd");
}

TEST(SplitBigIntegers, SplitRightTokenWithBorders) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("asd2356", true),
            "asd 2 3 5 6 ");
}
TEST(SplitBigIntegers, SplitLeftTokenWithBorders) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("2356asd", true),
            " 2 3 5 6 asd");
}

TEST(SplitBigIntegers, SplitVeryShort) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("1", false), "1");
}
TEST(SplitBigIntegers, SplitVeryShortWithBorders) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("1", true), "1");
}

TEST(SplitBigIntegers, EmptyString1) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("", true), "");
}
TEST(SplitBigIntegers, EmptyString2) {
  ASSERT_EQ(ivr_dispatcher::utils::SplitBigIntegers("", false), "");
}

// Hide car number parts
TEST(HideCarNumber, Short) {
  ASSERT_EQ(ivr_dispatcher::utils::HideCarNumber("1234"), "***");
}
TEST(HideCarNumber, Long) {
  ASSERT_EQ(ivr_dispatcher::utils::HideCarNumber("1234456"), "**344**");
}

// Normalize car number
TEST_F(NormalizeCarNumber, WithoutSettings) {
  ASSERT_EQ(
      ivr_dispatcher::utils::NormalizeCarNumber("A123BE23", "blr", {}, false),
      "A123BE23");
}

TEST_F(NormalizeCarNumber, WithSettings) {
  ASSERT_EQ(ivr_dispatcher::utils::NormalizeCarNumber("A123BE23", "rus", rules,
                                                      false),
            "123");
}
TEST_F(NormalizeCarNumber, WithoutSutableRule) {
  ASSERT_EQ(
      ivr_dispatcher::utils::NormalizeCarNumber("A123", "rus", rules, false),
      "A123");
}

TEST_F(LowerCarNumber, True) {
  ASSERT_EQ(
      ivr_dispatcher::utils::NormalizeCarNumber("A123BE23", "rus", rules, true),
      "a 123 be 23");
}

TEST_F(LowerCarNumber, False) {
  // don't use lower in call texts
  ASSERT_EQ(ivr_dispatcher::utils::NormalizeCarNumber("A123BE23", "rus", rules,
                                                      false),
            "A 123 BE 23");
}

}  // namespace ivr_dispatcher::unit_tests
