#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "application_config.hpp"

TEST(TestApplicationMapTranslations, TaxiVersionOverride) {
  const auto conf = R"({
    "yandex:10": {
        "client_message": "10"
    },
    "yandex:20": {
        "client_message": "20"
    },
    "yandex:30": {
        "client_message": "30"
    }
  })";

  auto docs_map = config::DocsMapForTest();
  docs_map.Override("APPLICATION_MAP_TRANSLATIONS", mongo::fromjson(conf));

  const auto& config = config::Config(docs_map);
  const auto& app_config = config.Get<config::application::ApplicationConfig>();

  // override for application `yandex` doesn't exists in config
  auto desc = app_config.app_translations.GetOverrideTranslation("yandex");
  ASSERT_EQ(desc.has_value(), false);

  // override for version 10 and less doesn't exists in config
  desc = app_config.app_translations.GetOverrideTranslation("yandex", 9);
  ASSERT_EQ(desc.has_value(), false);

  // Tests version detector
  desc = app_config.app_translations.GetOverrideTranslation("yandex", 10);
  ASSERT_EQ(desc.has_value(), true);
  ASSERT_EQ(desc->at("client_message"), "10");

  desc = app_config.app_translations.GetOverrideTranslation("yandex", 19);
  ASSERT_EQ(desc.has_value(), true);
  ASSERT_EQ(desc->at("client_message"), "10");

  desc = app_config.app_translations.GetOverrideTranslation("yandex", 20);
  ASSERT_EQ(desc.has_value(), true);
  ASSERT_EQ(desc->at("client_message"), "20");

  desc = app_config.app_translations.GetOverrideTranslation("yandex", 9999);
  ASSERT_EQ(desc.has_value(), true);
  ASSERT_EQ(desc->at("client_message"), "30");
}

TEST(TestApplicationMapTranslations, TaxiDefaultOverride) {
  const auto conf = R"({
    "yandex": {
        "client_message": "default"
    },
    "yandex:20": {
        "client_message": "20"
    }
  })";

  auto docs_map = config::DocsMapForTest();
  docs_map.Override("APPLICATION_MAP_TRANSLATIONS", mongo::fromjson(conf));

  const auto& config = config::Config(docs_map);
  const auto& app_config = config.Get<config::application::ApplicationConfig>();

  auto desc = app_config.app_translations.GetOverrideTranslation("yandex");
  ASSERT_EQ(desc.has_value(), true);
  ASSERT_EQ(desc->at("client_message"), "default");

  // select default override due to 10 < 20
  desc = app_config.app_translations.GetOverrideTranslation("yandex", 10);
  ASSERT_EQ(desc.has_value(), true);
  ASSERT_EQ(desc->at("client_message"), "default");

  // override for major version greter then 20
  desc = app_config.app_translations.GetOverrideTranslation("yandex", 20);
  ASSERT_EQ(desc.has_value(), true);
  ASSERT_EQ(desc->at("client_message"), "20");
}
