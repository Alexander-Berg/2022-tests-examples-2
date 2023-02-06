#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include "fetch_car_model.hpp"

namespace filters = candidates::filters;

namespace {

const filters::FilterInfo kEmptyInfo;

}  // namespace

TEST(FetchCarModelTest, Sample) {
  auto car = std::make_shared<models::Car>();
  car->raw_model = "brand_models";
  car->raw_brand = "raw_brand";

  filters::Context context;
  candidates::GeoMember member{{}, "dbid_uuid"};
  filters::infrastructure::FetchCar::Set(context, car);

  {
    auto brand_models =
        std::make_shared<cars_catalog::models::BrandModelsMap>();
    filters::infrastructure::FetchCarModel filter(kEmptyInfo, brand_models);
    EXPECT_EQ(filters::Result::kDisallow, filter.Process(member, context));
  }
  {
    auto brand_models =
        std::make_shared<cars_catalog::models::BrandModelsMap>();
    cars_catalog::models::BrandModelInfo target{
        cars_catalog::models::RawBrandModel{"brand_models", "raw_brand"},
        "model_code", "mark_code", "model"};
    brand_models->emplace(
        cars_catalog::models::RawBrandModel{"brand_models", "raw_brand"},
        target);
    filters::infrastructure::FetchCarModel filter(kEmptyInfo, brand_models);
    EXPECT_EQ(filters::Result::kAllow, filter.Process(member, context));
    EXPECT_EQ(
        target.corrected_model,
        filters::infrastructure::FetchCarModel::Get(context).corrected_model);
  }
}
