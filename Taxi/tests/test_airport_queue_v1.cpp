#include <gtest/gtest.h>

#include <ml/airport_queue/v1/configs.hpp>
#include <ml/airport_queue/v1/objects.hpp>
#include <ml/airport_queue/v1/resource.hpp>
#include <ml/common/filesystem.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::airport_queue::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("airport_queue_v1");
}  // namespace

TEST(AirportQueueV1, Serialization) {
  // Predictor config
  const auto predictor_config = ml::common::FromJsonString<PredictorConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/config.json"));
  ASSERT_EQ(predictor_config.pre_processor_config.time_intervals.size(), 3ul);
  // Predictor config with linear corrections
  const auto predictor_config_with_linear_corrections =
      ml::common::FromJsonString<PredictorConfig>(ml::common::ReadFileContents(
          kTestDataDir + "/config_with_linear_corrections.json"));
  ASSERT_TRUE(predictor_config_with_linear_corrections.post_processor_config
                  .has_value());
  ASSERT_EQ(predictor_config_with_linear_corrections.post_processor_config
                ->linear_corrections.count("vko"),
            1ul);
  ASSERT_EQ(predictor_config_with_linear_corrections.post_processor_config
                ->linear_corrections.at("vko")
                .count("econom"),
            1ul);
  ASSERT_EQ(predictor_config_with_linear_corrections.post_processor_config
                ->linear_corrections.at("vko")
                .at("econom")
                .size(),
            2ul);
  // Request
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  ASSERT_EQ(request.items.size(), 2ul);
  ASSERT_EQ(request.items.at(0).airport_zone, "vko");
  ASSERT_EQ(request.items.at(0).tariff_class, "econom");
  ASSERT_EQ(request.last_order_time_point,
            ml::common::datetime::Stringtime("2021-03-10T18:13:00", "UTC",
                                             "%Y-%m-%dT%H:%M:%S"));
  ASSERT_EQ(request.first_order_time_point,
            ml::common::datetime::Stringtime("2021-03-10T17:20:00", "UTC",
                                             "%Y-%m-%dT%H:%M:%S"));
  ASSERT_EQ(request.last_requested_time_point,
            ml::common::datetime::Stringtime("2021-03-10T18:20:00", "UTC",
                                             "%Y-%m-%dT%H:%M:%S"));
  // Inner Request
  const auto inner_request = ml::common::FromJsonString<InnerRequest>(
      ml::common::ReadFileContents(kTestDataDir + "/inner_request.json"));
  // Response
  Response response;
  for (size_t index = 0; index < inner_request.items.size(); ++index) {
    const auto& [item, interval] = inner_request.items.at(index);
    response.items.push_back(ResponseItem{item.airport_zone, item.tariff_class,
                                          interval, index * 30.0});
  }
  ASSERT_NO_THROW(ml::common::ToJsonString<Response>(response));

  response = ml::common::FromJsonString<Response>(
      ml::common::ReadFileContents(kTestDataDir + "/response.json"));
}

TEST(AirportQueueV1, Predictor) {
  const auto predictor_config = ml::common::FromJsonString<PredictorConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/config.json"));

  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));

  Resource resource(kTestDataDir, true);
  const auto predictor = resource.GetPredictor();
  auto response = predictor->Apply(request);

  ASSERT_EQ(predictor_config.features_config.add_atlas_features, true);
  ASSERT_EQ(response.items.size(), 6ul);

  response = predictor->Apply(request, Params());  // Explicit Params
}
