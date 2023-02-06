#include <gtest/gtest.h>
#include <json/json.h>
#include <utils/translation_mock.hpp>

std::string BuildMessage(const l10n::Translations& translations,
                         const std::string& project,
                         const std::string& tanker_key) {
  return translations.getTemplate(project, tanker_key, "en").Original();
}

TEST(TranslationTest, BuildTranslationMessages) {
  MockTranslations translations(true);
  EXPECT_EQ(
      "You need to be at least {1} meters closer to the pickup point "
      "before you can change your status",
      BuildMessage(translations, "taximeter_backend_driver_messages",
                   "alert_warning_wait"));
  EXPECT_EQ("{1} of {2}",
            BuildMessage(translations, "taximeter_driver_messages",
                         "full_work_index"));
  EXPECT_EQ(
      "workdays from {from} to {to}",
      BuildMessage(translations, "tariff", "workday_interval_description"));
}
