#include <gtest/gtest.h>
#include <utility>

#include <taxi_config/taxi_config.hpp>
#include <utils/validator.hpp>

using namespace localizations_replica::validator;
using namespace localizations_replica::models;

using Keysets = std::unordered_map<std::string, KeysetTranslations>;
using KeysetsList = std::vector<Keysets>;
using KeysetsStatusList = std::vector<std::pair<Keysets, KeysetInfoError>>;

TEST(TestValidator, TestStopwordSuccess) {
  ValidatorContext context{};

  taxi_config::locales_application_type_overrides::VersionOverrideSettings
      version_settings{};
  version_settings.override_keysets.extra = {{"geoareas", "ignore"},
                                             {"notify", "override_az"}};
  version_settings.supported_languages = {"en", "ru"};

  const std::unordered_set<std::string> stop_words_lowered{
      "яндекс", "яндекс.Такси", "я.такси", "yandex", "yandeks"};

  // clang-format off
  context.SetOverrideTranslations(
    {
      {
        {
          "override_az", {
            {
              "moscow", {
                {"ru", {{1, "Priehal Uber"}}},
                {"en", {{1, "Uber has arrived"}}},
                {"fr", {{1, "Yandeks has arrived"}}}, // contains stop word but is not supported language
              }
            } //, other key
          }
        } //, other keyset
      }
    }
  );

  KeysetsList keysets(
    {
      {
        {
          "geoareas", { // 'geoareas' is ignoring
            {
              "moscow", {
                {"ru", {{1, "Yandex"}}},
                {"en", {{1, "Yandex"}}},
              }
            } //, other key
          }
        },
        {
          "notify", {  //'notify' is overriding on override_az
            {
              "moscow", {
                {"ru", {{1, "Priehal Yandeks"}}},
                {"en", {{1, "Yandex has arrived"}}},
              }
            } //, other key
          }
        }, //, other keyset
      }
    }
  );
  // clang-format on

  context.SetPlaceholderStrictMode(false);
  for (const auto& keyset : keysets) {
    for (const auto& [keyset_name, translations] : keyset) {
      context.SetKeysetName(keyset_name);

      EXPECT_NO_THROW(RunCheckKeyset(translations, context));
      EXPECT_NO_THROW(CheckKeysetsStopwordsFree(
          translations, "az", version_settings, stop_words_lowered, context));
    }
  }

  context.SetPlaceholderStrictMode(true);
  for (const auto& keyset : keysets) {
    for (const auto& [keyset_name, translations] : keyset) {
      context.SetKeysetName(keyset_name);

      EXPECT_NO_THROW(RunCheckKeyset(translations, context));
      EXPECT_NO_THROW(CheckKeysetsStopwordsFree(
          translations, "az", version_settings, stop_words_lowered, context));
    }
  }
}

// Test that keys with stopwords without an alternative are prohibited
TEST(TestValidator, TestStopwordErrorNoAlternative) {
  ValidatorContext context{};

  taxi_config::locales_application_type_overrides::VersionOverrideSettings
      version_settings{};
  version_settings.override_keysets.extra = {{"geoareas", "ignore"},
                                             {"notify", "override_az"}};
  version_settings.supported_languages = {"en", "ru"};

  const std::unordered_set<std::string> stop_words_lowered{"yandex", "yandeks"};

  // clang-format off
  context.SetOverrideTranslations(
    {
      {
        {
          "override_az", {
            {
            } //, other key
          }
        } //, other keyset
      }
    }
  ); // empty override

  KeysetTranslations translation(
    {
      {
        "moscow", {
          {"ru", {{1, "Priehal Yandeks"}}},
          {"en", {{1, "Yandex has arrived"}}},
        }
      }
    }
  );
  // clang-format on

  context.SetKeysetName("notify");
  context.SetPlaceholderStrictMode(true);
  EXPECT_THROW(CheckKeysetsStopwordsFree(translation, "az", version_settings,
                                         stop_words_lowered, context),
               StopwordsValidationError);
  context.SetPlaceholderStrictMode(true);
  EXPECT_THROW(CheckKeysetsStopwordsFree(translation, "az", version_settings,
                                         stop_words_lowered, context),
               StopwordsValidationError);
}

// Test that keys with stopwords that have an alternative _with_
// stopwords are prohibited
TEST(TestValidator, TestStopwordErrorAlternative) {
  ValidatorContext context{};

  taxi_config::locales_application_type_overrides::VersionOverrideSettings
      version_settings{};
  version_settings.override_keysets.extra = {{"geoareas", "ignore"},
                                             {"notify", "override_az"}};
  version_settings.supported_languages = {"en", "ru"};

  const std::unordered_set<std::string> stop_words_lowered{"yandex", "yandeks"};

  // clang-format off
  context.SetOverrideTranslations(
    {
      {
        {
          "override_az", {
            {
              "moscow", {
                {"ru", {{1, "Priehal Yandeks"}}},
                {"en", {{1, "Uber has arrived"}}},
              }
            } //, other key
          }
        } //, other keyset
      }
    }
  ); // empty override

  KeysetTranslations translation(
    {
      {
        "moscow", {
          {"ru", {{1, "Priehal Yandeks"}}},
          {"en", {{1, "Yandex has arrived"}}},
        }
      }
    }
  );
  // clang-format on

  context.SetKeysetName("notify");
  context.SetPlaceholderStrictMode(false);
  EXPECT_THROW(CheckKeysetsStopwordsFree(translation, "az", version_settings,
                                         stop_words_lowered, context),
               StopwordsValidationError);
  context.SetPlaceholderStrictMode(true);
  EXPECT_THROW(CheckKeysetsStopwordsFree(translation, "az", version_settings,
                                         stop_words_lowered, context),
               StopwordsValidationError);
}

TEST(TestValidator, TestPlaceholdersSuccess) {
  KeysetInfoList ignoring = {{"geoareas_1", "spb", "en"}};

  // clang-format off
  KeysetsList keysets(
    {
      {
        {
          "geoareas_1", {
            {
              "moscow", {
                {"ru", {{1, "Москва - {0} {1}"}}},
                {"en", {{1, "Moscow is the {0} of {1}"}}},
              }
            }, {
              "spb", {
                {"ru", {{1, "spb"}}},
                {"en", {{1, "spb - 0}"}}}, // ignore error
              }
            }
          }
        }, {
          "geoareas_2", {
            {
              "moscow", {
                {"ru", {{1, "Москва - %(place1)d %(place2)s"}}},
                {"en", {{1, "Moscow is the %(place1)s of {1}"}}},
              }
            }, {
              "spb", {
                {"ru", {{1, "spb"}}},
                {"en", {{1, "spb - {0}"}}},
              }
            }
          }
        }
      }
    }
  );
  // clang-format on

  ValidatorContext context;
  context.SetIgnoreList(std::move(ignoring));

  context.SetPlaceholderStrictMode(false);
  for (const auto& keyset : keysets) {
    for (const auto& [keyset_name, translations] : keyset) {
      context.SetKeysetName(keyset_name);

      EXPECT_NO_THROW(RunCheckKeyset(translations, context));
    }
  }

  context.SetPlaceholderStrictMode(true);
  for (const auto& keyset : keysets) {
    for (const auto& [keyset_name, translations] : keyset) {
      context.SetKeysetName(keyset_name);

      EXPECT_NO_THROW(RunCheckKeyset(translations, context));
    }
  }
}

TEST(TestValidator, TestPlaceholdersError) {
  // clang-format off
  KeysetsList keysets(
    {
      {
        {
          "geoareas_1", {
            {
              "moscow", {
                {"ru", {{1, "Москва - {0} {1}"}}},
                {"en", {{1, "Moscow is the {0} of {1}"}}},
              }
            }, {
              "spb", {
                {"ru", {{1, "spb"}}},
                {"en", {{1, "spb - 0}"}}},
              }
            }
          }
        }, {
          "geoareas_2", {
            {
              "moscow", {
                {"ru", {{1, "Москва - %(place1) %(place2)s"}}},
                {"en", {{1, "Moscow is the %(place1)s of {1}"}}},
              }
            }, {
              "spb", {
                {"ru", {{1, "spb"}}},
                {"en", {{1, "spb - {0}"}}},
              }
            }
          }
        }
      }
    }
  );
  // clang-format on

  ValidatorContext context;
  context.SetPlaceholderStrictMode(false);
  for (const auto& keyset : keysets) {
    for (const auto& [keyset_name, translations] : keyset) {
      context.SetKeysetName(keyset_name);

      EXPECT_THROW(RunCheckKeyset(translations, context),
                   PlaceholderValidationError);
    }
  }

  context.SetPlaceholderStrictMode(true);
  for (const auto& keyset : keysets) {
    for (const auto& [keyset_name, translations] : keyset) {
      context.SetKeysetName(keyset_name);

      EXPECT_THROW(RunCheckKeyset(translations, context),
                   PlaceholderValidationError);
    }
  }
}

TEST(TestValidator, TestPlaceholdersChangeSupportedTypes) {
  // clang-format off
  Keysets keysets(
    {
      {
        "geoareas_2", {
          {
            "moscow", {
              {"ru", {{1, "Москва - %(place1)d %(place2)s"}}},
              {"en", {{1, "Moscow is the %(place1)s of {1}"}}},
            }
          }, {
            "spb", {
              {"ru", {{1, "spb"}}},
              {"en", {{1, "spb - {0}"}}},
            }
          }
        }
      }
    }
  );
  // clang-format on

  ValidatorContext context;
  context.SetPlaceholderStrictMode(true);
  context.SetPlaceholderSupportTypes({"d", "s"});
  for (const auto& [keyset_name, translations] : keysets) {
    context.SetKeysetName(keyset_name);

    EXPECT_NO_THROW(RunCheckKeyset(translations, context));
  }

  context.SetPlaceholderSupportTypes({"d"});
  for (const auto& [keyset_name, translations] : keysets) {
    context.SetKeysetName(keyset_name);

    EXPECT_THROW(RunCheckKeyset(translations, context),
                 PlaceholderValidationError);
  }
}
