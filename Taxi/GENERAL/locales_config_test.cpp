#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/locales_config.hpp>

namespace {
using config::Locales;
}

TEST(TestLocalesConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& cfg = config.Get<Locales>();

  std::map<std::string, std::map<std::string, std::string>> target{
      {Locales::kOverrideKeyAz, {}},    {Locales::kOverrideKeyUberdriver, {}},
      {Locales::kOverrideKeyVezet, {}}, {Locales::kOverrideKeyYangoPro, {}},
      {Locales::kOverrideKeyRida, {}},  {Locales::kOverrideKeyTurla, {}}};

  ASSERT_EQ(cfg.locales_override_keysets.value, target);
}

TEST(TestLocalesConfig, ConfigValue) {
  const auto config_str = R"(
    {
      "aze": {"override_keysets": {
        "backend_selfemployed": "override_az",
        "taximeter_driver_messages": "ignore"
      }},
      "uberdriver": {"override_keysets": {
        "backend_selfemployed": "override_uberdriver",
        "taximeter_driver_messages": "taximeter_driver_messages_uberdriver"
      }}
    }
  )";

  auto docs_map = config::DocsMapForTest();
  docs_map.Override("LOCALES_APPLICATION_TYPE_OVERRIDES",
                    mongo::fromjson(config_str));
  const auto& config = config::Config(docs_map);
  const auto& cfg = config.Get<config::Locales>();

  std::map<std::string, std::map<std::string, std::string>> target{
      {Locales::kOverrideKeyAz,
       {{"backend_selfemployed", "override_az"},
        {"taximeter_driver_messages", "ignore"}}},
      {Locales::kOverrideKeyUberdriver,
       {{"backend_selfemployed", "override_uberdriver"},
        {"taximeter_driver_messages", "taximeter_driver_messages_uberdriver"}}},
      {Locales::kOverrideKeyVezet, {}},
      {Locales::kOverrideKeyYangoPro, {}},
      {Locales::kOverrideKeyRida, {}},
      {Locales::kOverrideKeyTurla, {}}};

  ASSERT_EQ(cfg.locales_override_keysets.value, target);
}
