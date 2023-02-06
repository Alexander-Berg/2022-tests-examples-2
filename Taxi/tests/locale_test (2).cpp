#include <userver/utest/utest.hpp>

#include <types/locale.hpp>

namespace testing {
using ::eats_restapp_communications::types::locale::LocaleSettings;
using ConfigLocaleSettings =
    ::taxi_config::eats_restapp_communications_locale_settings::
        EatsRestappCommunicationsLocaleSettings;

struct LocaleSettingsFixture {
  LocaleSettings settings;
  LocaleSettingsFixture()
      : settings(ConfigLocaleSettings{"ru", {{"BY", "by"}, {"TR", "en"}}}) {}
};

using LocaleMapTestParams = std::tuple<std::string, std::string>;

struct LocaleMapTest : public LocaleSettingsFixture,
                       public TestWithParam<LocaleMapTestParams> {};

INSTANTIATE_TEST_SUITE_P(LocaleMapTest, LocaleMapTest,
                         Values(LocaleMapTestParams{"BY", "by"},
                                LocaleMapTestParams{"TR", "en"},
                                LocaleMapTestParams{"QQ", "ru"}));

TEST_P(LocaleMapTest, should_return_locale_by_country_code) {
  const auto [country_code, expected] = GetParam();
  ASSERT_EQ(settings.GetLocale(country_code), expected);
}
}  // namespace testing
