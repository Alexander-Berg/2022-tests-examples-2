#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <filters/infrastructure/fetch_categories/fetch_categories.hpp>
#include <testing/taxi_config.hpp>
#include "fetch_profile_classes.hpp"

const candidates::filters::FilterInfo kEmptyInfo;

TEST(FetchProfileClasses, Sample) {
  candidates::filters::Context context;
  const auto config = dynamic_config::GetDefaultSnapshot();
  candidates::filters::infrastructure::FetchProfileClasses filter(
      kEmptyInfo, models::Classes::GetAll(), {}, config);

  candidates::filters::infrastructure::FetchCar::Set(
      context, std::make_shared<const models::Car>());
  candidates::filters::infrastructure::FetchCategories::Set(
      context, models::Classes{"econom"});

  EXPECT_EQ(filter.Process({}, context), candidates::filters::Result::kAllow);
  const auto& profile_classes =
      candidates::filters::infrastructure::FetchProfileClasses::Get(context);
  EXPECT_GT(profile_classes.size(), 0);
  const auto& names = profile_classes.GetNames();
  EXPECT_NE(std::find(names.begin(), names.end(), "econom"), names.end());
}
