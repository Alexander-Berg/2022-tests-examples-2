#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <models/tariff_settings.hpp>
#include <tariffs/tariffs_builder.hpp>
#include "models/tariffs/visibility_helper.hpp"

#include <csignal>
#include <fstream>
#include "utils/jsonfixtures.hpp"
#include "utils/translation_mock.hpp"

#include <boost/range.hpp>
#include <boost/range/adaptors.hpp>
#include <boost/range/algorithm.hpp>
#include <boost/range/algorithm_ext.hpp>

namespace tariff {
tariff::Tariff ParseTariff(const mongo::BSONObj& doc);
}

static const std::string kZelenograd = "zelenograd";
static const std::string kMytishchi = "mytishchi";
static const std::string kEn = "en";

static tariff::VisibilityHelper GetVisibilityHelperMock() {
  return tariff::VisibilityHelper(models::Classes::All, nullptr);
}

static models::AppVars GetAppVarsMock(const config::Config& config) {
  models::AppVars app_vars;
  app_vars.SetCustomAppName("android", config);
  return app_vars;
}

struct TariffsTestHelper {
  // from py
  static void TestSpecialTaximeter() {
    static const config::Config test_config(config::DocsMapForTest());

    const auto tariff_bson = JSONFixtures::GetFixtureBSON(
        "tariff_with_different_special_taximeters.json");
    const auto t = tariff_bson[1].Obj();
    tariff::Tariff tariff = tariff::ParseTariff(t);
    TariffsBuilder tb(kZelenograd, kEn, GetAppVarsMock(test_config),
                      *JSONFixtures::GetMockTranslations(),
                      GetVisibilityHelperMock(), test_config);
    tb.currency_ = "rub";
    const auto st = tb.GenerateSpecialTaximeter(tariff.categories[0], false);

    std::vector<std::string> collected_lines;
    for (const auto& i : st) {
      collected_lines.push_back(fmt::format("{:s} {:s}", i.name, i.price_str));
    }

    // TODO: in py there is a space between the value and the unit (e.g 11
    // rub/km)
    std::vector<std::string> expected_lines = {
        "Thereafter Through Mytishchi 11rub/km",
        "Then (above 8 km) 7rub/km",
        "Thereafter Through Mytishchi 17rub/min",
        "Then (above 6 min) 13rub/min",
        "Thereafter Through Fryazino 23rub/km",
        "Thereafter (after 12 km Through Fryazino) 29rub/km",
        "Thereafter Through Fryazino 21rub/min",
        "Thereafter (after 10 min Through Fryazino) 19rub/min"};

    ASSERT_EQ(collected_lines, expected_lines);
  }

  // from py
  static void TestCityTaximeter() {
    static const config::Config test_config(config::DocsMapForTest());

    const auto tariff_bson = JSONFixtures::GetFixtureBSON(
        "tariff_with_different_special_taximeters.json");
    const auto t = tariff_bson[0].Obj();
    tariff::Tariff tariff = tariff::ParseTariff(t);
    TariffsBuilder tb(kZelenograd, kEn, GetAppVarsMock(test_config),
                      *JSONFixtures::GetMockTranslations(),
                      GetVisibilityHelperMock(), test_config);
    tb.currency_ = "rub";
    tb.tariff_ = tariff;
    const auto st = tb.GenerateCityTaximeter(tariff.categories[0], false);

    std::vector<std::string> collected_lines;
    for (const auto& i : st) {
      collected_lines.push_back(fmt::format("{:s} {:s}", i.name, i.price_str));
    }

    // TODO: in py there is a space between the value and the unit (e.g 11
    // rub/km)
    std::vector<std::string> expected_lines = {
        "Starting fare (5 min and 3 km included) 99rub",
        "further wait time is metered according to the selected service class ",
        "Thereafter inside city 11rub/km", "Thereafter inside city 17rub/min",
        "Then (above 6 min) 11rub/km and 13rub/min"};

    ASSERT_EQ(collected_lines, expected_lines);
  }

  // from py
  static void TestSpecialTaximeterSuburb() {
    static const config::Config test_config(config::DocsMapForTest());

    const auto tariff_bson = JSONFixtures::GetFixtureBSON(
        "tariff_with_different_special_taximeters.json");
    const auto t = tariff_bson[2].Obj();
    tariff::Tariff tariff = tariff::ParseTariff(t);

    // test relative prices for suburb
    TariffsBuilder tb_prices_relative(kMytishchi, kEn,
                                      GetAppVarsMock(test_config),
                                      *JSONFixtures::GetMockTranslations(),
                                      GetVisibilityHelperMock(), test_config);
    tb_prices_relative.currency_ = "rub";
    tb_prices_relative.tariff_ = tariff;
    const auto st_prices_rel = tb_prices_relative.GenerateSpecialTaximeter(
        tariff.categories[0], false);

    std::vector<std::string> collected_lines;
    for (const auto& i : st_prices_rel) {
      collected_lines.push_back(fmt::format("{:s} {:s}", i.name, i.price_str));
    }

    // TODO: in py there is a space between the value and the unit (e.g 11
    // rub/km)
    std::vector<std::string> expected_lines = {
        "Thereafter in suburbs (additional) 2rub/min",
    };
    ASSERT_EQ(collected_lines, expected_lines);

    // test absolute prices for suburb
    auto docs_map = config::DocsMapForTest();
    docs_map.Override("TARIFF_RELATIVE_PRICES_ENABLED", false);
    static const config::Config test_config_for_abs_prices(docs_map);
    TariffsBuilder tb_prices_absolute(
        kMytishchi, kEn, GetAppVarsMock(test_config_for_abs_prices),
        *JSONFixtures::GetMockTranslations(), GetVisibilityHelperMock(),
        test_config_for_abs_prices, models::Classes::All);
    tb_prices_absolute.currency_ = "rub";
    tb_prices_absolute.tariff_ = tariff;
    const auto st_prices_abs = tb_prices_absolute.GenerateSpecialTaximeter(
        tariff.categories[0], false);

    collected_lines.clear();
    for (const auto& i : st_prices_abs) {
      collected_lines.push_back(fmt::format("{:s} {:s}", i.name, i.price_str));
    }

    expected_lines = {
        "Thereafter in suburbs 11rub/km", "Then (above 8 km) 7rub/km",
        "Thereafter in suburbs 19rub/min", "Then (above 6 min) 15rub/min"};
    ASSERT_EQ(collected_lines, expected_lines);
  }

  static void TestGenerateSchedule() {
    static const config::Config test_config(config::DocsMapForTest());

    TariffsBuilder tb(kMytishchi, kEn, GetAppVarsMock(test_config),
                      *JSONFixtures::GetMockTranslations(),
                      GetVisibilityHelperMock(), test_config);
    tariff::Category cat;
    cat.day_type = tariff::DayType::Dayoff;
    cat.time_from = std::make_pair(0, 42);
    cat.time_to = std::make_pair(23, 42);
    const auto daysoff = tb.GenerateSchedule(cat);
    using namespace boost::adaptors;
    std::vector<std::string> s;
    boost::push_back(s, daysoff | map_keys);
    std::vector<std::string> expoff{"6", "7"};
    ASSERT_EQ(boost::sort(s), expoff);

    const auto check_time =
        boost::count_if(daysoff | map_values, [&cat](const ScheduleItem& si) {
          return si.time_from == cat.time_from && si.time_to == cat.time_to;
        });
    ASSERT_EQ((int)check_time, (int)daysoff.size());

    cat.day_type = tariff::DayType::Workday;
    const auto dayswork = tb.GenerateSchedule(cat);
    s.clear();
    boost::push_back(s, dayswork | map_keys);
    std::vector<std::string> expwork{"1", "2", "3", "4", "5"};
    ASSERT_EQ(boost::sort(s), expwork);

    cat.day_type = tariff::DayType::Everyday;
    const auto daysall = tb.GenerateSchedule(cat);
    s.clear();
    boost::push_back(s, daysall | map_keys);
    std::vector<std::string> expall{"1", "2", "3", "4", "5", "6", "7"};
    ASSERT_EQ(boost::sort(s), expall);

    DetailHelpers::TimepairToString(std::make_pair(0, 1));
  }

  static void TestGetGroupNames() {
    static const config::Config test_config(config::DocsMapForTest());

    Geoarea::geoarea_dict_t geoareas;
    geoareas.emplace("area", std::make_shared<Geoarea>("area", "area", 0,
                                                       GeoareaBase::polygon_t{},
                                                       0.0, Geoarea::type_t()));
    Geoarea::type_t flags_airport;
    flags_airport |= Geoarea::Type::Airport;
    geoareas.emplace("area_airport",
                     std::make_shared<Geoarea>("area_airport", "area_airport",
                                               0, GeoareaBase::polygon_t{}, 0.0,
                                               flags_airport));

    Geoarea::type_t flags_sign;
    flags_sign |= Geoarea::Type::SignificantTransfer;
    geoareas.emplace(
        "area_significant",
        std::make_shared<Geoarea>("area_significant", "area_significant", 0,
                                  GeoareaBase::polygon_t{}, 0.0, flags_sign));

    const auto result0 =
        TariffsBuilder::GetGroupNames("area", "area_airport", geoareas);
    const auto result1 = TariffsBuilder::GetGroupNames(
        "area_airport", "area_significant", geoareas);
    const auto result2 =
        TariffsBuilder::GetGroupNames("area_significant", "area", geoareas);
    const auto result3 =
        TariffsBuilder::GetGroupNames("area_airport", "area_airport", geoareas);

    ASSERT_EQ(result0.size(), 1u);
    ASSERT_EQ(result0.front(), std::string("to_airport"));

    ASSERT_EQ(result1.size(), 2u);
    ASSERT_EQ(result1.front(), std::string("from_airport"));
    ASSERT_EQ(result1[1], std::string("to_area_significant"));

    ASSERT_EQ(result2.size(), 1u);
    ASSERT_EQ(result2.front(), std::string("from_area_significant"));

    ASSERT_EQ(result3.size(), 3u);
    ASSERT_EQ(result3[2], std::string("between_airports"));
  }

  static void TestGetCompactPriceString() {
    static const config::Config test_config(config::DocsMapForTest());

    const auto tariff_bson =
        JSONFixtures::GetFixtureBSON("tariff_compact_price.json");
    const auto t = tariff_bson[0].Obj();
    tariff::Tariff tariff = tariff::ParseTariff(t);
    TariffsBuilder tb(kMytishchi, kEn, GetAppVarsMock(test_config),
                      *JSONFixtures::GetMockTranslations(),
                      GetVisibilityHelperMock(), test_config);
    tb.currency_ = "rub";
    tb.tariff_ = tariff;

    models::TariffSettings tariff_settings;
    tariff_settings.compact_transfers_layout = true;
    tb.tariff_settings_ = tariff_settings;

    const std::string price_str = "300rub";

    const auto result1 =
        tb.GetCompactPriceString(tariff.categories[0].transfers[0], price_str);
    const auto result2 =
        tb.GetCompactPriceString(tariff.categories[0].transfers[1], price_str);
    const auto result3 =
        tb.GetCompactPriceString(tariff.categories[0].transfers[2], price_str);
    const auto result4 =
        tb.GetCompactPriceString(tariff.categories[0].transfers[3], price_str);

    tariff_settings.compact_transfers_layout = false;
    tb.tariff_settings_ = tariff_settings;

    const auto result5 =
        tb.GetCompactPriceString(tariff.categories[0].transfers[0], price_str);

    ASSERT_EQ(result1, "Pickup 300rub, then 7rub/km and 9rub/min");
    ASSERT_EQ(result2, "Pickup 300rub, then 0rub/km and 12rub/min");
    ASSERT_EQ(result3, "Pickup 300rub, then 6rub/km and 0rub/min");
    ASSERT_EQ(result4, "Pickup 300rub, then 0rub/km and 0rub/min");
    ASSERT_EQ(result5, "");
  }
};

TEST(TariffBuilder, SpecialTaximeter) {
  TariffsTestHelper::TestSpecialTaximeter();
}

TEST(TariffBuilder, CityTaximeter) { TariffsTestHelper::TestCityTaximeter(); }

TEST(TariffBuilder, SpecialTaximeterSuburb) {
  TariffsTestHelper::TestSpecialTaximeterSuburb();
}

TEST(TariffBuilder, GenerateSchedule) {
  TariffsTestHelper::TestGenerateSchedule();
}

TEST(TariffBuilder, GetGroupNames) { TariffsTestHelper::TestGetGroupNames(); }

TEST(TariffBuilder, GetCompactPriceString) {
  TariffsTestHelper::TestGetCompactPriceString();
}
