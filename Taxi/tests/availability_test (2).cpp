#include <userver/utest/utest.hpp>

#include <userver/dynamic_config/storage_mock.hpp>

#include <taxi_config/variables/BILLING_CORP_ENABLED.hpp>
#include <taxi_config/variables/BILLING_CREDITCARD_ENABLED.hpp>
#include <taxi_config/variables/GEOAREAS_CLIENT_QOS.hpp>
#include <taxi_config/variables/STATISTICS_CLIENT_QOS.hpp>
#include <taxi_config/variables/SUBVENTION_GEOAREAS_CLIENT_QOS.hpp>
#include <taxi_config/variables/TARIFFS_CLIENT_QOS.hpp>
#include <taxi_config/variables/TYPED_GEOAREAS_CLIENT_QOS.hpp>

#include "utils/availability.hpp"

using taxi_tariffs::models::Category;
using taxi_tariffs::models::TariffSettings;
using utils::availability::kCard;
using utils::availability::kCash;
using utils::availability::kCorp;

namespace {

constexpr auto kBitcoin = "bitcoin";  // fake payment method for testing

constexpr auto ENABLED = true;
constexpr auto DISABLED = false;

constexpr auto AVAILABLE = true;
constexpr auto UNAVAILABLE = false;

dynamic_config::StorageMock GetConfig(bool corp_enabled = true,
                                      bool card_enabled = true) {
  return {
      {taxi_config::BILLING_CORP_ENABLED, corp_enabled},
      {taxi_config::BILLING_CREDITCARD_ENABLED, card_enabled},
      {taxi_config::GEOAREAS_CLIENT_QOS, {}},
      {taxi_config::STATISTICS_CLIENT_QOS, {}},
      {taxi_config::SUBVENTION_GEOAREAS_CLIENT_QOS, {}},
      {taxi_config::TARIFFS_CLIENT_QOS, {}},
      {taxi_config::TYPED_GEOAREAS_CLIENT_QOS, {}},
  };
}

struct TestCase {
  std::string payment_method;
  bool billing_card_enabled;
  bool billing_corp_enabled;
  bool available_in_zone;
  bool available_in_category;
  std::vector<std::string> available_types_in_zone;
  std::vector<std::string> available_types_in_category;
};

class TestAvailability : public ::testing::TestWithParam<TestCase> {};

const auto kTestCases = testing::ValuesIn<TestCase>({
    // simple
    {kCash, ENABLED, ENABLED, AVAILABLE, AVAILABLE, {kCash}, {kCash}},
    {kCard, ENABLED, ENABLED, AVAILABLE, AVAILABLE, {kCard}, {kCard}},
    {kCorp, ENABLED, ENABLED, AVAILABLE, AVAILABLE, {kCorp}, {kCorp}},
    // disabled by billing config
    {kCard, DISABLED, ENABLED, UNAVAILABLE, UNAVAILABLE, {kCard}, {kCard}},
    {kCorp, ENABLED, DISABLED, UNAVAILABLE, UNAVAILABLE, {kCorp}, {kCorp}},
    // disabled by zone
    {kCash, ENABLED, ENABLED, UNAVAILABLE, UNAVAILABLE, {kBitcoin}, {kCash}},
    {kCard, ENABLED, ENABLED, UNAVAILABLE, UNAVAILABLE, {kBitcoin}, {kCard}},
    {kCorp, ENABLED, ENABLED, UNAVAILABLE, UNAVAILABLE, {kBitcoin}, {kCorp}},
    // disabled by category
    {kCash, ENABLED, ENABLED, AVAILABLE, UNAVAILABLE, {kCash}, {kBitcoin}},
    {kCard, ENABLED, ENABLED, AVAILABLE, UNAVAILABLE, {kCard}, {kBitcoin}},
    {kCorp, ENABLED, ENABLED, AVAILABLE, UNAVAILABLE, {kCorp}, {kBitcoin}},
});

}  // namespace

TEST_P(TestAvailability, ParametrisedTest) {
  Category category;
  TariffSettings tariff_settings;

  const auto config = GetConfig(GetParam().billing_corp_enabled,
                                GetParam().billing_card_enabled);
  tariff_settings.payment_options = GetParam().available_types_in_zone;
  category.restrict_by_payment_type = GetParam().available_types_in_category;

  const auto& availability = utils::availability::GetAvailability(
      category, tariff_settings, config.GetSnapshot(),
      GetParam().payment_method);

  handlers::PaymentMethodAvailability expected_result = {
      GetParam().available_in_category, GetParam().available_in_zone};

  EXPECT_EQ(availability, expected_result);
}

INSTANTIATE_TEST_SUITE_P(/*empty*/, TestAvailability, kTestCases);
