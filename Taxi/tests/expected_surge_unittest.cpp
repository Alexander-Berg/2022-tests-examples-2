#include <gtest/gtest.h>
#include <fstream>
#include "models/expected_surge/v1/features.hpp"
#include "models/expected_surge/v1/request.hpp"

TEST(ExpectedSurge, FeatureExtractor) {
  //  request
  ml::expected_surge::v1::RequestData request;
  request.due_time = "2019-06-30T19:34:18.0000+0000";
  request.geopoint.lon = 37.48683708937394;
  request.geopoint.lat = 55.53387231033457;
  request.surge_id = "28666abeeaf74db290f7cdcddd35d6d8";
  request.nearest_zone = "moscow";
  ml::expected_surge::v1::ClassInfo classInfo;
  classInfo.tariff_class = "econom";

  std::vector<float> correct_features = {
      // time shifts
      0.5450694444444445, 0.8784027777777778, 0.21173611111111112,
      0.8154861111111111, 0.14881944444444445, 0.48215277777777776,
      // geo combinations
      37.48683708937394, 55.53387231033457, 53.72916878823851,
      51.924465266142455, 50.11976174404638, 48.315058221950316,
      46.51035469985426, 44.7056511777582, 42.90094765566214, 41.09624413356607,
      39.291540611470005, 233.66374484973724, 231.8084661099824,
      229.9679181929504, 228.1419841366276, 226.33054790767227,
      224.5334943940422, 222.75070939767906, 220.98207962725152,
      219.22749269095587};
  auto num_features =
      ml::expected_surge::v1::GetNumFeatures(request, classInfo);

  ASSERT_EQ(num_features.size(), correct_features.size());
  for (size_t i = 0; i < num_features.size(); ++i) {
    ASSERT_FLOAT_EQ(correct_features[i], num_features[i]);
  }

  std::vector<std::string> correct_cat_features = {
      "moscow", "28666abeeaf74db290f7cdcddd35d6d8", "econom"};
  auto cat_features =
      ml::expected_surge::v1::GetCatFeatures(request, classInfo);

  ASSERT_EQ(cat_features.size(), correct_cat_features.size());
  for (size_t i = 0; i < cat_features.size(); ++i) {
    ASSERT_EQ(correct_cat_features[i], cat_features[i]);
  }
}
