#include <gtest/gtest.h>

#include <cars_catalog/models/price_age_model.hpp>

namespace cars_catalog::models {
bool operator==(const PriceAge& left, const PriceAge& right) {
  return left.price == right.price && left.age == right.age;
}
}  // namespace cars_catalog::models

TEST(ClassifierTest, Serializer) {
  using namespace cars_catalog::models;
  PriceAgeMap model = {{NormalizedBrandModelYear{"normalized_model_code1",
                                                 "normalized_mark_code1", 2017},
                        PriceAge{100000, 2}},
                       {NormalizedBrandModelYear{"normalized_model_code2",
                                                 "normalized_mark_code2", 2018},
                        PriceAge{200000, 1}},
                       {NormalizedBrandModelYear{"normalized_model_code3",
                                                 "normalized_mark_code3", 2019},
                        PriceAge{300000, 0}}};
  EXPECT_EQ(model,
            Parse(Serialize(model, formats::serialize::To<std::string>{}),
                  formats::parse::To<PriceAgeMap>{}));
}
