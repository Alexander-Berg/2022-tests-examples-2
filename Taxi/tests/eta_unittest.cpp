#include <gtest/gtest.h>
#include <fstream>

#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>
#include "models/eta/eta_zone.hpp"
#include "models/eta/v1/eta_model.hpp"
#include "models/eta/v2/eta_model.hpp"
#include "models/eta/v3/eta_model.hpp"

namespace {

const std::string kTestDataDir = std::string(SOURCE_DIR) + "/tests/static/";

class ETAModelMock : public ml::eta::v1::ETAModel {
 public:
  std::vector<float> ExtractFeaturesMock(
      float eta_formula, const cctz::civil_second& date,
      const utils::GeoPoint& point, float free, float free_chain, float total,
      float surge_value, float radius, const ml::ZoneData* zone) const {
    return ExtractFeatures(eta_formula, date, point, free, free_chain, total,
                           surge_value, radius, zone);
  }
};

class ETAModelMockV2 : public ml::eta::v2::ETAModel {
 public:
  std::vector<float> ExtractFeaturesMock(
      float eta_formula, const cctz::civil_second& date,
      const utils::GeoPoint& point, const ml::SurgeClass& surgeclass,
      const ml::ZoneData& zone,
      const boost::optional<std::vector<ml::CandidateDriver>>& candidates)
      const {
    return ExtractFeatures(eta_formula, date, point, surgeclass, zone,
                           candidates);
  }
};

class ETAModelMockV3 : public ml::eta::v3::ETAModel {
 public:
  std::vector<float> ExtractFloatFeaturesMock(
      float eta_formula, const cctz::civil_second& date,
      const utils::GeoPoint& point, const ml::SurgeClass& surgeclass,
      const ml::ZoneData& zone,
      const boost::optional<std::vector<ml::CandidateDriver>>& candidates)
      const {
    return ExtractFloatFeatures(eta_formula, date, point, surgeclass, zone,
                                candidates);
  }
};

std::shared_ptr<ml::ZonesData> ReadParams(const std::string& filename) {
  std::ifstream in(kTestDataDir + filename);
  std::string content((std::istreambuf_iterator<char>(in)),
                      std::istreambuf_iterator<char>());

  return ml::ZonesDataParser()(content);
}

std::vector<float> ReadFeatures(const std::string& filename) {
  std::ifstream in(kTestDataDir + filename);
  Json::Value doc = utils::helpers::ParseJson(in);

  std::vector<float> features;
  for (auto it = doc.begin(); it != doc.end(); ++it) {
    features.push_back((*it).asFloat());
  }
  return features;
}

boost::optional<std::vector<ml::CandidateDriver>> ReadCandidatesV2(
    const std::string& filename, const utils::GeoPoint point) {
  std::ifstream in(kTestDataDir + filename);
  Json::Value doc = utils::helpers::ParseJson(in);

  const auto& candidates_arr = utils::helpers::FetchArray(doc, "candidates");
  boost::optional<std::vector<ml::CandidateDriver>> candidates =
      ml::ExtractClassCandidates(candidates_arr, point);
  return candidates;
}

boost::optional<std::vector<ml::CandidateDriver>> ReadCandidatesV3(
    const std::string& filename, const utils::GeoPoint point) {
  std::ifstream in(kTestDataDir + filename);
  Json::Value doc = utils::helpers::ParseJson(in);

  const auto& candidates_arr = utils::helpers::FetchArray(doc, "candidates");
  boost::optional<std::vector<ml::CandidateDriver>> candidates =
      ml::ExtractClassCandidates(candidates_arr, point);
  return candidates;
}

TEST(Eta, ExtractFeatures) {
  const ETAModelMock model;

  const auto zones = ReadParams("eta_nz.json");
  const auto gold_features = ReadFeatures("eta_features.json");
  auto point = utils::GeoPoint(37.642684, 55.734850);

  auto zone = zones->find("moscow")->second;

  // check old extractor
  auto features = model.ExtractFeaturesMock(
      240.0, cctz::civil_second(2018, 10, 20, 22, 33, 20), point, 10, 15, 50,
      1.3, 2500, &zone);
  for (unsigned int i = 0; i < features.size(); ++i) {
    ASSERT_FLOAT_EQ(features[i], gold_features[i]);
  }

  // check correct fillna in distance to center
  features = model.ExtractFeaturesMock(
      240.0, cctz::civil_second(2018, 10, 20, 22, 33, 20), point, 10, 15, 50,
      1.3, 2500, nullptr);
  ASSERT_FLOAT_EQ(features[18], -1);
}

TEST(Eta, ExtractFeaturesV2) {
  const ETAModelMockV2 model_v2;

  const auto zones = ReadParams("eta_nz.json");
  const auto gold_features = ReadFeatures("eta_features.json");
  auto point = utils::GeoPoint(37.642684, 55.734850);

  auto zone = zones->find("moscow")->second;
  auto candidates = ReadCandidatesV2("eta_candidates.json", point);
  boost::optional<std::vector<ml::CandidateDriver>> empty_candidates;

  ml::SurgeClass surgeclass;
  surgeclass.value = 1.3;
  surgeclass.free = 10;
  surgeclass.free_chain = 15;
  surgeclass.total = 50;
  surgeclass.radius = 2500;

  // check extractor with candidates
  auto features = model_v2.ExtractFeaturesMock(
      240.0, cctz::civil_second(2018, 10, 20, 22, 33, 20), point, surgeclass,
      zone, candidates);
  for (unsigned int i = 0; i < features.size(); ++i) {
    ASSERT_FLOAT_EQ(features[i], gold_features[i]);
  }

  // check extractor without candidates
  features = model_v2.ExtractFeaturesMock(
      240.0, cctz::civil_second(2018, 10, 20, 22, 33, 20), point, surgeclass,
      zone, empty_candidates);
  for (unsigned int i = 0; i < features.size(); ++i) {
    ASSERT_FLOAT_EQ(features[i], gold_features[i]);
  }

  // check geopoint of default zone
  zone = zones->find("default")->second;
  features = model_v2.ExtractFeaturesMock(
      240.0, cctz::civil_second(2018, 10, 20, 22, 33, 20), point, surgeclass,
      zone, empty_candidates);
  ASSERT_FLOAT_EQ(features[18], 2000);
}

TEST(Eta, ExtractFeaturesV3) {
  const ETAModelMockV3 model_v3;

  const auto zones = ReadParams("eta_nz.json");
  const auto gold_features = ReadFeatures("eta_features.json");
  auto point = utils::GeoPoint(37.642684, 55.734850);

  auto zone = zones->find("moscow")->second;
  auto candidates = ReadCandidatesV3("eta_candidates.json", point);
  boost::optional<std::vector<ml::CandidateDriver>> empty_candidates;

  ml::SurgeClass surgeclass;
  surgeclass.value = 1.3;
  surgeclass.free = 10;
  surgeclass.free_chain = 15;
  surgeclass.total = 50;
  surgeclass.radius = 2500;

  // check extractor with candidates
  auto features = model_v3.ExtractFloatFeaturesMock(
      240.0, cctz::civil_second(2018, 10, 20, 22, 33, 20), point, surgeclass,
      zone, candidates);
  for (unsigned int i = 0; i < features.size(); ++i) {
    ASSERT_FLOAT_EQ(features[i], gold_features[i]);
  }

  // check extractor without candidates
  features = model_v3.ExtractFloatFeaturesMock(
      240.0, cctz::civil_second(2018, 10, 20, 22, 33, 20), point, surgeclass,
      zone, empty_candidates);
  for (unsigned int i = 0; i < features.size(); ++i) {
    ASSERT_FLOAT_EQ(features[i], gold_features[i]);
  }

  // check geopoint of default zone
  zone = zones->find("default")->second;
  features = model_v3.ExtractFloatFeaturesMock(
      240.0, cctz::civil_second(2018, 10, 20, 22, 33, 20), point, surgeclass,
      zone, empty_candidates);
  ASSERT_FLOAT_EQ(features[18], 2000);
}

}  // namespace
