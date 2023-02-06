#include <gtest/gtest.h>

#include <unordered_set>

#include <boost/algorithm/string.hpp>

#include <testing/taxi_config.hpp>
#include <userver/formats/json.hpp>

#include <pricing-components/helpers/price_detailing.hpp>
#include <taxi_config/pricing-components/taxi_config.hpp>

using lang::meta_modifications::MetaId;
using lang::meta_modifications::MetaValue;

namespace {

static const std::string kDefaultConsumer{"__default__"};

static const std::string kOverrideL10nJson{R"json(
{
  "waiting_in_destination_price": {
    "keyset": "taximeter_driver_messages",
    "tanker_key": "complete_order_paid_unloading"
  },
  "waiting_in_transit_price": {
    "keyset": "taximeter_driver_messages",
    "tanker_key": "calc_label_waint_in_way"
  },
  "waiting_price": {
    "keyset": "taximeter_driver_messages",
    "tanker_key": "complete_order_payed_waiting"
  }
})json"};

static const std::string kRequirementsConfig{R"json(
{
  "__default__": {
    "requirements": {
      "patterns": [
        "([\\w|\\.]+_price):(price|per_unit|included|count)"
      ],
      "tanker": {
        "keyset": "tariff"
      }
    }
  }
})json"};

static const std::string kServicesConfig{R"json(
{
  "__default__": {
    "services": {
      "patterns": [
        "waiting_price",
        "waiting_in_transit_price",
        "waiting_in_destination_price",
        "childchair_booster_price"
      ],
      "tanker": {
        "keyset": "tariff"
      }
    }
  }
})json"};

static const std::string kDuplicatesLessConfig{R"json(
{
  "__default__": {
    "requirements": {
      "patterns": [
        "(waiting)_(price)",
        "(waiting)_(price|per_unit|included|count)"
      ],
      "tanker": {
        "keyset": "tariff"
      }
    }
  }
})json"};

static const std::string kDuplicatesMoreConfig{R"json(
{
  "__default__": {
    "requirements": {
      "patterns": [
        "(waiting)_(price|per_unit|included|count)",
        "(waiting)_(price)"
      ],
      "tanker": {
        "keyset": "tariff"
      }
    }
  }
})json"};

}  // namespace

struct PriceDetailingTestData {
  struct Values {
    uint16_t price{};
    std::optional<uint16_t> count{};
    std::optional<uint16_t> per_unit{};
    std::optional<uint16_t> included{};
  };

  std::string config;
  std::unordered_set<MetaId> metadata;
  std::vector<std::pair<std::string, Values>> expected;
};

class PriceDetailing : public ::testing::TestWithParam<PriceDetailingTestData> {
};

TEST_P(PriceDetailing, CreateByOrder) {
  const auto [config_json, metadata, expected] = GetParam();

  const dynamic_config::StorageMock storage_mock{
      {{taxi_config::PRICING_DATA_PREPARER_OVERRIDE_L10N,
        formats::json::FromString(kOverrideL10nJson)},
       {taxi_config::PRICING_DATA_PREPARER_DETAILING_BY_CONSUMERS,
        formats::json::FromString(config_json)}}};

  std::unordered_set<std::string> used_metadata_keys;
  const auto& price_details = helpers::BuildPriceDetails(
      metadata, kDefaultConsumer, storage_mock.GetSnapshot(),
      used_metadata_keys);

  for (const auto& item : metadata) {
    EXPECT_TRUE(used_metadata_keys.count(item.key));
  }

  const auto& actual =
      (!price_details.requirements.empty() ? price_details.requirements
                                           : price_details.services);
  EXPECT_EQ(actual.size(), expected.size());
  auto down_optional_type = [](const auto& meta) {
    return (meta ? std::make_optional(meta->value) : std::nullopt);
  };

  for (size_t i = 0, sz = std::min(actual.size(), expected.size()); i < sz;
       ++i) {
    double price = actual[i].price.value;
    std::optional<double> count = down_optional_type(actual[i].count);
    std::optional<double> per_unit = down_optional_type(actual[i].per_unit);
    std::optional<double> included = down_optional_type(actual[i].included);
    EXPECT_EQ(actual[i].name, expected[i].first);
    EXPECT_EQ(price, expected[i].second.price);
    EXPECT_EQ(count, expected[i].second.count);
    EXPECT_EQ(per_unit, expected[i].second.per_unit);
    EXPECT_EQ(included, expected[i].second.included);
    EXPECT_EQ(actual[i].keyset,
              (boost::algorithm::starts_with(actual[i].name, "waiting_")
                   ? "taximeter_driver_messages"
                   : "tariff"));
  }
}

INSTANTIATE_TEST_SUITE_P(            //
    PriceDetailing, PriceDetailing,  //
    ::testing::Values(               //
        PriceDetailingTestData{
            kRequirementsConfig,  //
            {
                MetaId{{"childchair_booster_price:price"}, 0},         //
                MetaId{{"waiting_price:price"}, 1},                    //
                MetaId{{"waiting_price:count"}, 2},                    //
                MetaId{{"waiting_in_transit_price:price"}, 3},         //
                MetaId{{"waiting_in_transit_price:count"}, 4},         //
                MetaId{{"waiting_in_transit_price:per_unit"}, 5},      //
                MetaId{{"waiting_in_destination_price:price"}, 6},     //
                MetaId{{"waiting_in_destination_price:count"}, 7},     //
                MetaId{{"waiting_in_destination_price:per_unit"}, 8},  //
                MetaId{{"waiting_in_destination_price:included"}, 9},  //
            },                                                         //
            {
                // one pattern: sorted by alphabetical
                {"childchair_booster_price", {0}},               //
                {"waiting_in_destination_price", {6, 7, 8, 9}},  //
                {"waiting_in_transit_price", {3, 4, 5}},         //
                {"waiting_price", {1, 2}},                       //
            }                                                    //
        },
        PriceDetailingTestData{
            kServicesConfig,  //
            {
                MetaId{{"childchair_booster_price"}, 0},      //
                MetaId{{"waiting_price"}, 1},                 //
                MetaId{{"waiting_in_transit_price"}, 2},      //
                MetaId{{"waiting_in_destination_price"}, 3},  //
            },                                                //
            {
                // some patterns: sorted as set in config
                {"waiting_price", {1}},                 //
                {"waiting_in_transit_price", {2}},      //
                {"waiting_in_destination_price", {3}},  //
                {"childchair_booster_price", {0}},      //
            }                                           //
        },                                              //
        PriceDetailingTestData{
            kDuplicatesLessConfig,  //
            {
                MetaId{{"waiting_price"}, 0},     //
                MetaId{{"waiting_count"}, 1},     //
                MetaId{{"waiting_per_unit"}, 2},  //
            },                                    //
            {
                // result of first pattern
                {"waiting", {0}},  //
            }                      //
        },                         //
        PriceDetailingTestData{
            kDuplicatesMoreConfig,  //
            {
                MetaId{{"waiting_price"}, 0},  //
                MetaId{{"waiting_count"}, 1},  //
                MetaId{{"waiting_per_unit"}, 2},
            },  //
            {
                // result of first pattern
                {"waiting", {0, 1, 2}},  //
            }                            //
        }                                //
        )                                //
);
