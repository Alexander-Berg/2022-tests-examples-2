#include <gtest/gtest.h>

#include <clients/codegen/command_control.hpp>
#include <clients/solomon-sensors/client_gmock.hpp>
#include <clients/solomon/solomon_client.hpp>
#include <clients/solomon/solomon_highlevel_client.hpp>

#include "tools/testutils.hpp"

namespace hejmdal {

const auto MockTime = testutils::MockTime;

namespace sensors_data =
    ::clients::solomon_sensors::api_v2_projects_project_name_sensors_data::post;

const std::vector<sensors_data::Request> requests{
    {"project1",
     {"{key1='key1_value'}",
      MockTime(1),
      MockTime(2),
      {},
      {sensors_data::kBodyVersionValues[1]}}},
    {"project2",
     {"{key2='key2_value'}",
      MockTime(3),
      MockTime(4),
      {},
      {sensors_data::kBodyVersionValues[1]}}},
    {"project3",
     {"{key3='key3_value'}",
      MockTime(5),
      MockTime(6),
      {},
      {sensors_data::kBodyVersionValues[1]}}},
    {"project4",
     {"{key4='key4_value'}",
      MockTime(7),
      MockTime(8),
      {},
      {sensors_data::kBodyVersionValues[1]}}},
    {"project5",
     {"{key5='key5_value'}",
      MockTime(9),
      MockTime(10),
      {},
      {sensors_data::kBodyVersionValues[1]}}},
    {"project6",
     {"{key6='key6_value'}",
      MockTime(11),
      MockTime(12),
      {},
      {sensors_data::kBodyVersionValues[1]}}},
    {"project7",
     {"{key7='key7_value'}",
      MockTime(13),
      MockTime(14),
      {},
      {sensors_data::kBodyVersionValues[1]}}},
    {"project8",
     {"{key8='key8_value'}",
      MockTime(15),
      MockTime(16),
      {},
      {sensors_data::kBodyVersionValues[1]}}}};

const std::string response1_str = R"=(
{
  "vector": [
    {
      "timeseries": {
        "alias": "alias1",
        "kind": "RATE",
        "labels": {
          "common_key1": "common_key1_value1"
        },
        "timestamps": [
          1574121600000,
          1574121660000,
          1574121720000,
          1574121780000,
          1574121840000,
          1574121900000
        ],
        "values": [
          17.0,
          23.0,
          25.0,
          23.0,
          20.0,
          16.0
        ]
      }
    }
  ]
}
)=";

const std::string response2_str = R"=(
{
  "vector": [
    {
      "timeseries": {
        "alias": "alias2",
        "kind": "RATE",
        "labels": {
          "common_key2": "common_key2_value2"
        },
        "timestamps": [
          1574121600000,
          1574121660000,
          1574121700000,
          1574121720000,
          1574121780000,
          1574121840000,
          1574121900000
        ],
        "values": [
          17.0,
          23.0,
          "NaN",
          25.0,
          23.0,
          20.0,
          16.0
        ]
      }
    }
  ]
}
)=";

const std::string response3_str = R"=(
{
  "vector": [
    {
      "timeseries": {
        "alias": "alias3",
        "kind": "RATE",
        "labels": {
          "common_key3": "common_key1_value3"
        },
        "timestamps": [
          1574121600000,
          1574121660000,
          1574121680000,
          1574121700000,
          1574121720000,
          1574121780000,
          1574121840000,
          1574121900000
        ],
        "values": [
          17.0,
          23.0,
          "NaN",
          "NaN",
          25.0,
          23.0,
          20.0,
          16.0
        ]
      }
    }
  ]
}
)=";

const std::string response4_str = R"=(
{
  "vector": [
    {
      "timeseries": {
        "alias": "alias4",
        "kind": "RATE",
        "labels": {
          "common_key4": "common_key4_value4"
        },
        "timestamps": [
          1574121500000,
          1574121600000,
          1574121660000,
          1574121700000,
          1574121720000,
          1574121780000,
          1574121840000,
          1574121900000,
          1574122000000,
          1574122100000
        ],
        "values": [
          "NaN",
          17.0,
          23.0,
          "NaN",
          25.0,
          23.0,
          20.0,
          16.0,
          "NaN",
          "NaN"
        ]
      }
    }
  ]
}
)=";

const std::string response5_str = R"=(
{
  "vector": [
    {
      "timeseries": {
        "alias": "alias5",
        "kind": "RATE",
        "labels": {
          "common_key5": "common_key1_value5"
        },
        "timestamps": [
          1574121500000,
          1574121600000,
          1574121660000,
          1574121700000,
          1574121720000,
          1574121780000,
          1574121840000,
          1574121900000,
          1574122000000,
          1574122100000
        ],
        "values": [
          "Infinity",
          17.0,
          23.0,
          "NaN",
          25.0,
          23.0,
          20.0,
          16.0,
          "Infinity",
          "NaN"
        ]
      }
    }
  ]
}
)=";

const std::string response_empty_str = R"=(
{
  "vector": [
    {
      "timeseries": {
        "alias": "alias6",
        "kind": "RATE",
        "labels": {
          "common_key6": "common_key6_value6"
        },
        "timestamps": [
          1574121500000,
          1574121600000,
          1574121660000
        ],
        "values": [
          "NaN",
          "NaN",
          "NaN"
        ]
      }
    }
  ]
}
)=";

const std::string response_invalid_str = R"=(
{
  "vector": [
    {
      "timeseries": {
        "alias": "alias7",
        "kind": "RATE",
        "labels": {
          "common_key7": "common_key7_value7"
        },
        "timestamps": [
          1574121500000,
          1574121600000,
          1574121660000
        ],
        "values": [
          "NaN",
          1.0,
          "invalid_value"
        ]
      }
    }
  ]
}
)=";

const std::string response_no_vector_str = R"=(
{
  "timeseries":
    {
      "alias": "alias1",
      "kind": "RATE",
      "labels": {
        "common_key1": "common_key1_value1"
      },
      "timestamps": [
        1574121600000,
        1574121660000,
        1574121720000,
        1574121780000,
        1574121840000,
        1574121900000
      ],
      "values": [
        17.0,
        23.0,
        25.0,
        23.0,
        20.0,
        16.0
      ]
    }
}
)=";

class MockSolomonGenClient final
    : public ::clients::solomon_sensors::ClientMockBase {
 public:
  sensors_data::Response ApiV2ProjectsProjectNameSensorsData(
      const sensors_data::Request& request,
      const ::clients::codegen::CommandControl& /*command_control*/ = {})
      const override {
    size_t ind = 0;
    while (ind < requests.size()) {
      if (requests[ind].project_name == request.project_name &&
          requests[ind].body.program == request.body.program &&
          requests[ind].body.from == request.body.from &&
          requests[ind].body.to == request.body.to &&
          requests[ind].body.version == request.body.version) {
        break;
      }
      ++ind;
    }
    if (ind == requests.size()) {
      throw std::logic_error(
          "invalid arguments to MockSolomonGenClient::"
          "ApiV2ProjectsProjectNameSensorsData()");
    }

    static std::vector<std::string> response_vector{
        response1_str,        response2_str,         response3_str,
        response4_str,        response5_str,         response_empty_str,
        response_invalid_str, response_no_vector_str};

    auto result_str = response_vector[ind];
    return sensors_data::Parse(formats::json::FromString(result_str),
                               formats::parse::To<sensors_data::Response>{});
  };
};

const auto from_times = std::vector<std::chrono::system_clock::time_point>{
    MockTime(1), MockTime(3),  MockTime(5),  MockTime(7),
    MockTime(9), MockTime(11), MockTime(13), MockTime(15)};
const auto to_times = std::vector<std::chrono::system_clock::time_point>{
    MockTime(2),  MockTime(4),  MockTime(6),  MockTime(8),
    MockTime(10), MockTime(12), MockTime(14), MockTime(16)};
auto programs = std::vector<std::string>{
    "{key1='key1_value'}", "{key2='key2_value'}", "{key3='key3_value'}",
    "{key4='key4_value'}", "{key5='key5_value'}", "{key6='key6_value'}",
    "{key7='key7_value'}", "{key8='key8_value'}"};

TEST(SolomonClient, RequestAndResponseTransfer) {
  auto gen_mock_client = MockSolomonGenClient();
  auto client = clients::CreateSolomonClient(gen_mock_client);

  clients::BatchResponseInfo response;

  EXPECT_NO_THROW(
      response = client->GetSensorsData("project1", from_times[0], to_times[0],
                                        std::move(programs[0]), false));
  auto json = formats::json::FromString(response1_str);
  auto expected = json["vector"].As<clients::BatchResponse>();
  EXPECT_EQ(response.batch_response, expected);

  response = client->GetSensorsData("project2", from_times[1], to_times[1],
                                    std::move(programs[1]), false);
  json = formats::json::FromString(response2_str);
  expected = json["vector"].As<clients::BatchResponse>();
  EXPECT_EQ(response.batch_response, expected);

  EXPECT_NO_THROW(
      response = client->GetSensorsData("project3", from_times[2], to_times[2],
                                        std::move(programs[2]), false));
  json = formats::json::FromString(response3_str);
  expected = json["vector"].As<clients::BatchResponse>();
  EXPECT_EQ(response.batch_response, expected);

  EXPECT_NO_THROW(
      response = client->GetSensorsData("project4", from_times[3], to_times[3],
                                        std::move(programs[3]), false));
  json = formats::json::FromString(response4_str);
  expected = json["vector"].As<clients::BatchResponse>();
  EXPECT_EQ(response.batch_response, expected);

  EXPECT_NO_THROW(
      response = client->GetSensorsData("project5", from_times[4], to_times[4],
                                        std::move(programs[4]), false));
  json = formats::json::FromString(response5_str);
  expected = json["vector"].As<clients::BatchResponse>();
  EXPECT_EQ(response.batch_response, expected);
}

TEST(SolomonClient, EmptyTimeseries) {
  auto gen_mock_client = MockSolomonGenClient();
  auto client = clients::CreateSolomonClient(gen_mock_client);

  clients::BatchResponseInfo response;

  EXPECT_NO_THROW(
      response = client->GetSensorsData("project6", from_times[5], to_times[5],
                                        std::move(programs[5]), false));
  auto json = formats::json::FromString(response_empty_str);
  auto expected = json["vector"].As<clients::BatchResponse>();
  EXPECT_EQ(response.batch_response, expected);
}

TEST(SolomonClient, InvalidStringInValues) {
  auto gen_mock_client = MockSolomonGenClient();
  auto client = clients::CreateSolomonClient(gen_mock_client);

  clients::BatchResponseInfo response;

  EXPECT_THROW(
      response = client->GetSensorsData("project7", from_times[6], to_times[6],
                                        std::move(programs[6]), false),
      std::exception);
}

TEST(SolomonClient, ResponseWithoutVector) {
  auto gen_mock_client = MockSolomonGenClient();
  auto client = clients::CreateSolomonClient(gen_mock_client);

  clients::BatchResponseInfo response;

  EXPECT_NO_THROW(
      response = client->GetSensorsData("project8", from_times[7], to_times[7],
                                        std::move(programs[7]), false));
  auto json = formats::json::FromString(response_no_vector_str);
  auto expected = json.As<clients::models::SolomonTimeSeriesResponse>();
  EXPECT_EQ(response.batch_response[0], expected);
}
}  // namespace hejmdal
