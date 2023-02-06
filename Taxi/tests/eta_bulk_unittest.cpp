#include <gtest/gtest.h>
#include <fstream>

#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>
#include "models/eta/eta_surge.hpp"
#include "models/eta/eta_zone.hpp"
#include "models/eta_bulk/v1/model.hpp"
#include "models/eta_bulk/v2/model.hpp"
#include "models/eta_bulk/v3/model.hpp"

namespace {

const std::string kTestDataDir = std::string(SOURCE_DIR) + "/tests/static/";

class EtaBulkModelMockV1 : public ml::eta_bulk::v1::EtaBulkModel {
 public:
  std::vector<float> ExtractFeaturesMock(float eta_formula,
                                         const cctz::civil_second& date,
                                         const utils::GeoPoint& point,
                                         const ml::SurgeClass& surge_class,
                                         const ml::ZoneData& zone) const {
    return ExtractFeatures(eta_formula, date, point, surge_class, zone);
  }
};

class ETAModelMockV2 : public ml::eta_bulk::v2::EtaBulkModel {
 public:
  std::vector<float> ExtractFeaturesMock(
      float eta_formula, const cctz::civil_second& date,
      const utils::GeoPoint& point, const ml::SurgeClass& surgeclass,
      const ml::ZoneData& zone,
      const std::vector<ml::eta_bulk::CandidateDriver> candidates) const {
    return ExtractFeatures(eta_formula, date, point, surgeclass, zone,
                           candidates);
  }
};

class ETAModelMockV3 : public ml::eta_bulk::v3::EtaBulkModel {
 public:
  std::vector<float> ExtractFloatFeaturesMock(
      float eta_formula, const cctz::civil_second& date,
      const utils::GeoPoint& point, const ml::SurgeClass& surgeclass,
      const ml::ZoneData& zone,
      const std::vector<ml::eta_bulk::CandidateDriver> candidates) const {
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
  for (auto it : doc) {
    features.push_back(it.asFloat());
  }
  return features;
}

std::vector<ml::eta_bulk::CandidateDriver> ReadCandidates(
    const std::string& filename, const utils::GeoPoint point) {
  using ml::eta_bulk::CandidateDriver;
  using utils::helpers::FetchArray;
  using utils::helpers::FetchMember;
  using utils::helpers::FetchMemberDef;
  using utils::helpers::FetchMemberOptional;

  std::ifstream in(kTestDataDir + filename);
  Json::Value doc = utils::helpers::ParseJson(in);

  const auto& candidates_arr = FetchArray(doc, "candidates");

  std::vector<CandidateDriver> candidates;
  candidates.reserve(candidates_arr.size());

  for (const auto& candidate_doc : candidates_arr) {
    CandidateDriver candidate;
    FetchMember(candidate.grade, candidate_doc, "grade");
    FetchMember(candidate.in_pool, candidate_doc, "in_pool");
    FetchMemberDef(candidate.online_seconds, -1, candidate_doc,
                   "online_seconds");
    FetchMember(candidate.position, candidate_doc, "position");
    FetchMemberOptional(candidate.destination, candidate_doc, "destination");
    FetchMember(candidate.route_dist, candidate_doc, "route_dist");
    FetchMember(candidate.route_time, candidate_doc, "route_time");
    FetchMember(candidate.free, candidate_doc, "free");
    FetchMember(candidate.clid_uuid, candidate_doc, "uuid");

    if (candidate.free || !candidate.destination) {
      candidate.line_dist =
          utils::geometry::CalcDistance(candidate.position, point);
    } else {
      candidate.line_dist =
          utils::geometry::CalcDistance(candidate.position,
                                        candidate.destination.get()) +
          utils::geometry::CalcDistance(candidate.destination.get(), point);
    }
    candidates.push_back(std::move(candidate));
  }

  return candidates;
}

TEST(EtaBulk, ExtractFeaturesV1) {
  const EtaBulkModelMockV1 model;

  const auto zones = ReadParams("eta_nz.json");
  const auto gold_features = ReadFeatures("eta_features.json");

  float eta_formula = 240;
  auto point = utils::GeoPoint(37.642684, 55.734850);
  auto datetime = cctz::civil_second(2018, 10, 20, 22, 33, 20);
  unsigned int kNumFeatures = 25;

  ml::SurgeClass surgeclass;
  surgeclass.value = 1.3;
  surgeclass.free = 10;
  surgeclass.free_chain = 15;
  surgeclass.total = 50;
  surgeclass.radius = 2500;

  // check extractor
  auto features = model.ExtractFeaturesMock(
      eta_formula, datetime, point, surgeclass, zones->find("moscow")->second);
  ASSERT_EQ(features.size(), kNumFeatures);
  for (unsigned int i = 0; i < kNumFeatures; ++i) {
    ASSERT_FLOAT_EQ(features[i], gold_features[i]);
  }

  // check geopoint of default zone
  features = model.ExtractFeaturesMock(eta_formula, datetime, point, surgeclass,
                                       zones->find("default")->second);
  ASSERT_FLOAT_EQ(features[18], 2000);
}

TEST(EtaBulk, ExtractFeaturesV2) {
  const ETAModelMockV2 model_v2;

  const auto zones = ReadParams("eta_nz.json");
  const auto gold_features = ReadFeatures("eta_features.json");
  auto point = utils::GeoPoint(37.642684, 55.734850);

  auto zone = zones->find("moscow")->second;
  auto candidates = ReadCandidates("eta_candidates.json", point);
  std::vector<ml::eta_bulk::CandidateDriver> empty_candidates;

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

TEST(EtaBulk, ExtractFeaturesV3) {
  const ETAModelMockV3 model_v3;

  const auto zones = ReadParams("eta_nz.json");
  const auto gold_features = ReadFeatures("eta_features.json");
  auto point = utils::GeoPoint(37.642684, 55.734850);

  auto zone = zones->find("moscow")->second;
  auto candidates = ReadCandidates("eta_candidates.json", point);
  std::vector<ml::eta_bulk::CandidateDriver> empty_candidates;

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
