#include <gtest/gtest.h>

#include <pricing-functions/helpers/adapted_io.hpp>
#include <pricing-functions/lang/internal/backend_variables_io.hpp>
#include <userver/formats/json.hpp>
#include <userver/formats/json/serialize_duration.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/formats/serialize/common_containers.hpp>

namespace {
const auto kDefaultJson = R"json(
{
   "discount" : {
      "id" : "ID",
      "restrictions" : {
         "max_discount_coeff" : 0.2,
         "min_discount_coeff" : 0.1,
         "driver_less_coeff" : 0.3
      }
   },
   "cashback_discount" : {
      "id" : "ID",
      "restrictions" : {
         "max_discount_coeff" : 0.2,
         "min_discount_coeff" : 0.1,
         "driver_less_coeff" : 0.3
      }
   },
   "surge_params" : {
      "value" : 1.0,
      "value_raw" : 1.0,
      "value_smooth" : 1.0
   },
   "zone" : "spb",
   "category" : "econom",
   "rounding_factor" : 1.0,
   "tariff" : {
      "boarding_price" : 0.0,
      "minimum_price" : 0.0,
      "waiting_price" : {
         "free_waiting_time" : 0.0,
         "price_per_minute" : 0.0
      },
      "requirement_prices" : {}
   },
   "category_data" : {
      "fixed_price" : false,
      "paid_cancel_waiting_time_limit" : 600.0,
      "min_paid_supply_price_for_paid_cancel" : 20.0,
      "decoupling" : false
   },
   "exps": {},
   "country_code2" : "RU",
   "requirements" : {
      "simple" : [],
      "select" : {}
   },
   "user_data" : {
      "has_yaplus" : false,
      "has_cashback_plus" : false
   },
   "user_tags" : [],
   "editable_requirements": {
       "luggage_count": {
          "default_value": 1,
          "max_value": 3,
          "min_value": 0
        },
        "third_passenger": {
          "default_value": 1,
          "max_value": 1,
          "min_value": 0
        }
   },
   "waypoints_count": 2,
   "forced_skip_label": "without_surge"
}
)json";

}

TEST(BackendVariablesIo, ParseSerialize) {
  auto doc = formats::json::FromString(kDefaultJson);
  const auto vars = doc.As<lang::variables::BackendVariables>();
  const auto doc2 = formats::json::ValueBuilder(vars).ExtractValue();
  EXPECT_EQ(doc, doc2);
}
