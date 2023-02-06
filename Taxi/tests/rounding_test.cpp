#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utils/shared_readable_ptr.hpp>

#include <taxi_config/variables/CURRENCY_ROUNDING_RULES.hpp>

#include <grocery-pricing/rounding.hpp>

namespace {
using grocery_pricing::Numeric;
using grocery_pricing::RoundedCurrencyValue;

const std::string kDefault = "__default__";
const std::string kILS = "ILS";
const std::string kGEL = "GEL";
const std::string kRUB = "RUB";
const std::string kAMD = "AMD";

dynamic_config::StorageMock GetConfig() {
  return {{taxi_config::CURRENCY_ROUNDING_RULES,
           {
               {kDefault, {{kDefault, 1}}},
               {kILS, {{kDefault, 0.1}}},
               {kGEL, {{kDefault, 0.2}}},
               {kRUB, {{kDefault, 1}}},
               {kAMD, {{kDefault, 100}}},
           }}};
}

TEST(TestRoundedValue, ILS) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();

  ASSERT_EQ(Numeric::FromFloatInexact(5.6),
            RoundedCurrencyValue(Numeric::FromFloatInexact(5.6), kILS, config,
                                 false));
  ASSERT_EQ(
      Numeric::FromFloatInexact(5.6),
      RoundedCurrencyValue(Numeric::FromFloatInexact(5.6), kILS, config, true));
  ASSERT_EQ(Numeric::FromFloatInexact(5.6),
            RoundedCurrencyValue(Numeric::FromFloatInexact(5.61), kILS, config,
                                 false));
  ASSERT_EQ(Numeric::FromFloatInexact(5.7),
            RoundedCurrencyValue(Numeric::FromFloatInexact(5.61), kILS, config,
                                 true));
}

TEST(TestRoundedValue, GEL) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();

  ASSERT_EQ(Numeric::FromFloatInexact(5.6),
            RoundedCurrencyValue(Numeric::FromFloatInexact(5.6), kGEL, config,
                                 false));
  ASSERT_EQ(
      Numeric::FromFloatInexact(5.6),
      RoundedCurrencyValue(Numeric::FromFloatInexact(5.6), kGEL, config, true));
  ASSERT_EQ(Numeric::FromFloatInexact(5.6),
            RoundedCurrencyValue(Numeric::FromFloatInexact(5.61), kGEL, config,
                                 false));
  ASSERT_EQ(Numeric::FromFloatInexact(5.8),
            RoundedCurrencyValue(Numeric::FromFloatInexact(5.61), kGEL, config,
                                 true));
}

TEST(TestRoundedValue, RUB) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();

  ASSERT_EQ(Numeric{1000},
            RoundedCurrencyValue(Numeric::FromFloatInexact(1000.0), kRUB,
                                 config, false));
  ASSERT_EQ(Numeric{1000},
            RoundedCurrencyValue(Numeric::FromFloatInexact(1000.0), kRUB,
                                 config, true));
  ASSERT_EQ(Numeric{1000},
            RoundedCurrencyValue(Numeric::FromFloatInexact(1000.137), kRUB,
                                 config, false));
  ASSERT_EQ(Numeric{1000},
            RoundedCurrencyValue(Numeric::FromFloatInexact(999.137), kRUB,
                                 config, true));
}

TEST(TestRoundedValue, AMD) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();

  ASSERT_EQ(Numeric{500}, RoundedCurrencyValue(Numeric::FromFloatInexact(500.0),
                                               kAMD, config, false));
  ASSERT_EQ(Numeric{500}, RoundedCurrencyValue(Numeric::FromFloatInexact(500.0),
                                               kAMD, config, true));
  ASSERT_EQ(Numeric{500},
            RoundedCurrencyValue(Numeric::FromFloatInexact(530.137), kAMD,
                                 config, false));
  ASSERT_EQ(Numeric{500},
            RoundedCurrencyValue(Numeric::FromFloatInexact(430.137), kAMD,
                                 config, true));
}

}  // namespace
