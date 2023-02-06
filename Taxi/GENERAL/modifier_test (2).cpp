#include "modifier.hpp"

#include <cmath>
#include <iterator>
#include <limits>
#include <utility>

#include <gtest/gtest.h>

#include <fmt/format.h>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>
#include <localization/localization.hpp>
#include <models/place.hpp>
#include <taxi_config/taxi_config.hpp>
#include <taxi_config/variables/EATS_CATALOG_PREPARATION_TIME_FEATURE.hpp>

namespace handlers::common_map {

namespace {

using eats_catalog::localization::Localizer;
using eats_catalog::localization::LocalizerPtr;
using eats_catalog::localization::TankerKey;

class TestLocalizer : public Localizer {
 public:
  std::string Translate(const TankerKey& tanker_key,
                        const int count = 1) const override {
    return Translate(tanker_key, {}, count);
  }

  std::string Translate(const TankerKey& tanker_key, const l10n::ArgsList& args,
                        [[maybe_unused]] const int count = 1) const override {
    const auto translation = tanker_key.GetUnderlying();
    if (args.empty()) {
      return translation;
    }
    formats::json::ValueBuilder builder;
    for (const auto& [key, value] : args) {
      builder[key] = value;
    }
    return translation + "," + formats::json::ToString(builder.ExtractValue());
  }

  std::optional<std::string> TranslateOptional(
      const TankerKey& tanker_key, const int count = 1) const override {
    return Translate(tanker_key, count);
  }

  std::optional<std::string> TranslateOptional(
      const TankerKey& tanker_key, const l10n::ArgsList& args,
      const int count = 1) const override {
    return Translate(tanker_key, args, count);
  }

  std::string GetPriceTemplate() const override { return ""; }

  std::string GetLocalizedCurrency(
      const price_format::Currency&) const override {
    return "";
  }
};

LocalizerPtr MakeTestLocalizer() { return std::make_shared<TestLocalizer>(); }

}  // namespace

namespace render = ::handlers::internal_v1_catalog_for_layout::post::render;
using ::taxi_config::eats_catalog_preparation_time_feature::
    EatsCatalogPreparationTimeFeature;
using ::taxi_config::eats_catalog_preparation_time_feature::Parse;

namespace {

constexpr std::string_view kPreparationTimeConfig = R"(
{
    "rounding_policy": [
        {
            "from_preparation_minutes": 0,
            "abs_tolerance": 1
        },
        {
            "from_preparation_minutes": 15,
            "abs_tolerance": 5
        },
        {
            "from_preparation_minutes": 60,
            "abs_tolerance": 10
        },
        {
            "from_preparation_minutes": 120,
            "abs_tolerance": 20
        }
    ]
}
)";

taxi_config::TaxiConfig PatchConfig(const std::string_view preparation_config,
                                    const int min_preparation_minutes) {
  auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();
  config.eats_catalog_preparation_time_feature =
      Parse(formats::json::FromString(preparation_config),
            formats::parse::To<EatsCatalogPreparationTimeFeature>{});
  config.eats_catalog_place_storage_settings.min_preparation_minutes =
      std::chrono::minutes{min_preparation_minutes};
  return config;
}

struct PreparationTestCase {
  int preparation_minutes, extra_minutes;
  std::string expected;
  int min_preparation_minutes{1};
  std::string_view config{kPreparationTimeConfig};
};

void TestPreparationTimeFeature(const PreparationTestCase& tc) {
  const auto config = PatchConfig(tc.config, tc.min_preparation_minutes);
  const auto localizer_ptr = MakeTestLocalizer();
  const auto context =
      eats_catalog::models::Context({}, std::nullopt, localizer_ptr);

  PreparationTimeFeature feature(context, config);

  eats_catalog::models::PlaceInfo place_info;
  place_info.times.preparation =
      std::chrono::seconds{tc.preparation_minutes * 60};
  place_info.times.extra_preparation =
      std::chrono::seconds{tc.extra_minutes * 60};
  eats_catalog::models::Place place{place_info};
  PlaceListItem view;
  feature.Modify(view, place, render::Context{});

  const auto& badge = view.payload.data.features.badge;
  if (!badge.has_value()) {
    FAIL();
  }
  auto result = badge.value().text;
  result = result.substr(result.find(',') + 1);
  EXPECT_EQ(result, tc.expected);
}

void TestPreparationTimeFeature(const std::vector<PreparationTestCase>& cases) {
  for (const auto& tc : cases) {
    TestPreparationTimeFeature(tc);
  }
}

}  // namespace

UTEST(TestPreparationTimeFeature, Simple) {
  PreparationTestCase tc{
      2,                       // preparation
      10,                      // extra
      R"({"n_minutes":"12"})"  // expected
  };
  TestPreparationTimeFeature(tc);
}

UTEST(TestPreparationTimeFeature, ZeroPreparationTime) {
  std::vector<PreparationTestCase> cases{
      {
          0,                       // preparation
          0,                       // extra
          R"({"n_minutes":"5"})",  // expected
          5                        // min_preparation_minutes
      },
      {
          0,                        // preparation
          10,                       // extra
          R"({"n_minutes":"11"})",  // expected
          1                         // min_preparation_minutes
      }};
  TestPreparationTimeFeature(cases);
}

UTEST(TestPreparationTimeFeature, RoundingPolicy) {
  std::vector<PreparationTestCase> cases{
      {
          3,                      // preparation
          0,                      // extra
          R"({"n_minutes":"3"})"  // expected
      },
      {
          15,                      // preparation
          0,                       // extra
          R"({"n_minutes":"15"})"  // expected
      },
      {
          16,                      // preparation
          0,                       // extra
          R"({"n_minutes":"20"})"  // expected
      },
      {
          39,                      // preparation
          10,                      // extra
          R"({"n_minutes":"50"})"  // expected
      },
      {
          60,                      // preparation
          1,                       // extra
          R"({"n_minutes":"70"})"  // expected
      },
      {
          121,                      // preparation
          0,                        // extra
          R"({"n_minutes":"140"})"  // expected
      },
  };
  TestPreparationTimeFeature(cases);
}

}  // namespace handlers::common_map
