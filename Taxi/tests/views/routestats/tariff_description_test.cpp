#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "utils/translation_mock.hpp"
#include "views/routestats/tariff_description.hpp"

class TariffDescriptionTest : public ::testing::Test {
 public:
  TariffDescriptionTest()
      : translations_(new MockTranslations(true)),
        config_(new config::Config(config::DocsMapForTest())) {
    config_->currency_rounding_rules =
        std::unordered_map<std::string, config::ValueDict<double>>(
            {{"__default__",
              config::ValueDict<double>({{"__default__", 0.1}})}});

    Json::Value v;
    v["tariff_description_fixed_transfer_time_threshold_min"] = 3;
    v["tariff_description_fixed_transfer_distance_threshold_km"] = 3;
    config::DocsMap doc_map;
    doc_map.Parse(v.toStyledString());

    config_->tariff_description_fixed_transfer_time_threshold_min =
        config::Value<int>(
            "tariff_description_fixed_transfer_time_threshold_min", doc_map);
    config_->tariff_description_fixed_transfer_distance_threshold_km =
        config::Value<int>(
            "tariff_description_fixed_transfer_distance_threshold_km", doc_map);
  }

 protected:
  std::shared_ptr<MockTranslations> translations_;
  std::shared_ptr<config::Config> config_;

  static Json::Value BuildExpectedDetails(const std::string& price,
                                          const std::string& icon,
                                          std::vector<std::string> comments) {
    auto format = [](const std::string& type, const std::string& value) {
      Json::Value r;
      r["type"] = type;
      r["value"] = value;
      return r;
    };
    Json::Value result{Json::arrayValue};
    result.append(format("price", price));
    result.append(format("icon", icon));
    for (const auto& c : comments) result.append(format("comment", c));
    return result;
  }
};

TEST_F(TariffDescriptionTest, RouteWithDestination) {
  views::routestats::TariffDescription td;
  td.price_info.predicted_price.value = 199.51;
  td.route_info.with_destination = true;

  auto resp = views::routestats::BuildDescriptionResponse(
      td, *translations_, *config_, "en", "rus", "RUB", false, false, true,
      ClientCapabilities(), {});

  EXPECT_EQ("200rub", resp);
}

TEST_F(TariffDescriptionTest, FixedPriceTransfer) {
  views::routestats::TariffDescription td;
  td.price_info.min_price = 999.1;
  td.route_info.home_zone = "moscow";
  td.route_info.source_zone = "ekb";
  td.route_info.is_transfer = true;
  td.route_info.with_destination = false;

  auto resp = views::routestats::BuildDescriptionResponse(
      td, *translations_, *config_, "en", "rus", "RUB", false, false, true,
      ClientCapabilities(), {});

  EXPECT_EQ("to Moscow — from 999rub", resp);
}

TEST_F(TariffDescriptionTest, FreeRide) {
  views::routestats::TariffDescription td;
  td.price_info.min_price = 99;
  td.price_info.predicted_price.value = 289;
  td.route_info.is_transfer = false;
  td.route_info.with_destination = false;

  // include nothing
  auto resp = views::routestats::BuildDescriptionResponse(
      td, *translations_, *config_, "en", "rus", "RUB", false, false, true,
      ClientCapabilities(), {});
  EXPECT_EQ("from 99rub", resp);

  // include time and distance
  td.price_info.time =
      views::routestats::TarifficationUnit<std::chrono::minutes>();
  td.price_info.time->included = std::chrono::minutes(3);
  td.price_info.time->price = 5;
  td.price_info.distance = views::routestats::TarifficationUnit<int>();
  td.price_info.distance->included = 3;
  td.price_info.distance->price = 10;
  resp = views::routestats::BuildDescriptionResponse(
      td, *translations_, *config_, "en", "rus", "RUB", false, false, true,
      ClientCapabilities(), {});
  EXPECT_EQ("99rub for the first 3 min and 3 km", resp);

  // use predicted price
  td.route_info.home_zone = "moscow";
  td.route_info.source_zone = "ekb";
  td.price_info.paid_dispatch_price = 10;
  resp = views::routestats::BuildDescriptionResponse(
      td, *translations_, *config_, "en", "rus", "RUB", false, false, true,
      ClientCapabilities(), {});
  EXPECT_EQ("~289rub for the first 3 min and 3 km", resp);
}

TEST_F(TariffDescriptionTest, DetailsFixedPriceTransfer) {
  views::routestats::TariffDescription td;
  td.price_info.min_price = 999.1;
  td.route_info.home_zone = "moscow";
  td.route_info.source_zone = "ekb";
  td.route_info.is_transfer = true;
  td.route_info.with_destination = false;

  // (sia-raimu) tariff::Category, Experiments3Data and LogExtra should not
  // affect test result, they were added only because of method signature change
  // in TAXIBACKEND-28507 (values are used only if
  // route_additional_information_step experiment is on)
  auto resp = views::routestats::BuildTariffDetails(
      td, *translations_, *config_, "en", "RUB", boost::none,
      tariff::Category{}, Experiments3Data{}, LogExtra{}, false);
  EXPECT_EQ(utils::helpers::WriteJson(BuildExpectedDetails(
                "from at 999rub", "from 999rub", {"ride to Moscow"})),
            utils::helpers::WriteJson(resp));
}

TEST_F(TariffDescriptionTest, DetailsFreeRide) {
  views::routestats::TariffDescription td;
  td.price_info.min_price = 99;
  td.price_info.predicted_price.value = 289;
  td.route_info.is_transfer = false;
  td.route_info.with_destination = false;

  // (sia-raimu) tariff::Category, Experiments3Data and LogExtra should not
  // affect test result, they were added only because of method signature change
  // in TAXIBACKEND-28507 (values are used only if
  // route_additional_information_step experiment is on)

  // with no data
  auto resp = views::routestats::BuildTariffDetails(
      td, *translations_, *config_, "en", "RUB", boost::none,
      tariff::Category{}, Experiments3Data{}, LogExtra{}, false);
  EXPECT_EQ(utils::helpers::WriteJson(
                BuildExpectedDetails("99rub", "99rub", {"pickup"})),
            utils::helpers::WriteJson(resp));

  // with time and distance price, nothing included
  td.price_info.time =
      views::routestats::TarifficationUnit<std::chrono::minutes>();
  td.price_info.time->included = std::chrono::minutes(0);
  td.price_info.time->price = 5;
  td.price_info.distance = views::routestats::TarifficationUnit<int>();
  td.price_info.distance->included = 0;
  td.price_info.distance->price = 10;

  resp = views::routestats::BuildTariffDetails(
      td, *translations_, *config_, "en", "RUB", boost::none,
      tariff::Category{}, Experiments3Data{}, LogExtra{}, false);
  EXPECT_EQ(
      utils::helpers::WriteJson(BuildExpectedDetails(
          "99rub", "99rub", {"pickup", "thereafter 10rub/km and 5rub/min"})),
      utils::helpers::WriteJson(resp));

  // with time and distance price, with prepaid intervals
  td.price_info.time->included = std::chrono::minutes(3);
  td.price_info.distance->included = 3;
  resp = views::routestats::BuildTariffDetails(
      td, *translations_, *config_, "en", "RUB", boost::none,
      tariff::Category{}, Experiments3Data{}, LogExtra{}, false);
  EXPECT_EQ(utils::helpers::WriteJson(
                BuildExpectedDetails("99rub", "99rub",
                                     {"3 min included thereafter 5rub/min",
                                      "3 km included thereafter 10rub/km"})),
            utils::helpers::WriteJson(resp));
}
