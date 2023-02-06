#include <gtest/gtest.h>

#include <memory>
#include <string>
#include <utility>
#include <vector>

#include <userver/utils/shared_readable_ptr.hpp>

#include <subvention-dependencies/caches/tariff_cache.hpp>
#include <subvention-dependencies/caches/tariffs_fwd.hpp>
#include <subvention-dependencies/models/tariffs.hpp>

#include <subvention-rule-utils/helpers/tariff_zones.hpp>

// TODO: убрать тесты старой функции
// https://st.yandex-team.ru/EFFICIENCYDEV-19135
namespace sru = subvention_rule_utils;
namespace sdm = subvention_dependencies::models;
using HomeZone = sdm::HomeZone;
using ActivationZone = sdm::ActivationZone;

sdm::TariffsMap CreateMap(std::vector<std::pair<std::string, std::string>>
                              home_and_activation_zones) {
  sdm::TariffsMap result;
  for (auto& [home_zone, activation_zone] : home_and_activation_zones) {
    sdm::Tariffs tariffs;
    tariffs.home_zone = home_zone;
    tariffs.activation_zone = std::move(activation_zone);
    result[std::move(home_zone)] = std::move(tariffs);
  }
  return result;
}

struct TakeActiveTariffZonesData {
  std::vector<std::string> tariff_zones_names;
  sru::helpers::TariffZones expected;
};

struct TestTakeActiveTariffZonesParametrized
    : public testing::TestWithParam<TakeActiveTariffZonesData> {};

TEST_P(TestTakeActiveTariffZonesParametrized, Tests) {
  auto [tariff_zones_names, expected] = GetParam();
  static const std::unordered_set<std::string> invalid_activation_zones = {
      "not_ok1", "not_ok2"};

  static const caches::TariffCacheTraits::DataType old_tariff_cache = {
      {HomeZone("tz1"), {ActivationZone("ok1"), HomeZone("tz1")}},
      {HomeZone("tz2"), {ActivationZone("ok2"), HomeZone("tz2")}},
      {HomeZone("tz3"), {ActivationZone("not_ok1"), HomeZone("tz3")}}};

  const auto active_result = sru::helpers::TakeOnlyActiveTariffZones(
      tariff_zones_names, old_tariff_cache, false, invalid_activation_zones);
  ASSERT_EQ(active_result, expected);

  const auto tmp_ptr = std::make_shared<const sdm::TariffsMap>(
      CreateMap({{"tz1", "ok1"}, {"tz2", "ok2"}, {"tz3", "not_ok1"}}));
  const utils::SharedReadablePtr ptr(tmp_ptr);

  const auto split_result =
      sru::helpers::SplitTariffZones(std::move(tariff_zones_names), ptr, false,
                                     invalid_activation_zones)
          .active;
  ASSERT_EQ(split_result, expected);
}

const std::vector<TakeActiveTariffZonesData> kTakeActiveTariffZonesData = {
    {{}, {}},
    {{"bad_tz_name"}, {}},
    {{"tz1"}, {"tz1"}},
    {{"tz3"}, {}},
    {{"tz2", "tz3", "tz1"}, {"tz1", "tz2"}}};

INSTANTIATE_TEST_SUITE_P(TestTakeActiveTariffZonesParametrized,
                         TestTakeActiveTariffZonesParametrized,
                         ::testing::ValuesIn(kTakeActiveTariffZonesData));

struct TestInvalidTariffZonesParametrized
    : public testing::TestWithParam<TakeActiveTariffZonesData> {};

TEST_P(TestInvalidTariffZonesParametrized, TestInvalid) {
  auto [tariff_zones_names, expected] = GetParam();
  static const std::unordered_set<std::string> invalid_activation_zones = {};

  static const caches::TariffCacheTraits::DataType old_tariff_cache = {
      {HomeZone("tz1"), {ActivationZone("ok1_activation"), HomeZone("tz1")}},
      {HomeZone("tz2"), {ActivationZone("ok2_activation"), HomeZone("tz2")}},
      {HomeZone("tz3"), {ActivationZone("tz3"), HomeZone("tz3")}}};

  const auto active_result = sru::helpers::TakeOnlyActiveTariffZones(
      tariff_zones_names, old_tariff_cache, true, invalid_activation_zones);
  ASSERT_EQ(active_result, expected);

  const auto tmp_ptr = std::make_shared<const sdm::TariffsMap>(CreateMap(
      {{"tz1", "ok1_activation"}, {"tz2", "ok2_activation"}, {"tz3", "tz3"}}));
  const utils::SharedReadablePtr ptr(tmp_ptr);

  const auto split_result =
      sru::helpers::SplitTariffZones(std::move(tariff_zones_names), ptr, true,
                                     invalid_activation_zones)
          .active;
  ASSERT_EQ(split_result, expected);
}

const std::vector<TakeActiveTariffZonesData> kInvalidTariffZonesData = {
    {{"tz3"}, {}}, {{"tz2", "tz3", "tz1"}, {"tz1", "tz2"}}};

INSTANTIATE_TEST_SUITE_P(TestInvalidTariffZonesParametrized,
                         TestInvalidTariffZonesParametrized,
                         ::testing::ValuesIn(kInvalidTariffZonesData));

struct SplittingTariffZonesData {
  std::vector<std::string> tariff_zones_names;
  sru::helpers::TariffZonesWithStatus expected;
};

struct TestSplittingTariffZonesParametrized
    : public testing::TestWithParam<SplittingTariffZonesData> {};

TEST_P(TestSplittingTariffZonesParametrized, TestInvalid) {
  auto [tariff_zones_names, expected] = GetParam();
  static const std::unordered_set<std::string> invalid_activation_zones = {
      "not_ok2_activation"};

  const auto tmp_ptr = std::make_shared<const sdm::TariffsMap>(
      CreateMap({{"tz1", "ok1_activation"},
                 {"tz2", "not_ok2_activation"},
                 {"tz3", "tz3"}}));
  const utils::SharedReadablePtr ptr(tmp_ptr);

  const auto result = sru::helpers::SplitTariffZones(
      std::move(tariff_zones_names), ptr, true, invalid_activation_zones);
  ASSERT_EQ(result.active, expected.active);
  ASSERT_EQ(result.inactive, expected.inactive);
}

const std::vector<SplittingTariffZonesData> kSplittingTariffZonesData = {
    {{}, {{}, {}}},
    {{"tz1"}, {{"tz1"}, {}}},
    {{"tz2"}, {{}, {"tz2"}}},
    {{"tz2", "tz3", "tz1", "not_in_cache_tz"},
     {{"tz1"}, {"tz2", "tz3", "not_in_cache_tz"}}}};

INSTANTIATE_TEST_SUITE_P(TestSplittingTariffZonesParametrized,
                         TestSplittingTariffZonesParametrized,
                         ::testing::ValuesIn(kSplittingTariffZonesData));
