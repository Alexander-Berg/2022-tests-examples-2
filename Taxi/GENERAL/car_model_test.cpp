#include <gtest/gtest.h>

#include <cars_catalog/models/car_model.hpp>

namespace cars_catalog::models {
bool operator==(const BrandModelInfo& left, const BrandModelInfo& right) {
  return left.raw == right.raw &&
         left.normalized_model_code == right.normalized_model_code &&
         left.normalized_mark_code == right.normalized_mark_code &&
         left.corrected_model == right.corrected_model;
}
}  // namespace cars_catalog::models

TEST(CarModelTest, Serializer) {
  using namespace cars_catalog::models;
  BrandModelsMap model = {
      {RawBrandModel{"raw_model1", "raw_brand1"},
       BrandModelInfo{RawBrandModel{"raw_model1", "raw_brand1"},
                      "normalized_model_code1", "normalized_mark_code1",
                      "corrected_model1"}},
      {RawBrandModel{"raw_model2", "raw_brand2"},
       BrandModelInfo{RawBrandModel{"raw_model2", "raw_brand2"},
                      "normalized_model_code2", "normalized_mark_code2",
                      "corrected_model2"}},
      {RawBrandModel{"raw_model3", "raw_brand3"},
       BrandModelInfo{RawBrandModel{"raw_model3", "raw_brand3"},
                      "normalized_model_code3", "normalized_mark_code3",
                      "corrected_model3"}}};
  EXPECT_EQ(model,
            Parse(Serialize(model, formats::serialize::To<std::string>{}),
                  formats::parse::To<BrandModelsMap>{}));
}
