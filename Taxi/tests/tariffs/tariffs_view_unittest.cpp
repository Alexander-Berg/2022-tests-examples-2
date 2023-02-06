#include <gtest/gtest.h>
#include <models/parsing.hpp>
#include <models/tariff_settings.hpp>
#include <tariffs/tariffs_builder.hpp>
#include "tariffs/tariffs_data.hpp"

#include <common/test_config.hpp>
#include <csignal>
#include <fstream>
#include <regex>
#include "config/config.hpp"
#include "mongo/mongo.hpp"
#include "utils/geoareas_fixture.hpp"
#include "utils/json_compare.hpp"
#include "utils/jsonfixtures.hpp"
#include "utils/translation_mock.hpp"
#include "views/tariffs/tariffs.hpp"

namespace tariff {
tariff::Tariff ParseTariff(const mongo::BSONObj& doc);
}
namespace geoarea {
Geoarea ParseGeoarea(const mongo::BSONObj& doc,
                     bool use_new_contains_point_fast_algo = false);
}

struct TariffsViewGeneratorTestHelper {
  // Test cases from python
  //----------------------------------------------------------------------------

  static views::tariffs::full::Deps GetDependencies(
      const std::string& tariff_settings_json = "tariff_settings2.json",
      const bool relative_prices_enabled = true) {
    const auto geoareas_bson = JSONFixtures::GetFixtureBSON("geoareas.json");

    const auto& tariffs_fixture = JSONFixtures::GetFixtureJSON("tariffs2.json");
    const auto& tariff_settings_fixture =
        JSONFixtures::GetFixtureJSON(tariff_settings_json);

    views::tariffs::full::Deps deps;
    deps.translations = JSONFixtures::GetMockTranslations();
    deps.geoareas = std::make_shared<Geoarea::geoarea_dict_t>(
        GeoareasFixture::LoadFromBSONArray(geoareas_bson));

    const auto& tariffs = std::make_shared<tariff::tariff_dict_t>();
    for (const auto& obj : tariffs_fixture) {
      (*tariffs)[obj["home_zone"].asString()] =
          tariff::ParseTariff(mongo::fromjson(obj.toStyledString()));
    }
    deps.tariffs = tariffs;

    auto tariff_settings = std::make_shared<models::tariff_settings_dict>();
    for (const auto& obj : tariff_settings_fixture) {
      models::TariffSettings tariff_setting;
      tariff_setting.Parse(mongo::fromjson(obj.toStyledString()));
      (*tariff_settings)[obj["hz"].asString()] = std::move(tariff_setting);
    }
    deps.tariff_settings = tariff_settings;

    models::Country country;
    country.id = "rus";
    country.currency = "RUB";

    const auto& countries = std::make_shared<models::CountryMap>();
    (*countries)["rus"] = country;
    deps.countries = countries;

    deps.cities_model = JSONFixtures::GetMockCities();
    deps.experiments = std::make_shared<common::Experiments>();
    deps.experiments3 = std::make_shared<experiments3::models::CacheManager>();

    config::DocsMap docs_map = config::DocsMapForTest();
    docs_map.Override("ALL_CATEGORIES", BSON_ARRAY("express"
                                                   << "econom"
                                                   << "business"
                                                   << "comfortplus"
                                                   << "vip"
                                                   << "minivan"
                                                   << "pool"
                                                   << "business2"
                                                   << "kids"
                                                   << "uberx"
                                                   << "uberselect"
                                                   << "uberblack"
                                                   << "uberkids"
                                                   << "uberstart"));
    docs_map.Override("APPLICATION_BRAND_CATEGORIES_SETS",
                      BSON("__default__" << BSON_ARRAY("express"
                                                       << "econom"
                                                       << "business"
                                                       << "comfortplus"
                                                       << "vip"
                                                       << "minivan"
                                                       << "pool"
                                                       << "business2"
                                                       << "kids")
                                         << "yauber"
                                         << BSON_ARRAY("uberx"
                                                       << "uberselect"
                                                       << "uberblack"
                                                       << "uberkids"
                                                       << "uberstart")));

    if (!relative_prices_enabled) {
      docs_map.Override("TARIFF_RELATIVE_PRICES_ENABLED", false);
    }

    deps.config = std::make_shared<config::Config>(docs_map);
    return deps;
  }

  static tariff::VisibilityHelper MakeVisibilityHelper() {
    const views::tariffs::full::Deps& deps = GetDependencies();
    return tariff::VisibilityHelper::ApplicationBrandTariffs(
        "yataxi", *deps.config, deps.geoareas.get());
  }

  // call BuildTariffDescription and check if the result json matches the
  // expected result
  static void TestBuildTariffDescription(
      const views::tariffs::full::Args& args, const std::string expected,
      const views::tariffs::full::Deps& deps = GetDependencies()) {
    Json::Value received_json = views::tariffs::Build(args, deps);
    Json::Value expected_json = JSONFixtures::GetFixtureJSON(expected);

    const bool cmp = JSONCompare().Compare(received_json, expected_json);

    ASSERT_TRUE(cmp);
  }

  static void TestBuildTariffDescriptionEkb() {
    auto visibility_helper = MakeVisibilityHelper();
    TestBuildTariffDescription(
        {"Ekb", models::Classes::All, "en", false, visibility_helper, {}, {}},
        "tariffs_rendered_ekb_relative_prices.json");

    // turn off TARIFF_RELATIVE_PRICES_ENABLED
    auto deps = GetDependencies("tariff_settings2.json", false);
    TestBuildTariffDescription(
        {"Ekb", models::Classes::All, "en", false, visibility_helper, {}, {}},
        "tariffs_rendered_ekb_absolute_prices.json", deps);
  }

  static void TestBuildTariffDescriptionMytishchi() {
    auto visibility_helper = MakeVisibilityHelper();
    TestBuildTariffDescription(
        {"Mytishchi",
         models::Classes::All,
         "en",
         false,
         visibility_helper,
         {},
         {}},
        "tariffs_rendered_mytishchi_relative_prices.json");

    // turn off TARIFF_RELATIVE_PRICES_ENABLED
    auto deps = GetDependencies("tariff_settings2.json", false);
    TestBuildTariffDescription(
        {"Mytishchi",
         models::Classes::All,
         "en",
         false,
         visibility_helper,
         {},
         {}},
        "tariffs_rendered_mytishchi_absolute_prices.json", deps);
  }

  static void TestBuildTariffDescriptionKolomna() {
    auto deps = GetDependencies();
    std::shared_ptr<MockTranslations> translations{new MockTranslations(false)};
    translations->LoadFromJSON(
        "geoareas", JSONFixtures::GetFixtureJSON("translations_geoareas.json"));
    translations->LoadFromJSON(
        "tariff", JSONFixtures::GetFixtureJSON("db_localization_tariff.json"));
    deps.translations = translations;
    auto visibility_helper = MakeVisibilityHelper();

    TestBuildTariffDescription({"Коломна",
                                models::Classes::All,
                                "en",
                                false,
                                visibility_helper,
                                {},
                                {}},
                               "tariffs_rendered_kolomna_relative_prices.json",
                               deps);

    // turn off TARIFF_RELATIVE_PRICES_ENABLED
    deps = GetDependencies("tariff_settings2.json", false);
    deps.translations = translations;
    TestBuildTariffDescription({"Коломна",
                                models::Classes::All,
                                "en",
                                false,
                                visibility_helper,
                                {},
                                {}},
                               "tariffs_rendered_kolomna_absolute_prices.json",
                               deps);
  }

  //------------------------------------end python
  // tests----------------------------------------

  static void TestBuildTariffDescriptionWithFormatCurrency() {
    auto deps = GetDependencies();
    auto visibility_helper = MakeVisibilityHelper();
    views::tariffs::full::Args args{
        "Ekb", models::Classes::All, "en", true, visibility_helper, {}, {}};

    Json::Value received_json = views::tariffs::Build(args, deps);

    ASSERT_FALSE(received_json["currency_rules"].empty());
    const auto& cr = received_json["currency_rules"];
    ASSERT_EQ(cr["text"].asString(), "rub");
    ASSERT_EQ(cr["code"].asString(), "RUB");
    ASSERT_EQ(cr["template"].asString(), "$SIGN$$VALUE$$CURRENCY$");
    ASSERT_EQ(cr["sign"].asString(), "\u20BD");
  }

  // call BuildResponse and check if the result json matches the expected result
  static void TestBuildResponse() {
    auto deps = GetDependencies();
    ClientCapabilities cc(Json::objectValue, views::Args{}, {});

    auto ImageComponentMock = [](const std::string&) {
      return Image{"tag", "base_url", "key", "path", "id", 42};
    };

    views::tariffs::categories::Args args{
        "Mytishchi", models::Classes::All, 0, "en", ImageComponentMock, {}, {}};

    Json::Value received_json = views::tariffs::BuildCategories(args, deps, cc);
    Json::Value expected_json = JSONFixtures::GetFixtureJSON(
        "tariffs_rendered_mytishchi_no_intervals.json");
    JSONCompare jsc;
    const bool cmp = jsc.Compare(received_json, expected_json["max_tariffs"]);

    ASSERT_TRUE(cmp);
  }

  // Check if filtering by ClientCapabilities works
  // Specifically, tariffs support supports_no_cars_available flag
  static void TestBuildResponseClientCaps() {
    auto deps = GetDependencies("tariff_settings_no_cars.json");
    ClientCapabilities cc(Json::objectValue, views::Args{}, {});

    auto ImageComponentMock = [](const std::string&) {
      return Image{"tag", "base_url", "key", "path", "id", 42};
    };
    // no categories matching client capabilities
    {
      views::tariffs::categories::Args reponse_args{
          "Mytishchi", models::Classes::All, 64, "en", ImageComponentMock, {},
          {}};

      // client does not provide supports_no_cars_available
      ClientCapabilities cc(Json::objectValue, views::Args{}, {});

      // so, no categories can be returned
      Json::Value received_json =
          views::tariffs::BuildCategories(reponse_args, deps, cc);
      ASSERT_TRUE(received_json.isArray() && received_json.size() == 0);
    }

    // a single category matching client capabilities
    {
      views::tariffs::categories::Args args{
          "Mytishchi", models::Classes::All, 64, "en", ImageComponentMock, {},
          {}};
      Json::Value js = Json::objectValue;
      js["supports_no_cars_available"] = true;
      // client does provide supports_no_cars_available
      ClientCapabilities cc(js, views::Args{}, {});
      // hence, 1 category is available
      Json::Value received_json =
          views::tariffs::BuildCategories(args, deps, cc);
      ASSERT_TRUE(received_json.isArray() && received_json.size() == 1);
    }
  }
};

struct DetailedUnitsTestHelper {
  static void TestDetailedTime() {
    const auto test = [](double nsec) {
      return DetailHelpers::DetailedTime(nsec, "en", false,
                                         *JSONFixtures::GetMockTranslations());
    };

    ASSERT_EQ(test(3600 + 240 + 42), "1 h 4 min 42 s");
    ASSERT_EQ(test(3600 + 360 + 42), "1 h 6 min");

    ASSERT_EQ(test(1), "1 s");
    ASSERT_EQ(test(61), "1 min 1 s");

    const auto test2 = [](double nsec) {
      return DetailHelpers::DetailedTime(nsec, "en", true,
                                         *JSONFixtures::GetMockTranslations());
    };

    ASSERT_EQ(test2(1), "1 s");
    ASSERT_EQ(test2(60), "min");
    ASSERT_EQ(test2(3600), "h");
    ASSERT_EQ(test2(3600 + 240 + 42), "1 h 4 min 42 s");
  }

  static void TestDetailedDistance() {
    const auto test = [](double nmeters) {
      return DetailHelpers::DetailedDistance(
          nmeters, "en", false, *JSONFixtures::GetMockTranslations());
    };
    ASSERT_EQ(test(42000), "42 km");
    ASSERT_EQ(test(42042), "42.042 km");

    const auto test2 = [](double nmeters) {
      return DetailHelpers::DetailedDistance(
          nmeters, "en", true, *JSONFixtures::GetMockTranslations());
    };

    ASSERT_EQ(test2(1000), "km");
    ASSERT_EQ(test2(42042), "42.042 km");
  }

  static void TestDetailedSpeed() {
    const auto test = [](double mps) {
      return DetailHelpers::DetailedSpeed(mps, "en",
                                          *JSONFixtures::GetMockTranslations());
    };
    ASSERT_EQ(test(10), "36 km/h");
    ASSERT_EQ(test(11), "39.6 km/h");
  }
};

TEST(TariffsViewGenerator, TestBuildTariffDescriptionEkb) {
  TariffsViewGeneratorTestHelper::TestBuildTariffDescriptionEkb();
}

TEST(TariffsViewGenerator, TestBuildTariffDescriptionMytishchi) {
  TariffsViewGeneratorTestHelper::TestBuildTariffDescriptionMytishchi();
}

TEST(TariffsViewGenerator, TestBuildTariffDescriptionKolomna) {
  TariffsViewGeneratorTestHelper::TestBuildTariffDescriptionKolomna();
}

TEST(TariffsViewGenerator, TestBuildTariffDescriptionWithFormatCurrency) {
  TariffsViewGeneratorTestHelper::
      TestBuildTariffDescriptionWithFormatCurrency();
}

TEST(TariffsViewGenerator, TestBuildResponse) {
  TariffsViewGeneratorTestHelper::TestBuildResponse();
}

TEST(TariffsView, TestBuildResponseClientCaps) {
  TariffsViewGeneratorTestHelper::TestBuildResponseClientCaps();
}

TEST(DetailedUnitsHelper, TestDetailedTime) {
  DetailedUnitsTestHelper::TestDetailedTime();
}

TEST(DetailedUnitsHelper, TestDetailedDistance) {
  DetailedUnitsTestHelper::TestDetailedDistance();
}

TEST(DetailedUnitsHelper, TestDetailedSpeed) {
  DetailedUnitsTestHelper::TestDetailedSpeed();
}
