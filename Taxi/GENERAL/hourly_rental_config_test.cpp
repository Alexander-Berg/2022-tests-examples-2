#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/hourly_rental_config.hpp>

TEST(TestHourlyRental, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& hourly_rental = config.Get<config::HourlyRental>();
  ASSERT_FALSE(hourly_rental.use_requirement_intervals);
  ASSERT_FALSE(hourly_rental.crutch_destinations);
}
