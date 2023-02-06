#include <gtest/gtest.h>
#include <fstream>
#include "models/ps_shift/ps_shift_model.hpp"

class PsShiftModelMock : public ml::ps_shift::PsShiftModel {
 public:
  std::vector<float> ExtractFeaturesMock(
      const std::string& datetime, const utils::geometry::Point& point,
      const ml::ps_shift::FeaturesExtractorParams& params) const {
    return ExtractFeatures(datetime, point, params);
  }
};

std::shared_ptr<ml::ps_shift::FeaturesExtractorParams> ReadParams(
    const std::string& filename) {
  std::ifstream in(std::string(SOURCE_DIR) + "/tests/static/" + filename);
  std::string content((std::istreambuf_iterator<char>(in)),
                      std::istreambuf_iterator<char>());

  return ml::ps_shift::FeaturesExtractorParamsParser()(content);
}

TEST(PsShift, ExtractFeatures) {
  const PsShiftModelMock model;

  const auto& params = ReadParams("ps_shift_config.json");
  ASSERT_EQ(6u, params->important_points.size());

  const auto& features = model.ExtractFeaturesMock(
      "2018-02-22T23:37:00-0300", {37.642684, 55.734850}, *params);
  ASSERT_EQ(features.size(), (31 + 2 * params->important_points.size()));

  // simple point assertions
  ASSERT_FLOAT_EQ(features[0], 37.642684);
  ASSERT_FLOAT_EQ(features[1], 55.734850);

  // 2-21 are based on merely complex calculations, hardcoding expected
  // numbers will not be useful here

  // datetime-related stuff
  ASSERT_FLOAT_EQ(features[22], 4.);    // friday
  ASSERT_FLOAT_EQ(features[23], 5.);    // 11pm in (-3) meaning 5am in (+3)
  ASSERT_FLOAT_EQ(features[24], 101.);  // 24 * 4 + 5
  ASSERT_FLOAT_EQ(features[25], 1.);
  ASSERT_FLOAT_EQ(features[26], 0.);
  ASSERT_FLOAT_EQ(features[27], 0.);
  ASSERT_FLOAT_EQ(features[28], 0.);
  ASSERT_FLOAT_EQ(features[29], 0.);
  ASSERT_FLOAT_EQ(features[30], 3.);

  // 31+ are omitted here for the same reason as 2-21
}
