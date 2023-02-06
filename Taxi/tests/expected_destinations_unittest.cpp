#include <unicode/unistr.h>

#include <cctz/time_zone.h>
#include <gtest/gtest.h>
#include <boost/algorithm/string/trim.hpp>
#include <boost/locale.hpp>
#include <boost/locale/generator.hpp>
#include <common/datetime.hpp>
#include <fstream>
#include <models/expected_destinations/candidates.hpp>
#include <models/expected_destinations/expected_destinations_model.hpp>
#include <models/expected_destinations/features.hpp>

namespace {

const std::string kTestDataDir = std::string(SOURCE_DIR) + "/tests/static/";

struct PhoneHistorySample {
  std::vector<ml::expected_destinations::PhoneHistory> history;
  ml::expected_destinations::Address current_address;
  utils::TimePoint current_time;

  void Deserialize(const Json::Value& value) {
    DeserializeLastRoute(value["last_route"]);

    history.clear();
    for (const auto& route : value["routes_info"]) {
      DeserializeRoute(route);
    }
  }

  void DeserializeLastRoute(const Json::Value& value) {
    current_address.full_text = value[0].asString();
    current_address.point.lon = value[1].asDouble();
    current_address.point.lat = value[2].asDouble();

    current_time = ml::common::ParsePhoneHistoryDatetime(value[6].asString());
  }

  void DeserializeRoute(const Json::Value& value) {
    ml::expected_destinations::PhoneHistory rslt;
    rslt.source.full_text = value[0].asString();
    rslt.source.point.lon = value[1].asDouble();
    rslt.source.point.lat = value[2].asDouble();

    if (!value[3].isNull()) {
      ml::expected_destinations::Address addr;
      addr.full_text = value[3].asString();
      addr.point.lon = value[4].asDouble();
      addr.point.lat = value[5].asDouble();
      rslt.destination = std::move(addr);
    }
    rslt.created = ml::common::ParsePhoneHistoryDatetime(value[6].asString());
    history.push_back(rslt);
  }
};

struct CandidatesSample {
  std::vector<ml::expected_destinations::Candidate> candidates;

  void Deserialize(const Json::Value& value) {
    candidates.clear();
    for (const auto& candidate_doc : value["candidates"]) {
      ml::expected_destinations::Candidate candidate;

      candidate.address = candidate_doc[0].asString();
      candidate.point.lon = candidate_doc[1].asDouble();
      candidate.point.lat = candidate_doc[2].asDouble();
      candidate.score = candidate_doc[3].asDouble();
      candidate.rank = candidate_doc[5].asInt();

      candidates.push_back(std::move(candidate));
    }
  }
};

const std::string cities_data = R"json(
[
   {
      "br_lon" : 60.9533,
      "city" : "Екатеринбург",
      "tl_lon" : 60.0069,
      "tl_lat" : 56.9886,
      "br_lat" : 56.586256,
      "tz" : "Asia/Yekaterinburg"
   },
   {
      "tz" : "Asia/Omsk",
      "tl_lat" : 55.139569,
      "br_lat" : 54.799461,
      "br_lon" : 73.669032,
      "tl_lon" : 72.901363,
      "city" : "Омск"
   }
])json";

TEST(ExpectedDestinations, CandidatesExtractor) {
  ml::expected_destinations::AddressInfo address;
  ml::expected_destinations::GeopointsNet points_net(1000.0);

  address.AddGeopoint({55.678894, 37.26387}, 4.0);
  points_net.AddGeopoint({55.678894, 37.26387}, 2.0);
  address.AddGeopoint({55.678894, 37.26387}, 4.0);
  points_net.AddGeopoint({55.678894, 37.26387}, 2.0);
  address.AddGeopoint({55.678894, 37.26387}, 4.0);
  points_net.AddGeopoint({55.678894, 37.26387}, 2.0);

  address.AddGeopoint({55.678818, 37.26094}, 2.0);
  points_net.AddGeopoint({55.678818, 37.26094}, 1.0);

  address.AddGeopoint({55.678894, 37.26387}, 4.0);
  points_net.AddGeopoint({55.678894, 37.26387}, 2.0);
  address.AddGeopoint({55.678894, 37.26387}, 4.0);
  points_net.AddGeopoint({55.678894, 37.26387}, 2.0);

  std::priority_queue<ml::expected_destinations::Candidate> candidates;

  address.AddCandidatesTo("", candidates, 100, points_net);

  ASSERT_EQ(candidates.size(), 2u);

  std::vector<ml::expected_destinations::Candidate> top;
  top.push_back(candidates.top());
  candidates.pop();
  top.push_back(candidates.top());
  candidates.pop();

  ml::expected_destinations::Candidate candidate_1;
  candidate_1.point = {55.678894, 37.263869999999997};
  candidate_1.score = 32.0;

  ml::expected_destinations::Candidate candidate_2;
  candidate_2.point = {55.678818, 37.260939999999998};
  candidate_2.score = 23.0;

  ASSERT_EQ(candidate_1, top[0]);
  ASSERT_EQ(candidate_2, top[1]);
}

TEST(ExpectedDestinations, ExtractCandidates) {
  std::ifstream samples_file(kTestDataDir + "candidates_extract.json");
  Json::Value sample_doc = utils::helpers::ParseJson(samples_file);

  PhoneHistorySample sample;
  sample.Deserialize(sample_doc);

  ml::expected_destinations::CandidatesExtractorConfig config;
  config.history_size = 200;
  config.count_memory = std::chrono::seconds(5184000);
  config.coordinate_mult = 1000.0;
  config.last2week_mult = 3;
  config.source_address_hit_score = 2;
  config.source_point_hit_score = 1;
  config.destination_address_hit_score = 4;
  config.destination_point_hit_score = 2;
  config.exact_destination_address_hit_score = 50;
  config.exact_destination_point_hit_score = 50;
  config.max_merge_distance = 100;
  config.max_candidates = 20;

  auto candidates = ml::expected_destinations::ExtractCandidates(
      sample.history, sample.current_address, sample.current_time, config);

  std::vector<ml::expected_destinations::Candidate> expected_candidates;

  expected_candidates.push_back(
      {"Россия, Московская область, Одинцово", {55.678894, 37.26387}, 32.0});
  expected_candidates.push_back(
      {"Россия, Московская область, Одинцово", {55.678818, 37.26094}, 23.0});
  expected_candidates.push_back(
      {"Россия, Московская область, Одинцовский район, село Дубки, "
       "Комсомольская улица",
       {55.66382, 37.214657},
       9.0});
  expected_candidates.push_back(
      {"Россия, Россия, город Москва, Центральный парк культуры и отдыха им. "
       "А.М. Горького, ЦПКиО им. Горького",
       {55.727894, 37.600475},
       6.0});
  expected_candidates.push_back(
      {"Россия, Московская область, Одинцовский район, село Дубки, Новый "
       "переулок",
       {55.66247, 37.19522},
       6.0});
  expected_candidates.push_back({"Россия, Москва, Дружинниковская улица, 11А",
                                 {55.758007, 37.57553},
                                 6.0});
  expected_candidates.push_back(
      {"Россия, Московская область, Одинцовский район, село Дубки, Северная "
       "улица",
       {55.664875, 37.21414},
       3.0});
  expected_candidates.push_back(
      {"Россия, Московская область, Одинцовский район, посёлок ВНИИССОК, "
       "Можайское шоссе, 28 километр",
       {55.660828, 37.212093},
       3.0});
  expected_candidates.push_back(
      {"Россия, Московская область, Одинцово, Можайское шоссе, 12",
       {55.670746, 37.266773},
       3.0});
  expected_candidates.push_back(
      {"Россия, Москва, Конюшковская улица", {55.756325, 37.57771}, 3.0});

  ASSERT_EQ(expected_candidates.size(), candidates.size());

  for (size_t i = 0; i < expected_candidates.size(); ++i) {
    ASSERT_EQ(expected_candidates[i].address, candidates[i].address);
    ASSERT_FLOAT_EQ(expected_candidates[i].point.lon, candidates[i].point.lon);
    ASSERT_FLOAT_EQ(expected_candidates[i].point.lat, candidates[i].point.lat);
    ASSERT_EQ(expected_candidates[i].score, candidates[i].score);
  }
}

TEST(ExpectedDestinations, GetWeekDay) {
  cctz::time_zone tz;
  cctz::load_time_zone("Asia/Krasnoyarsk", &tz);
  // UTC - 6:57, Москва - 9:57, Красноярск - 13:57
  auto time = std::chrono::system_clock::from_time_t(1507705045);
  auto civil_time = cctz::convert(time, tz);

  cctz::civil_day day(civil_time);
  ASSERT_EQ(2, static_cast<int>(cctz::get_weekday(day)));
  ASSERT_EQ(13, civil_time.hour());
}

TEST(ExpectedDestinations, ToLower) {
  std::string str("АНАПА");
  std::locale loc = boost::locale::generator().generate("ru_RU.UTF-8");
  std::string r = boost::locale::to_lower(boost::trim_copy(str), loc);

  ASSERT_EQ("анапа", r);
}

TEST(ExpectedDestinations, DISABLED_ExtractFeatures) {
  Json::Value cities_doc = utils::helpers::ParseJson(cities_data);

  std::ifstream samples_file(kTestDataDir +
                             "expected_destinations_sample.json");
  Json::Value sample_doc = utils::helpers::ParseJson(samples_file);

  ml::expected_destinations::Cities cities;
  cities.ParseFrom(cities_doc);

  PhoneHistorySample sample;
  sample.Deserialize(sample_doc);
  CandidatesSample candidates_sample;
  candidates_sample.Deserialize(sample_doc);

  ml::expected_destinations::FeatureExtractor features_extractor(
      cities.GetCity(sample.current_address.point),
      candidates_sample.candidates, sample.history, sample.current_address,
      sample.current_time);

  size_t candidate_no = 0;

  for (const auto& candidate_features_doc : sample_doc["expected_features"]) {
    std::vector<float> expected_features;
    for (const auto& features_doc : candidate_features_doc) {
      expected_features.push_back(features_doc.asDouble());
    }

    std::vector<float> actual_features;
    ASSERT_TRUE(features_extractor.HasNextCandidate());
    features_extractor.GetNextCandidateFeatures(actual_features);

    for (size_t i = 0; i < actual_features.size(); ++i) {
      ASSERT_FLOAT_EQ(expected_features[i], actual_features[i])
          << "Wrong feature #" << std::to_string(i) << " in candidate "
          << candidate_no;
    }
    candidate_no += 1;
  }
}

}  // namespace
