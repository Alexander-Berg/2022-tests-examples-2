#include <gtest/gtest.h>
#include <fstream>

#include "clients/airport_timetable.hpp"
#include "common/datetime.hpp"
#include "models/airport_queue/v1/airport_queue_model.hpp"
#include "models/airport_queue/v2/airport_queue_model.hpp"

namespace {

const std::string kTestDataDir = std::string(SOURCE_DIR) + "/tests/static/";

class AirportQueueModelV1Mock
    : public ml::airport_queue::v1::AirportQueueModel {
 public:
  std::vector<std::vector<float>> ExtractFeatures(
      const std::string& datetime, const std::string& min_minute_datetime,
      const std::vector<unsigned>& orders,
      const std::vector<unsigned>& success_orders,
      const ml::airport_queue::v1::FeaturesExtractorParams& params) const {
    return AirportQueueModel::ExtractFeatures(datetime, min_minute_datetime,
                                              orders, success_orders, params);
  }
};

class AirportQueueModelV2Mock
    : public ml::airport_queue::v2::AirportQueueModel {
 public:
  std::vector<std::vector<float>> ExtractFeatures(
      const std::string& datetime, const std::string& min_minute_datetime,
      const std::vector<unsigned>& orders,
      const std::vector<unsigned>& success_orders,
      const ml::airport_queue::v2::FeaturesExtractorParams& params) const {
    return AirportQueueModel::ExtractFeatures(datetime, min_minute_datetime,
                                              orders, success_orders, params);
  }
};

std::shared_ptr<ml::airport_queue::v1::FeaturesExtractorParams> ReadParamsV1() {
  std::ifstream in(kTestDataDir + "airport_queue_extractor_params.json");
  std::string content((std::istreambuf_iterator<char>(in)),
                      std::istreambuf_iterator<char>());

  return ml::airport_queue::v1::FeaturesExtractorParamsParser()(content);
}

std::shared_ptr<ml::airport_queue::v2::FeaturesExtractorParams> ReadParamsV2() {
  std::ifstream in(kTestDataDir + "airport_queue_extractor_params_v2.json");
  std::string content((std::istreambuf_iterator<char>(in)),
                      std::istreambuf_iterator<char>());

  return ml::airport_queue::v2::FeaturesExtractorParamsParser()(content);
}

void ReadOrders(std::vector<unsigned>& orders,
                std::vector<unsigned>& success_orders) {
  std::ifstream in(kTestDataDir + "airport_queue_extractor.txt");
  size_t records_count;
  in >> records_count;

  for (size_t i = 0; i < records_count; ++i) {
    unsigned order;
    unsigned success_order;

    in >> order;
    in >> success_order;

    orders.push_back(order);
    success_orders.push_back(success_order);
  }
}

std::vector<float> ReadExpectedFeatures(const std::string& filename) {
  std::ifstream in(kTestDataDir + filename);
  std::vector<float> result;

  while (in) {
    float feature;
    in >> feature;
    result.push_back(feature);
  }

  result.pop_back();
  return result;
}

std::vector<FlightInfo> ReadTimetableData(const std::string& filename) {
  std::ifstream request_file(std::string(SOURCE_DIR) + "/tests/static/" +
                             filename + ".json");
  std::string format = "%Y-%m-%dT%H:%M:%S";
  auto doc = utils::helpers::ParseJson(request_file);
  std::vector<FlightInfo> flight_info;
  for (const auto& flight_doc : doc) {
    FlightInfo flight;
    flight.number = flight_doc["number"].asString();
    flight.iata_code_from = flight_doc["airport_from_code"].asString();
    flight.iata_code_to = flight_doc["airport_to_code"].asString();
    flight.status = flight_doc["status"].asString();
    flight.arrival_utc =
        ml::common::ParseDatetime(flight_doc["arrival_utc"].asString(), format);
    flight.departure_utc = ml::common::ParseDatetime(
        flight_doc["departure_utc"].asString(), format);
    flight.arrival_utc_status = ml::common::ParseDatetime(
        flight_doc["arrival_utc_status"].asString(), format);
    flight_info.push_back(flight);
  }
  return flight_info;
}

}  // namespace

TEST(AirportQueueV1, ParseDatetime) {
  std::string datetime("2005-08-09T18:31:42+0300");
  ASSERT_EQ(18, ml::common::ParseDatetime(datetime).hour());
}

TEST(AirportQueueV1, FeaturesExtractor) {
  std::vector<unsigned> orders;
  std::vector<unsigned> success_orders;

  auto params = ReadParamsV1();
  ReadOrders(orders, success_orders);
  AirportQueueModelV1Mock model;

  const auto& features_vec = model.ExtractFeatures(
      "2017-12-01T2:21:00+0300", "2017-10-01T04:01:00+0300", orders,
      success_orders, *params);

  std::vector<float> expected =
      ReadExpectedFeatures("airport_queue_features_expected.txt");
  auto expected_it = expected.begin();

  for (size_t vec_id = 0; vec_id < features_vec.size(); ++vec_id) {
    const auto& features = features_vec[vec_id];
    for (size_t feature_id = 0; feature_id < features.size(); ++feature_id) {
      ASSERT_FLOAT_EQ(*expected_it, features[feature_id])
          << "Wrong feature #" << feature_id << " in " << vec_id;
      expected_it++;
    }
  }
}

TEST(AirportQueueV2, FeaturesExtractor) {
  std::vector<unsigned> orders;
  std::vector<unsigned> success_orders;

  auto params = ReadParamsV2();
  ReadOrders(orders, success_orders);
  AirportQueueModelV2Mock model;

  // base part with empty flight data
  const auto& features_vec = model.ExtractFeatures(
      "2017-12-01T2:21:00+0300", "2017-10-01T04:01:00+0300", orders,
      success_orders, *params);
  auto expected =
      ReadExpectedFeatures("airport_queue_features_expected_v2.txt");
  auto expected_it = expected.begin();
  for (size_t vec_id = 0; vec_id < features_vec.size(); ++vec_id) {
    const auto& features = features_vec[vec_id];
    for (size_t feature_id = 0; feature_id < features.size(); ++feature_id) {
      ASSERT_FLOAT_EQ(*expected_it, features[feature_id])
          << "Wrong feature #" << feature_id << " in " << vec_id;
      expected_it++;
    }
  }

  // flight data extractor
  auto flight_info = ReadTimetableData("airport_queue_timetable_v2");
  auto timetable_expected =
      ReadExpectedFeatures("airport_queue_timetable_features_expected_v2.txt");

  auto datetime = "2019-05-01T20:21:00+0300";
  auto last_update = ml::common::ParseDatetime(datetime) - 10;
  auto config = config::AirportQueueMlConfig();
  config.timetable_data_life_time = 1000;
  params->tz_offset = 10800;

  auto timetable_features = ExtractTimetableFeatures(
      flight_info, *params, datetime, last_update, config);

  ASSERT_EQ(timetable_expected.size(), timetable_features.size());
  for (size_t i = 0; i < timetable_expected.size(); ++i) {
    ASSERT_FLOAT_EQ(timetable_expected[i], timetable_features[i]);
  }
}
