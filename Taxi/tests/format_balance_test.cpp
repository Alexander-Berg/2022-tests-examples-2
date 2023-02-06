#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/assert.hpp>

#include <l10n/l10n_override.hpp>

#include <bank-localization/bank-localization.hpp>

// mocked localization

class TestTranslations : public l10n::Translations {
 public:
  TestTranslations(const std::unordered_map<
                   std::string, std::unordered_map<std::string, std::string>>&
                       translations)
      : translations_(translations){};

  std::string GetWithArgs([[maybe_unused]] const std::string& keyset,
                          [[maybe_unused]] const std::string& key,
                          [[maybe_unused]] const std::string& locale,
                          [[maybe_unused]] const l10n::ArgsList& args,
                          [[maybe_unused]] int count = 1,
                          [[maybe_unused]] const std::string& fallback_locale =
                              l10n::locales::kRussian) const final {
    return Get(keyset, key, locale, count, fallback_locale);
  }

  std::string Get([[maybe_unused]] const std::string& keyset,
                  [[maybe_unused]] const std::string& key,
                  [[maybe_unused]] const std::string& locale,
                  [[maybe_unused]] const int count = 1,
                  [[maybe_unused]] const std::string& fallback_locale =
                      l10n::locales::kRussian) const final {
    EXPECT_EQ(keyset, "bank_backend");
    const auto& key_translations = translations_.at(key);
    const auto& translations_it = key_translations.find(locale);
    if (translations_it != key_translations.end()) {
      return translations_it->second;
    }
    return translations_.at(key).at(fallback_locale);
  }

  const simple_template::TextTemplate& GetTemplate(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& key,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] const int count = 1,
      [[maybe_unused]] const std::string& fallback_locale =
          l10n::locales::kRussian) const final {
    UINVARIANT(false, "Not implemented");
    static simple_template::TextTemplate test("test");
    return test;
  }
  std::optional<std::string> GetOptional(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& key,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] int count = 1,
      [[maybe_unused]] const std::string& fallback_locale =
          l10n::locales::kRussian) const final {
    return Get(keyset, key, locale, count, fallback_locale);
  }
  const simple_template::TextTemplate* GetTemplateOptional(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& key,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] int count = 1,
      [[maybe_unused]] const std::string& fallback_locale =
          l10n::locales::kRussian) const final {
    UINVARIANT(false, "Not implemented");
    return nullptr;
  }
  std::unordered_map<std::string, std::string> GetAllMappings(
      [[maybe_unused]] const std::string& keyset,
      [[maybe_unused]] const std::string& locale,
      [[maybe_unused]] const std::vector<std::string>& fallback_locales,
      [[maybe_unused]] bool use_all_fallbacks) const final {
    return {};
  };

  std::optional<l10n::KeysetWrapper> GetKeysetOptional(
      const std::string& keyset, const std::string& fallback_locale =
                                     l10n::locales::kDefault) const final {
    return l10n::KeysetWrapper(keyset, fallback_locale, *this);
  }

  size_t GetSize() const { return 1; }

 private:
  std::unordered_map<std::string, std::unordered_map<std::string, std::string>>
      translations_;
};

UTEST(BankFormatterImplTest, FormatAmount) {
  auto translations =
      TestTranslations({{"localization.system_locales",
                         {{"ru", "ru_RU.UTF-8"}, {"en", "en_US.UTF-8"}}},
                        {"localization.templates",
                         {{"ru", "$VALUE$ $SIGN$$CURRENCY$"},
                          {"en", "$SIGN$$CURRENCY$ $VALUE$"}}}});

  dynamic_config::StorageMock config_storage{
      {{taxi_config::BANK_LOCALIZATION_CURRENCY_SIGNS,
        {{{"EUR", "€"}, {"RUB", "\u20BD"}, {"USD", "$"}}}}}};

  auto config = config_storage.GetSnapshot();
  auto formatter =
      bank_localization::BalanceFormatter(translations, config, "ru");

  EXPECT_EQ(formatter.FormatBalance("423.34", "USD"), "423,34 $");
  EXPECT_EQ(formatter.FormatBalance("10000.34", "RUB"), "10 000,34 ₽");
  EXPECT_EQ(formatter.FormatBalance("-0.04", "RUB", 1), "0 ₽");
  EXPECT_EQ(formatter.FormatBalance("-0.05", "RUB", 1), "\u22120,1 ₽");
  EXPECT_EQ(formatter.FormatBalance(
                "-0.05", "RUB", 1, false,
                bank_localization::CurrencyRepresentation::kCurrency),
            "\u22120,1 RUB");
  EXPECT_EQ(bank_localization::FormatBalance(translations, config, "ka",
                                             "4230.34", "USD"),
            "4230,34 $");
  EXPECT_EQ(bank_localization::FormatBalance(translations, config, "en",
                                             "423000.34", "EUR"),
            "€ 423,000.34");

  EXPECT_THROW(bank_localization::FormatBalance(translations, config, "en",
                                                "423000.34", "BAD"),
               std::runtime_error);

  auto bad_translations = TestTranslations({});
  EXPECT_THROW(bank_localization::FormatBalance(bad_translations,
                                                config_storage.GetSnapshot(),
                                                "ka", "423.34", "USD"),
               std::out_of_range);
}
