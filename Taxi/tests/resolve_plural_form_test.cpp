#include <userver/utest/parameter_names.hpp>
#include <userver/utest/utest.hpp>
#include <utils/resolve_plural_form.hpp>

namespace grocery_l10n {

using ByNumericNumber = models::plural_form_modificator_type::ByNumericNumber;
using ByIntegerNumber = models::plural_form_modificator_type::ByIntegerNumber;
using Numeric = grocery_pricing::Numeric;

TEST(ResolvePluralFormTest, AsIs) {
  const std::vector<std::string> locales{"en", "he", "ru", "fr", "unknown"};
  const std::vector<models::PluralForm> plural_forms{
      models::PluralForm::kOne, models::PluralForm::kSome,
      models::PluralForm::kMany, models::PluralForm::kNone};

  for (const auto& locale : locales) {
    for (auto plural_form : plural_forms) {
      EXPECT_EQ(
          utils::ResolvePluralForm(
              locale, models::plural_form_modificator_type::AsIs{plural_form}),
          plural_form);
    }
  }
}

struct ResolvePluralFormTestParams {
  std::string test_name;
  std::string locale;
  std::vector<models::PluralFormModificator> plural_form_modificators;
  models::PluralForm expected_plural_form;
};

class ResolvePluralFormParamTest
    : public ::testing::TestWithParam<ResolvePluralFormTestParams> {};

class ResolvePluralFromByNumericNumberTest : public ResolvePluralFormParamTest {
};

const std::vector<ResolvePluralFormTestParams>
    kResolvePluralFormByNumericNumberParams{
        {"RU_Some",
         "ru",
         {ByNumericNumber{Numeric::FromFloatInexact(0.0)},
          ByNumericNumber{Numeric::FromFloatInexact(0.1)},
          ByNumericNumber{Numeric::FromFloatInexact(1.0)},
          ByNumericNumber{Numeric::FromFloatInexact(1.1)},
          ByNumericNumber{Numeric::FromFloatInexact(10.7)}},
         models::PluralForm::kSome},
        {"EN_Many",
         "en",
         {ByNumericNumber{Numeric::FromFloatInexact(0.0)},
          ByNumericNumber{Numeric::FromFloatInexact(0.1)},
          ByNumericNumber{Numeric::FromFloatInexact(1.0)},
          ByNumericNumber{Numeric::FromFloatInexact(1.1)},
          ByNumericNumber{Numeric::FromFloatInexact(10.7)}},
         models::PluralForm::kMany},
        {"FR_One",
         "fr",
         {ByNumericNumber{Numeric::FromFloatInexact(0.0)},
          ByNumericNumber{Numeric::FromFloatInexact(0.1)},
          ByNumericNumber{Numeric::FromFloatInexact(1.0)},
          ByNumericNumber{Numeric::FromFloatInexact(1.1)}},
         models::PluralForm::kOne},
        {"FR_Many",
         "fr",
         {ByNumericNumber{Numeric::FromFloatInexact(2.0)},
          ByNumericNumber{Numeric::FromFloatInexact(10.7)}},
         models::PluralForm::kMany},
        {"HE_One",
         "he",
         {ByNumericNumber{Numeric::FromFloatInexact(0.0)},
          ByNumericNumber{Numeric::FromFloatInexact(0.1)},
          ByNumericNumber{Numeric::FromFloatInexact(1.0)}},
         models::PluralForm::kOne},
        {"HE_Many",
         "he",
         {ByNumericNumber{Numeric::FromFloatInexact(1.1)},
          ByNumericNumber{Numeric::FromFloatInexact(10.7)}},
         models::PluralForm::kMany}};

TEST_P(ResolvePluralFromByNumericNumberTest, ResolvePluralForm) {
  const auto& param = GetParam();
  for (const auto& plural_form_modificator : param.plural_form_modificators) {
    EXPECT_EQ(utils::ResolvePluralForm(param.locale, plural_form_modificator),
              param.expected_plural_form);
  }
}

INSTANTIATE_TEST_SUITE_P(
    /* prefix */, ResolvePluralFromByNumericNumberTest,
    ::testing::ValuesIn(kResolvePluralFormByNumericNumberParams),
    utest::PrintTestName());

class ResolvePluralFromByIntegerNumberTest : public ResolvePluralFormParamTest {
};

const std::vector<ResolvePluralFormTestParams>
    kResolvePluralFormByIntegerNumberParams{
        {"RU_One",
         "ru",
         {ByIntegerNumber{1}, ByIntegerNumber{21}, ByIntegerNumber{101}},
         models::PluralForm::kOne},
        {"RU_Some",
         "ru",
         {ByIntegerNumber{2}, ByIntegerNumber{3}, ByIntegerNumber{4},
          ByIntegerNumber{22}, ByIntegerNumber{33}, ByIntegerNumber{44}},
         models::PluralForm::kSome},
        {"RU_Many",
         "ru",
         {ByIntegerNumber{0}, ByIntegerNumber{5}, ByIntegerNumber{9},
          ByIntegerNumber{11}, ByIntegerNumber{12}, ByIntegerNumber{13},
          ByIntegerNumber{100}},
         models::PluralForm::kMany},
        {"EN_One", "en", {ByIntegerNumber{1}}, models::PluralForm::kOne},
        {"EN_Many",
         "en",
         {ByIntegerNumber{0}, ByIntegerNumber{2}, ByIntegerNumber{3},
          ByIntegerNumber{10}, ByIntegerNumber{100}},
         models::PluralForm::kMany},
        {"HE_One", "he", {ByIntegerNumber{1}}, models::PluralForm::kOne},
        {"HE_Many",
         "he",
         {ByIntegerNumber{0}, ByIntegerNumber{2}, ByIntegerNumber{3},
          ByIntegerNumber{10}, ByIntegerNumber{100}},
         models::PluralForm::kMany},
        {"FR_One",
         "fr",
         {ByIntegerNumber{0}, ByIntegerNumber{1}},
         models::PluralForm::kOne},
        {"FR_Many",
         "fr",
         {ByIntegerNumber{2}, ByIntegerNumber{3}, ByIntegerNumber{10},
          ByIntegerNumber{100}},
         models::PluralForm::kMany}};

TEST_P(ResolvePluralFromByIntegerNumberTest, ResolvePluralForm) {
  const auto& param = GetParam();
  for (const auto& plural_form_modificator : param.plural_form_modificators) {
    EXPECT_EQ(utils::ResolvePluralForm(param.locale, plural_form_modificator),
              param.expected_plural_form);
  }
}

INSTANTIATE_TEST_SUITE_P(
    /* prefix */, ResolvePluralFromByIntegerNumberTest,
    ::testing::ValuesIn(kResolvePluralFormByIntegerNumberParams),
    utest::PrintTestName());

}  // namespace grocery_l10n
