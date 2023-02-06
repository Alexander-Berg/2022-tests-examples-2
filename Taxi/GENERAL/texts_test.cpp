#include "texts.hpp"

#include <optional>

#include <cctz/time_zone.h>
#include <gtest/gtest.h>

#include <models/place.hpp>
#include "localization/localization.hpp"

namespace {

using eats_catalog::models::Context;
using eats_catalog::models::DeliveryCondition;
using eats_catalog::models::DeliveryType;
using eats_catalog::models::Money;
using eats_places_availability::Schedule;
using handlers::eats_catalog_v1_slug_slug::get::DeliveryConditionText;
using handlers::eats_catalog_v1_slug_slug::get::DeliveryThresholdText;
using handlers::eats_catalog_v1_slug_slug::get::ScheduleTextFor;
using handlers::eats_catalog_v1_slug_slug::get::WeightThresholdText;

namespace keys = eats_catalog::localization::keys;

const std::unordered_map<eats_catalog::localization::TankerKey, std::string>
    kTranslations = {
        {keys::slug::delivery_conditions::kFree, "Бесплатно"},
        {keys::slug::delivery_conditions::kOneThreshold,
         "Доставка {n_price} {s_currency_sign}"},
        {keys::slug::delivery_conditions::kTwoThresholdsWithFreeNative,
         "Бесплатно при заказе от {free_order_price} {s_currency_sign}"},
        {keys::slug::delivery_conditions::kTwoThresholdsWithFreeMarketplace,
         "Доставка {delivery_cost} {s_currency_sign}. Бесплатно при заказе от "
         "{free_order_price} {s_currency_sign}"},
        {keys::slug::delivery_conditions::kTwoThresholds,
         "Доставка {delivery_cost} {s_currency_sign} на заказ от {order_price} "
         "{s_currency_sign}"},
        {keys::slug::delivery_conditions::kManyThresholdsWithFree,
         "Доставка {min_delivery_cost}–{max_delivery_cost} {s_currency_sign}. "
         "Бесплатно при заказе от {order_price} {s_currency_sign}"},
        {keys::slug::delivery_conditions::kManyThresholds,
         "Доставка {min_delivery_cost}–{max_delivery_cost} {s_currency_sign}"},
        {keys::slug::delivery_and_assembly_conditions::kOneThreshold,
         "Доставка и сборка {n_price} {s_currency_sign}"},
        {keys::slug::delivery_and_assembly_conditions::kTwoThresholds,
         "Доставка и сборка {delivery_cost} {s_currency_sign} на заказ от "
         "{order_price} {s_currency_sign}"},
        {keys::slug::delivery_and_assembly_conditions::kManyThresholds,
         "Доставка и сборка {min_delivery_cost}–{max_delivery_cost} "
         "{s_currency_sign}"},
        {keys::slug::delivery_conditions::text::kOnOrderFrom,
         "на заказ от {n_price} {s_currency_sign}"},
        {keys::slug::delivery_conditions::text::kOnOrderUpTo,
         "на заказ до {n_price} {s_currency_sign}"},
        {keys::slug::delivery_conditions::text::kOnOrder,
         "на заказ {min}-{max} {s_currency_sign}"},
        {keys::slug::schedule::kFromTo, "с {from} до {to}"},
        {keys::slug::schedule::kWorkingTime, "Режим работы"},
        {keys::slug::messages::kLimits, "Лимиты"},
        {keys::slug::messages::kDeliveryAndAssemblyConditionsTitle,
         "Условия сборки и доставки"},
        {keys::slug::messages::kDeliveryAndAssemblyConditionsFooter,
         "В стоимость входит доставка и сборка заказа"},
};

const std::string kCurrencySign = "^";
const cctz::time_zone utc = cctz::utc_time_zone();

std::chrono::system_clock::time_point CreateTime(
    int y, int m = 1, int d = 1, int hh = 0, int mm = 0,
    const cctz::time_zone& tz = utc) {
  return cctz::convert(cctz::civil_minute(y, m, d, hh, mm), tz);
}

Context MakeContext() {
  const auto localizer =
      eats_catalog::localization::MakeTestLocalizer(kTranslations);
  return Context{
      {},            // request
      std::nullopt,  // offer
      localizer,     // localizer
  };
}

}  // namespace

TEST(DeliveryConditionText, Empty) {
  const std::vector<DeliveryCondition> conditions = {};

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, std::nullopt, kCurrencySign);

  ASSERT_EQ(std::nullopt, result);
}

TEST(DeliveryConditionText, NativeFreeDelivery) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),  // order_cost
          Money(0),  // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, std::nullopt, kCurrencySign);

  ASSERT_EQ("Бесплатно", result);
}

TEST(DeliveryConditionText, MarketFreeDelivery) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),  // order_cost
          Money(0),  // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result =
      DeliveryConditionText(context, conditions, DeliveryType::kMarketplace,
                            std::nullopt, kCurrencySign);

  ASSERT_EQ("Бесплатно", result);
}

TEST(DeliveryConditionText, NativeSingleCondition) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(100),  // order_cost
          Money(50),   // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, std::nullopt, kCurrencySign);

  ASSERT_EQ("Доставка 50 ^", result);
}

TEST(DeliveryConditionText, MarketSingleCondition) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(100),  // order_cost
          Money(50),   // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result =
      DeliveryConditionText(context, conditions, DeliveryType::kMarketplace,
                            std::nullopt, kCurrencySign);

  ASSERT_EQ("Доставка 50 ^", result);
}

TEST(DeliveryConditionText, NativeTwoConditions) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(100),  // delivery_cost
      },
      {
          Money(1000),  // order_cost
          Money(50),    // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, std::nullopt, kCurrencySign);

  ASSERT_EQ("Доставка 50 ^ на заказ от 1000 ^", result);
}

TEST(DeliveryConditionText, MarketTwoConditions) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(100),  // delivery_cost
      },
      {
          Money(1000),  // order_cost
          Money(50),    // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result =
      DeliveryConditionText(context, conditions, DeliveryType::kMarketplace,
                            std::nullopt, kCurrencySign);

  ASSERT_EQ("Доставка 50 ^ на заказ от 1000 ^", result);
}

TEST(DeliveryConditionText, NativeTwoConditionsWithFree) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(100),  // delivery_cost
      },
      {
          Money(5000),  // order_cost
          Money(0),     // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, std::nullopt, kCurrencySign);

  ASSERT_EQ("Бесплатно при заказе от 5000 ^", result);
}

TEST(DeliveryConditionText, MarketTwoConditionsWithFree) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(100),  // delivery_cost
      },
      {
          Money(5000),  // order_cost
          Money(0),     // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result =
      DeliveryConditionText(context, conditions, DeliveryType::kMarketplace,
                            std::nullopt, kCurrencySign);

  ASSERT_EQ("Доставка 100 ^. Бесплатно при заказе от 5000 ^", result);
}

TEST(DeliveryConditionText, NativeThreeConditionsWithFree) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(100),  // delivery_cost
      },
      {
          Money(1000),  // order_cost
          Money(50),    // delivery_cost
      },
      {
          Money(2000),  // order_cost
          Money(0),     // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, std::nullopt, kCurrencySign);

  ASSERT_EQ("Доставка 50–100 ^. Бесплатно при заказе от 2000 ^", result);
}

TEST(DeliveryConditionText, MarketThreeConditions) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(100),  // delivery_cost
      },
      {
          Money(1000),  // order_cost
          Money(50),    // delivery_cost
      },
      {
          Money(2000),  // order_cost
          Money(0),     // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result =
      DeliveryConditionText(context, conditions, DeliveryType::kMarketplace,
                            std::nullopt, kCurrencySign);

  ASSERT_EQ("Доставка 50–100 ^. Бесплатно при заказе от 2000 ^", result);
}

TEST(DeliveryConditionText, NativeFourConditions) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(200),  // delivery_cost
      },
      {
          Money(2000),  // order_cost
          Money(100),   // delivery_cost
      },
      {
          Money(3000),  // order_cost
          Money(50),    // delivery_cost
      },
      {
          Money(4000),  // order_cost
          Money(50),    // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, std::nullopt, kCurrencySign);

  ASSERT_EQ("Доставка 50–200 ^", result);
}

TEST(DeliveryConditionText, MarketFourConditions) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(200),  // delivery_cost
      },
      {
          Money(2000),  // order_cost
          Money(100),   // delivery_cost
      },
      {
          Money(3000),  // order_cost
          Money(50),    // delivery_cost
      },
      {
          Money(4000),  // order_cost
          Money(50),    // delivery_cost
      },
  };
  const auto context = MakeContext();
  const auto result =
      DeliveryConditionText(context, conditions, DeliveryType::kMarketplace,
                            std::nullopt, kCurrencySign);

  ASSERT_EQ("Доставка 50–200 ^", result);
}

TEST(DeliveryConditionText, SingleConditionFreeWithAssembly) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),  // order_cost
          Money(0),  // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, Money(100), kCurrencySign);

  ASSERT_EQ("Доставка и сборка 100 ^", result);
}

TEST(DeliveryConditionText, SingleConditionWithAssembly) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(300),  // order_cost
          Money(99),   // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, Money(100), kCurrencySign);

  ASSERT_EQ("Доставка и сборка 199 ^", result);
}

TEST(DeliveryConditionText, TwoConditionWithAssembly) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(100),  // delivery_cost
      },
      {
          Money(1000),  // order_cost
          Money(50),    // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, Money(100), kCurrencySign);

  ASSERT_EQ("Доставка и сборка 150 ^ на заказ от 1000 ^", result);
}

TEST(DeliveryConditionText, FourConditionWithAssembly) {
  const std::vector<DeliveryCondition> conditions = {
      {
          Money(0),    // order_cost
          Money(200),  // delivery_cost
      },
      {
          Money(2000),  // order_cost
          Money(100),   // delivery_cost
      },
      {
          Money(3000),  // order_cost
          Money(50),    // delivery_cost
      },
      {
          Money(4000),  // order_cost
          Money(50),    // delivery_cost
      },
  };

  const auto context = MakeContext();
  const auto result = DeliveryConditionText(
      context, conditions, DeliveryType::kNative, Money(200), kCurrencySign);

  ASSERT_EQ("Доставка и сборка 250–400 ^", result);
}

TEST(DeliveryThresholdText, FromMin) {
  const auto context = MakeContext();
  const auto result =
      DeliveryThresholdText(context, Money(100), std::nullopt, kCurrencySign);
  ASSERT_EQ("на заказ от 100 ^", result);
}

TEST(DeliveryThresholdText, ToMax) {
  const auto context = MakeContext();
  const auto result =
      DeliveryThresholdText(context, Money(0), Money(200), kCurrencySign);
  ASSERT_EQ("на заказ до 200 ^", result);
}

TEST(DeliveryThresholdText, Interval) {
  const auto context = MakeContext();
  const auto result =
      DeliveryThresholdText(context, Money(100), Money(200), kCurrencySign);
  ASSERT_EQ("на заказ 100-200 ^", result);
}

TEST(ScheduleTextFor, Empty) {
  const Schedule schedule{};
  const auto context = MakeContext();
  const auto result = ScheduleTextFor(
      context, CreateTime(2021, 2, 12, 21, 20, utc), utc, schedule);

  ASSERT_EQ(std::nullopt, result);
}

TEST(ScheduleTextFor, TooEarly) {
  const Schedule schedule{
      {
          CreateTime(2021, 2, 13, 8, 20, utc),   // start
          CreateTime(2021, 2, 13, 12, 20, utc),  // end
      },
  };
  const auto context = MakeContext();
  const auto result = ScheduleTextFor(
      context, CreateTime(2021, 2, 11, 21, 20, utc), utc, schedule);

  ASSERT_EQ(std::nullopt, result);
}

TEST(ScheduleTextFor, TooLate) {
  const Schedule schedule{
      {
          CreateTime(2021, 2, 15, 8, 20, utc),   // start
          CreateTime(2021, 2, 15, 12, 20, utc),  // end
      },
  };
  const auto context = MakeContext();
  const auto result = ScheduleTextFor(
      context, CreateTime(2021, 2, 16, 21, 20, utc), utc, schedule);

  ASSERT_EQ(std::nullopt, result);
}

TEST(ScheduleTextFor, DayOverlap) {
  const Schedule schedule{
      {
          CreateTime(2021, 2, 12, 21, 20, utc),  // start
          CreateTime(2021, 2, 14, 12, 20, utc),  // end
      },
  };
  const auto context = MakeContext();
  const auto result = ScheduleTextFor(
      context, CreateTime(2021, 2, 13, 21, 20, utc), utc, schedule);

  ASSERT_EQ("Режим работы: с 00:00 до 24:00", result);
}

TEST(ScheduleTextFor, SecondHaflOfDay) {
  const Schedule schedule{
      {
          CreateTime(2021, 2, 13, 8, 20, utc),   // start
          CreateTime(2021, 2, 14, 12, 20, utc),  // end
      },
  };
  const auto context = MakeContext();
  const auto result = ScheduleTextFor(
      context, CreateTime(2021, 2, 13, 21, 20, utc), utc, schedule);

  ASSERT_EQ("Режим работы: с 08:20 до 24:00", result);
}

TEST(ScheduleTextFor, FirstHaflOfDay) {
  const Schedule schedule{
      {
          CreateTime(2021, 2, 12, 8, 20, utc),   // start
          CreateTime(2021, 2, 13, 12, 20, utc),  // end
      },
  };
  const auto context = MakeContext();
  const auto result = ScheduleTextFor(
      context, CreateTime(2021, 2, 13, 21, 20, utc), utc, schedule);

  ASSERT_EQ("Режим работы: с 00:00 до 12:20", result);
}

TEST(ScheduleTextFor, InTheDay) {
  const Schedule schedule{
      {
          CreateTime(2021, 2, 13, 8, 20, utc),   // start
          CreateTime(2021, 2, 13, 12, 20, utc),  // end
      },
  };
  const auto context = MakeContext();
  const auto result = ScheduleTextFor(
      context, CreateTime(2021, 2, 13, 21, 20, utc), utc, schedule);

  ASSERT_EQ("Режим работы: с 08:20 до 12:20", result);
}

TEST(ScheduleTextFor, Multiple) {
  const Schedule schedule{
      {
          CreateTime(2021, 2, 12, 23, 20, utc),  // start
          CreateTime(2021, 2, 13, 1, 20, utc),   // end
      },
      {
          CreateTime(2021, 2, 13, 5, 43, utc),  // start
          CreateTime(2021, 2, 13, 9, 32, utc),  // end
      },
      {
          CreateTime(2021, 2, 13, 18, 30, utc),  // start
          CreateTime(2021, 2, 13, 18, 30, utc),  // end
      },
      {
          CreateTime(2021, 2, 13, 19, 30, utc),  // start
          CreateTime(2021, 2, 13, 20, 30, utc),  // end
      },
      {
          CreateTime(2021, 2, 13, 23, 30, utc),  // start
          CreateTime(2021, 2, 14, 23, 30, utc),  // end
      },
  };
  const auto context = MakeContext();
  const auto result = ScheduleTextFor(
      context, CreateTime(2021, 2, 13, 21, 20, utc), utc, schedule);

  ASSERT_EQ(
      "Режим работы: с 00:00 до 01:20; с 05:43 до 09:32; с 19:30 до 20:30; с "
      "23:30 до 24:00",
      result);
}
