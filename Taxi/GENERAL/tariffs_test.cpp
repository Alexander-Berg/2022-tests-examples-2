#include <gtest/gtest.h>

#include "tariffs.cpp"

#include <logging/logger.hpp>
#include <models/tariffs.hpp>

std::vector<tariff::Interval> SingleIntervals() {
  return {tariff::Interval{0, std::numeric_limits<double>::max(), 10,
                           tariff::IntervalPaymentMode::Prepay, 1}};
}

std::vector<tariff::Interval> RequirementIntervals(
    const boost::optional<double>& begin) {
  if (!begin) return {};
  return {tariff::Interval{*begin, std::numeric_limits<double>::max(), 10,
                           tariff::IntervalPaymentMode::Prepay, 1}};
}

tariff::PriceObject BuildPriceObject(
    const std::vector<tariff::Interval>& time_intervals,
    const std::vector<tariff::Interval>& distance_intervals) {
  tariff::PriceObject result;
  result.time_price_intervals = time_intervals;
  result.distance_price_intervals = distance_intervals;
  result.time_price_intervals_meter_id = 5;
  result.distance_price_intervals_meter_id = 6;
  return result;
}

std::vector<tariff::SpecialTaximeter> BuildSpecialTaximeter(
    const std::vector<tariff::Interval>& time_intervals,
    const std::vector<tariff::Interval>& distance_intervals) {
  tariff::SpecialTaximeter taximeter;
  taximeter.zone_name = "moscow";
  taximeter.price = BuildPriceObject(time_intervals, distance_intervals);
  return {taximeter};
}

tariff::RequirementTariffPrice BuildRequirementTariffPrice(
    const boost::optional<double>& included_time,
    const boost::optional<double>& included_distance) {
  tariff::RequirementTariffPrice result;
  result.included_time = included_time;
  result.included_distance = included_distance;
  result.time_multiplier = 1.0;
  result.distance_multiplier = 1.0;
  result.special_taximeters =
      BuildSpecialTaximeter(RequirementIntervals(included_time),
                            RequirementIntervals(included_distance));
  return result;
}

std::vector<tariff::RequirementPrice> BuildTariffRequirementPrices(
    const boost::optional<double>& included_time,
    const boost::optional<double>& included_distance) {
  tariff::RequirementPrice booking_requirement;
  booking_requirement.type = "hourly_rental.1";
  booking_requirement.tariff_price =
      BuildRequirementTariffPrice(included_time, included_distance);

  std::vector<tariff::RequirementPrice> results;
  results.push_back(booking_requirement);
  return results;
}

tariff::Category BuildCategory(
    const std::vector<tariff::SpecialTaximeter>& taximeters,
    const std::vector<tariff::RequirementPrice>& requirement_prices) {
  return {
      "default_id",
      "default_tanker_key",
      "RUB",
      "moscow",
      {0, 0},
      {23, 59},
      tariff::DayType::Everyday,
      tariff::CategoryType::Application,
      {},                  // waiting_price
      0,                   // minimal
      0,                   // paid_cancel_fix
      true,                // add_minimal_to_paid_cancel
      taximeters,          // special_taximeters
      requirement_prices,  // requirement_prices
      {},                  // included_one_of
      {},                  // transfers
      {
          {tariff::TriggerType::OnFirstOccurence},
          {tariff::TriggerType::OnFirstOccurence},
          {tariff::TriggerType::OnFirstOccurence},
          {tariff::TriggerType::OnFirstOccurence},
          {tariff::TriggerType::OnFirstOccurence},
          {tariff::TriggerType::OnTransporting},
          {tariff::TriggerType::OnTransporting},
      },  // meters
  };
}

void CheckIntervals(const std::vector<tariff::Interval>& intervals,
                    const boost::optional<double>& value) {
  if (value) {
    const auto& expected_intervals = RequirementIntervals(value);
    ASSERT_EQ(*intervals.begin(), *expected_intervals.begin());
  } else {
    ASSERT_TRUE(intervals.empty());
  }
}

void CheckMakeRequirementCategory(
    const tariff::Category& category,
    const boost::optional<double>& included_time,
    const boost::optional<double>& included_distance) {
  LogExtra log_extra;
  const auto& requirement_categories =
      utils::helpers::MakeRequirementCategories(category, log_extra);
  ASSERT_EQ(requirement_categories.size(), 1u);
  for (const auto& [_, requirement_category] : requirement_categories) {
    ASSERT_TRUE(requirement_category.IsValid(log_extra));
  }

  const auto& booking_category = requirement_categories.begin()->second;
  ASSERT_DOUBLE_EQ(booking_category.minimal, 0.0);

  const auto& special_taximeters = booking_category.special_taximeters;
  const auto& price = (*special_taximeters.begin()).price;

  CheckIntervals(price.time_price_intervals, included_time);
  CheckIntervals(price.distance_price_intervals, included_distance);
}

TEST(Tariffs, DefaultCategories) {
  LogExtra log_extra;

  const auto& default_intervals = SingleIntervals();
  const auto& category = BuildCategory(
      BuildSpecialTaximeter(default_intervals, default_intervals), {});
  ASSERT_TRUE(category.IsValid(log_extra));

  const auto& special_taximeters = category.special_taximeters;
  const auto& price = (*special_taximeters.begin()).price;
  ASSERT_EQ(price.time_price_intervals.size(), 1u);
  ASSERT_EQ(price.distance_price_intervals.size(), 1u);

  const auto& requirement_categories =
      utils::helpers::MakeRequirementCategories(category, log_extra);
  ASSERT_TRUE(requirement_categories.empty());
}

TEST(Tariffs, SelectInterval) {
  const auto& default_intervals = SingleIntervals();
  const auto& default_special_taximeter =
      BuildSpecialTaximeter(default_intervals, default_intervals);
  const tariff::Category category1 = BuildCategory(
      default_special_taximeter, BuildTariffRequirementPrices(30, 30));
  CheckMakeRequirementCategory(category1, 30 * 60, 30 * 1000);
}

TEST(Tariffs, RecomputeSpecialTaximeterPriceIntervalsBasic) {
  using utils::helpers::RecomputeSpecialTaximeterPriceIntervals;
  using TestInput = std::vector<std::pair<double, double>>;

  auto test_simple = [](const TestInput& begin_prices, double new_beginning,
                        double multiplier, const TestInput& expected_output) {
    auto get_intervals = [](const TestInput& begins_prices) {
      auto intervals = std::vector<tariff::Interval>(begins_prices.size());
      for (size_t idx = 0; idx < begins_prices.size(); ++idx) {
        intervals[idx].begin = begins_prices[idx].first;
        intervals[idx].price = begins_prices[idx].second;
      }
      return intervals;
    };
    auto result = RecomputeSpecialTaximeterPriceIntervals(
        get_intervals(begin_prices), new_beginning, multiplier);
    auto expected = get_intervals(expected_output);

    ASSERT_EQ(result.size(), expected.size());
    for (size_t idx = 0; idx < result.size(); ++idx) {
      ASSERT_EQ(result[idx], expected[idx]);
    }
  };
  test_simple({}, 1., 2., {});
  test_simple({{0., 2.}}, 30., 2., {{30., 4.}});
  test_simple({{40., 2.}}, 30., 2., {{30., 4.}});
  test_simple({{0., 2.}, {25., 3.}}, 30., 2., {{30., 6.}});
  test_simple({{35., 2.}, {40., 3.}}, 30., 2., {{30., 4.}, {40., 6.}});
  test_simple({{35., 2.}, {40., 3.}}, 35., 2., {{35., 4.}, {40., 6.}});
}
