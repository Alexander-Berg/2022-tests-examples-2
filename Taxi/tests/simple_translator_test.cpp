#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utest/parameter_names.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <grocery-localization/translators/simple.hpp>
#include <taxi_config/variables/GROCERY_LOCALIZATION_FALLBACK_LOCALES.hpp>
#include <taxi_config/variables/GROCERY_LOCALIZATION_TRANSLATION_FAILURE_LOG_LEVEL.hpp>

namespace grocery_l10n {

namespace {

dynamic_config::KeyValue CreateTranslationFailureLogLevelConfig(
    const std::string& failure_log_level) {
  return {taxi_config::GROCERY_LOCALIZATION_TRANSLATION_FAILURE_LOG_LEVEL,
          failure_log_level};
}

std::vector<dynamic_config::KeyValue> ToTranslationFailureLogLevel(
    const std::string& failure_log_level) {
  return {CreateTranslationFailureLogLevelConfig(failure_log_level)};
}

dynamic_config::KeyValue CreateFallbackLocalesConfig(
    const std::string& locale,
    const taxi_config::grocery_localization_fallback_locales::FallbackLocales&
        fallback_locales) {
  using namespace taxi_config::grocery_localization_fallback_locales;

  VariableType value{{locale, FallbackLocales{fallback_locales}}};
  return {taxi_config::GROCERY_LOCALIZATION_FALLBACK_LOCALES, std::move(value)};
}

std::vector<dynamic_config::KeyValue> ToFallbackLocales(
    const std::string& locale,
    const taxi_config::grocery_localization_fallback_locales::FallbackLocales&
        fallback_locales) {
  return {CreateFallbackLocalesConfig(locale, fallback_locales)};
}

models::Keyset MakeTestKeyset(const std::string& keyset_name,
                              const std::string& key, const std::string& locale,
                              models::PluralForm form,
                              const std::string& translation) {
  return models::Keyset{
      keyset_name, std::nullopt,
      models::KeysetTranslations{
          {key, models::Translations{{locale, {{form, translation}}}}}}};
};

class TranslatorContext {
 protected:
  TranslatorContext() : keysets_{}, storage_mock_{} {}

  void AddKeyset(const models::Keyset& keyset) {
    keysets_.insert({keyset.Name(), keyset});
  }

  std::shared_ptr<models::Keysets> KeysetsHandler() {
    return {&keysets_, [](auto*) {}};
  }

  void SetDefaultTranslationFailureLogLevel(
      const std::string& failure_log_level) {
    storage_mock_.Extend(ToTranslationFailureLogLevel(failure_log_level));
  }

  void SetDefaultTranslationFailureLogLevel() {
    SetDefaultTranslationFailureLogLevel(kDefaultFailureLogLevel);
  }

  void SetFallbackLocales(std::optional<std::string> locale,
                          const std::vector<std::string>& fallback_locales) {
    storage_mock_.Extend(ToFallbackLocales(
        locale.value_or(kConfigDictKeyByDefault), fallback_locales));
  }

  void SetDefaultFallbackLocales(
      const std::vector<std::string>& fallback_locales) {
    SetFallbackLocales(std::nullopt, fallback_locales);
  }

  void SetDefaultConfigs() {
    SetDefaultTranslationFailureLogLevel(kDefaultFailureLogLevel);
    SetDefaultFallbackLocales(kDefaultFallbackLocales);
  }

  dynamic_config::Snapshot ConfigSnapshot() const {
    return storage_mock_.GetSnapshot();
  }

 private:
  const std::string kConfigDictKeyByDefault = "__default__";
  const std::string kDefaultFailureLogLevel = "warning";
  const std::vector<std::string> kDefaultFallbackLocales{};

  models::Keysets keysets_;
  dynamic_config::StorageMock storage_mock_;
};

struct SmokeTestParams {
  std::string test_name;
  std::string keyset;
  std::string key;
  std::string locale;
  models::PluralForm form;
  std::string expected_translation;
  bool expect_translation;
  std::string source_value;
};

}  // namespace

class SimpleTranslatorSmokeTest
    : public ::testing::TestWithParam<SmokeTestParams>,
      protected TranslatorContext {};

const std::vector<SmokeTestParams> kSmokeTestParams = {
    {"HasTranslation", "keyset-1", "key-1", "ru", models::PluralForm::kOne,
     "translation", true, "translation"},
    {"MissingKeyset", "missing-keyset", "key-1", "ru", models::PluralForm::kOne,
     "translation", false, "translation"},
    {"MissingKey", "keyset-1", "missing-key", "ru", models::PluralForm::kOne,
     "translation", false, "translation"},
    {"MissingLocale", "keyset-1", "key-1", "en", models::PluralForm::kOne,
     "translation", false, "translation"},
    {"MissingFormFallback", "keyset-1", "key-1", "ru",
     models::PluralForm::kSome, "translation", true, "translation"},
    {"EmptyTranslation", "keyset-1", "key-1", "ru", models::PluralForm::kSome,
     "translation", false, ""}};

UTEST_P(SimpleTranslatorSmokeTest, TryTranslate) {
  const auto& param = GetParam();
  AddKeyset(MakeTestKeyset("keyset-1", "key-1", "ru", models::PluralForm::kOne,
                           param.source_value));
  SetDefaultConfigs();

  translators::Simple translator{KeysetsHandler(), ConfigSnapshot(),
                                 param.keyset, param.locale};
  const auto translated = translator.TryTranslate(
      param.key, models::template_type::AsIs{},
      models::plural_form_modificator_type::AsIs{param.form});

  ASSERT_TRUE(translated.has_value() == param.expect_translation);
  EXPECT_TRUE(!param.expect_translation ||
              translated.value() == param.expected_translation);
}

INSTANTIATE_UTEST_SUITE_P(/* prefix */, SimpleTranslatorSmokeTest,
                          ::testing::ValuesIn(kSmokeTestParams),
                          utest::PrintTestName());

struct FallbackLocalesTestParams {
  std::string test_name;
  std::optional<std::string> locale;
  std::optional<std::string> keyset;
  std::vector<std::string> fallback_locales;
  bool expect_translation;
};

class SimpleTranslatorFallbackLocalesTest
    : public ::testing::TestWithParam<FallbackLocalesTestParams>,
      protected TranslatorContext {};

const std::vector<FallbackLocalesTestParams> kFallbackLocalesTestParams = {
    {"Empty", {}, {}, {}, false},
    {"One", {}, {}, std::vector<std::string>{"en"}, true},
    {"Several", {}, {}, std::vector<std::string>{"fr", "en"}, true},
    {"ByLocale", {"ru"}, {}, std::vector<std::string>{"en"}, true}};

UTEST_P(SimpleTranslatorFallbackLocalesTest, TryTranslate) {
  AddKeyset(MakeTestKeyset("keyset-1", "key-1", "en", models::PluralForm::kOne,
                           "translation"));

  SetDefaultConfigs();

  const auto& param = GetParam();
  SetFallbackLocales(param.locale, param.fallback_locales);

  translators::Simple translator{KeysetsHandler(), ConfigSnapshot(), "keyset-1",
                                 "ru"};
  const auto translated = translator.TryTranslate("key-1");

  ASSERT_TRUE(translated.has_value() == param.expect_translation);
  EXPECT_TRUE(!param.expect_translation || translated.value() == "translation");
}

INSTANTIATE_UTEST_SUITE_P(/* prefix */, SimpleTranslatorFallbackLocalesTest,
                          ::testing::ValuesIn(kFallbackLocalesTestParams),
                          utest::PrintTestName());

struct PluralFormsTestParams {
  std::string test_name;
  std::string locale;
  models::PluralFormModificator plural_form_modificator;
  std::string translation;
};

class SimpleTranslatorPluralFormTest
    : public testing::TestWithParam<PluralFormsTestParams>,
      protected TranslatorContext {};

const std::vector<PluralFormsTestParams> kPluralFormsTestParams = {
    {"Resolve", "ru", models::plural_form_modificator_type::ByIntegerNumber{3},
     "метра"},
    {"FallbackForm", "ru",
     models::plural_form_modificator_type::ByIntegerNumber{6}, "метр"},
    {"FallbackLocale", "fr",
     models::plural_form_modificator_type::ByIntegerNumber{6}, "meters"}};

UTEST_P(SimpleTranslatorPluralFormTest, TryTranslate) {
  const std::string keyset = "amount_units";
  const std::string key = "meter";
  AddKeyset(models::Keyset{
      keyset, std::nullopt,
      models::KeysetTranslations{
          {key,
           models::Translations{{"ru",
                                 {{models::PluralForm::kOne, "метр"},
                                  {models::PluralForm::kSome, "метра"},
                                  {models::PluralForm::kNone, "метров"}}},
                                {"en",
                                 {{models::PluralForm::kOne, "meter"},
                                  {models::PluralForm::kMany, "meters"}}},
                                {"he",
                                 {{models::PluralForm::kOne, "מטר"},
                                  {models::PluralForm::kMany, "מטרים"}}}}}}});
  SetDefaultConfigs();
  SetDefaultFallbackLocales({"en"});

  const auto param = GetParam();
  translators::Simple translator{KeysetsHandler(), ConfigSnapshot(), keyset,
                                 param.locale};
  const auto translated = translator.TryTranslate(
      key, models::template_type::AsIs{}, param.plural_form_modificator);
  ASSERT_TRUE(translated.has_value());
  EXPECT_EQ(translated.value(), param.translation);
}

INSTANTIATE_UTEST_SUITE_P(/* prefix */, SimpleTranslatorPluralFormTest,
                          ::testing::ValuesIn(kPluralFormsTestParams),
                          utest::PrintTestName());

class SimpleTranslatorApplyTemplateSubstitutionTest
    : public testing::Test,
      protected TranslatorContext {};

UTEST_F(SimpleTranslatorApplyTemplateSubstitutionTest, TryTranslate) {
  const std::string string_template = "Delivery from {from} till {till}.";
  AddKeyset(MakeTestKeyset("showcase", "delivery", "en",
                           models::PluralForm::kOne, string_template));
  SetDefaultConfigs();
  translators::Simple translator{KeysetsHandler(), ConfigSnapshot(), "showcase",
                                 "en"};

  const simple_template::ArgsList args{{"from", "7:00"}, {"till", "23:00"}};
  const auto translated = translator.TryTranslate(
      "delivery", models::template_type::SimpleTemplate{args});

  ASSERT_TRUE(translated.has_value());
  EXPECT_EQ(translated.value(), "Delivery from 7:00 till 23:00.");
}

}  // namespace grocery_l10n
