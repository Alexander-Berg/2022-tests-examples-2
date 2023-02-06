#include <gtest/gtest.h>

#include <chrono>

#include <userver/engine/run_in_coro.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utils/datetime.hpp>

#include <clients/codegen/command_control.hpp>
#include <clients/solomon-sensors/client_gmock.hpp>
#include <clients/solomon/solomon_client.hpp>
#include <clients/solomon/solomon_highlevel_client.hpp>
#include <clients/solomon/utils/solomon_selector_builder.hpp>

#include "tools/testutils.hpp"

namespace hejmdal {

using BatchResponse = hejmdal::clients::BatchResponse;
using SolomonRequest = hejmdal::clients::models::SolomonRequest;
using SolomonResponse = hejmdal::clients::models::SolomonResponse;
using SensorValue = hejmdal::models::SensorValue;
using TimeSeries = hejmdal::models::TimeSeries;

const auto MockTime = testutils::MockTime;

time::TimeRange MockTimeRange(std::time_t begin, std::time_t end) {
  auto begin_time = MockTime(begin);
  auto end_time = MockTime(end);
  return time::TimeRange(begin_time, end_time);
}

TEST(SolomonHighlevelClient, SelectorBuilder) {
  clients::utils::SolomonSelectorBuilder common_builder;
  common_builder.AddKeyValue("common_key1", "common_key1_value1");
  common_builder.AddKeyValue("common_key1", "common_key1_value2");
  common_builder.AddKeyValue("common_key2", "common_key2_value1");
  common_builder.ExcludeLabelValue("key3", "to_exclude");
  common_builder.ExcludeLabel("label_to_exclude");
  EXPECT_EQ(
      "{common_key1='common_key1_value1|common_key1_value2',common_key2='"
      "common_key2_value1',label_to_exclude=-,key3!='to_exclude'}",
      common_builder.Get());

  {
    bool should_be_true =
        common_builder.Match({{"common_key1", "common_key1_value1"},
                              {"common_key2", "common_key2_value1"}});
    EXPECT_TRUE(should_be_true);
  }

  {
    bool should_be_true =
        common_builder.Match({{"common_key1", "common_key1_value2"},
                              {"common_key2", "common_key2_value1"}});
    EXPECT_TRUE(should_be_true);
  }

  {
    bool should_be_true =
        common_builder.Match({{"common_key1", "common_key1_value1"},
                              {"common_key2", "common_key2_value1"},
                              {"key3", "not_to_exclude"}});
    EXPECT_TRUE(should_be_true);
  }

  {
    bool should_be_false =
        common_builder.Match({{"common_key1", "common_key1_value1"}});
    EXPECT_FALSE(should_be_false);
  }

  {
    bool should_be_false =
        common_builder.Match({{"common_key1", "common_key1_value1"},
                              {"common_key2", "common_key2_value2"}});
    EXPECT_FALSE(should_be_false);
  }

  {
    bool should_be_false =
        common_builder.Match({{"common_key1", "common_key1_value1"},
                              {"common_key2", "common_key2_value1"},
                              {"key3", "to_exclude"}});
    EXPECT_FALSE(should_be_false);
  }

  {
    bool should_be_false =
        common_builder.Match({{"common_key1", "common_key1_value1"},
                              {"common_key2", "common_key2_value1"},
                              {"label_to_exclude", "some_value"}});
    EXPECT_FALSE(should_be_false);
  }
}

TEST(SolomonHighlevelClient, MakeRequestMapTest) {
  clients::utils::SolomonSelectorBuilder common_builder;
  common_builder.AddKeyValue("common_key1", "common_key1_value1");
  common_builder.AddKeyValue("common_key2", "common_key2_value1");
  auto req1_builder = common_builder;
  req1_builder.AddKeyValue("req1_key1", "req1_key1_value");
  auto req2_builder = common_builder;
  req2_builder.AddKeyValue("req2_key1", "req2_key1_value");
  auto req3_builder = common_builder;
  req3_builder.AddKeyValue("req3_key1", "req3_key1_value");

  clients::utils::SolomonSelectorBuilder common2_builder;
  common2_builder.AddKeyValue("common_key1", "common_key1_value1");
  common2_builder.AddKeyValue("common_key2", "common_key2_value2");

  auto req4_builder = common2_builder;
  req4_builder.AddKeyValue("req4_key", "req4_key_value");

  clients::utils::SolomonSelectorBuilder raw_builder_1;
  raw_builder_1.RawProgram("MyProgram_1()");

  clients::utils::SolomonSelectorBuilder raw_builder_2;
  raw_builder_2.RawProgram("MyProgram_2()");

  auto tr1 = MockTimeRange(1, 3);
  auto tr2 = MockTimeRange(2, 4);
  auto tr3 = MockTimeRange(3, 5);
  auto tr12 = MockTimeRange(1, 4);

  std::vector<std::shared_ptr<SolomonRequest>> requests{
      std::make_shared<SolomonRequest>(
          SolomonRequest{"project", req1_builder, tr1, common_builder, {}}),
      std::make_shared<SolomonRequest>(
          SolomonRequest{"project", req2_builder, tr2, common_builder, {}}),
      std::make_shared<SolomonRequest>(SolomonRequest{
          "other_project", req3_builder, tr2, common_builder, {}}),
      std::make_shared<SolomonRequest>(
          SolomonRequest{"project", req4_builder, tr3, common2_builder, {}}),
      std::make_shared<SolomonRequest>(
          SolomonRequest{"project", raw_builder_1, tr1, raw_builder_1, {}}),
      std::make_shared<SolomonRequest>(
          SolomonRequest{"project", raw_builder_2, tr1, raw_builder_2, {}}),
  };

  auto map = clients::SolomonHighLevelClient::MakeLowLevelRequestMap(requests);
  clients::SolomonHighLevelClient::LowLevelRequestMap expected_map{
      {{"project",
        "{common_key1='common_key1_value1',common_key2='common_"
        "key2_value1'}"},
       {{0, 1}, tr12}},
      {{"other_project",
        "{common_key1='common_key1_value1',common_key2='common_"
        "key2_value1'}"},
       {{2}, tr2}},
      {{"project",
        "{common_key1='common_key1_value1',common_key2='common_"
        "key2_value2'}"},
       {{3}, tr3}},
      {{"project", "MyProgram_1()"}, {{4}, tr1}},
      {{"project", "MyProgram_2()"}, {{5}, tr1}},
  };
  EXPECT_EQ(expected_map, map);
}

using SolomonTimeSeriesResponse =
    hejmdal::clients::models::SolomonTimeSeriesResponse;

SolomonTimeSeriesResponse MockSolomonResponse(
    std::unordered_map<std::string, std::string> labels,
    std::vector<SensorValue> values) {
  hejmdal::models::TimeSeries series{std::move(values)};
  return SolomonTimeSeriesResponse{{}, {}, labels, series};
}

std::vector<SensorValue> MockSensorValues(std::time_t from, std::time_t to,
                                          double value) {
  std::vector<SensorValue> result;
  for (; from < to; ++from) {
    result.push_back(SensorValue(MockTime(from), value));
  }
  return result;
}

TEST(SolomonHighlevelClient, MatchBatchResponseTest) {
  clients::utils::SolomonSelectorBuilder common_builder;
  common_builder.AddKeyValue("common_key1", "common_key1_value1");
  common_builder.AddKeyValue("common_key2", "common_key2_value1");
  auto req1_builder = common_builder;
  req1_builder.AddKeyValue("req1_key1", "req1_key1_value");
  auto req2_builder = common_builder;
  req2_builder.AddKeyValue("req2_key1", "req2_key1_value");
  clients::utils::SolomonSelectorBuilder common2_builder;
  common2_builder.AddKeyValue("common_key1", "common_key1_value1");
  common2_builder.AddKeyValue("common_key2", "common_key2_value2");
  auto req3_builder = common2_builder;
  req3_builder.AddKeyValue("req3_key", "req3_key_value");
  clients::utils::SolomonSelectorBuilder raw_builder_1;
  raw_builder_1.RawProgram("MyProgram_1()");
  clients::utils::SolomonSelectorBuilder raw_builder_2;
  raw_builder_2.RawProgram("MyProgram_2()");
  auto tr1 = MockTimeRange(1, 4);
  auto tr2 = MockTimeRange(2, 5);
  auto tr3 = MockTimeRange(3, 8);

  auto sr0 = std::make_shared<SolomonRequest>(
      SolomonRequest{"project", req1_builder, tr1, common_builder, {}});
  auto sr1 = std::make_shared<SolomonRequest>(
      SolomonRequest{"project", req2_builder, tr2, common_builder, {}});
  auto sr2 = std::make_shared<SolomonRequest>(
      SolomonRequest{"project", req3_builder, tr3, common2_builder, {}});
  auto sr3 = std::make_shared<SolomonRequest>(
      SolomonRequest{"project", raw_builder_1, tr3, raw_builder_1, {}});
  auto sr4 = std::make_shared<SolomonRequest>(
      SolomonRequest{"project", raw_builder_2, tr3, raw_builder_2, {}});
  std::vector<std::shared_ptr<SolomonRequest>> requests{
      sr0, sr1, sr2, sr3, sr4,
  };

  {
    std::unordered_set<size_t> indices{0, 1};
    BatchResponse batch_response{
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value1"},
                             {"req1_key1", "req1_key1_value"},
                             {"another_key", "another_value"}},
                            MockSensorValues(1, 5, 0.0)),
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value1"},
                             {"req2_key1", "req2_key1_value"},
                             {"another_key", "another_value2"}},
                            MockSensorValues(1, 3, 1.0)),
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value1"},
                             {"req2_key1", "req2_key1_value"},
                             {"another_key", "another_value3"}},
                            MockSensorValues(3, 5, 2.0))};
    EXPECT_NO_THROW(clients::SolomonHighLevelClient::MatchLowLevelResponse(
        requests, indices, {batch_response, {}}));
    EXPECT_EQ(SolomonResponse::Status::kOk, sr0->response.status);
    EXPECT_EQ(MockTime(1), sr0->response.value_series_view.front().GetTime());
    EXPECT_EQ(MockTime(3), sr0->response.value_series_view.back().GetTime());
    EXPECT_EQ(std::vector<SolomonTimeSeriesResponse>{batch_response[0]},
              sr0->response.raw_responses);

    EXPECT_EQ(SolomonResponse::Status::kOkMerged, sr1->response.status);
    EXPECT_EQ(MockTime(2), sr1->response.value_series_view.front().GetTime());
    EXPECT_DOUBLE_EQ(1.0, sr1->response.value_series_view.front().GetValue());
    EXPECT_EQ(MockTime(4), sr1->response.value_series_view.back().GetTime());
    EXPECT_DOUBLE_EQ(2.0, sr1->response.value_series_view.back().GetValue());
    auto expected_ts_vector = std::vector<SolomonTimeSeriesResponse>{
        batch_response[1], batch_response[2]};
    EXPECT_EQ(expected_ts_vector, sr1->response.raw_responses);

    EXPECT_EQ(SolomonResponse::Status::kNoData, sr2->response.status);
    EXPECT_EQ(SolomonResponse::Status::kNoData, sr3->response.status);
    EXPECT_EQ(SolomonResponse::Status::kNoData, sr4->response.status);
  }

  {
    std::unordered_set<size_t> indices{2};
    BatchResponse batch_response{
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value2"},
                             {"req3_key", "req3_key_value"},
                             {"another_key", "another_value"}},
                            MockSensorValues(3, 4, 0.0)),
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value2"},
                             {"req3_key", "req3_key_value"}},
                            MockSensorValues(5, 8, 1.0)),
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value2"},
                             {"req3_key", "req3_key_value"},
                             {"another_key", "another_value3"}},
                            MockSensorValues(4, 7, 2.0))};
    EXPECT_NO_THROW(clients::SolomonHighLevelClient::MatchLowLevelResponse(
        requests, indices, {batch_response, {}}));

    EXPECT_EQ(SolomonResponse::Status::kFailedToMerge, sr2->response.status);
    EXPECT_EQ(MockTime(3), sr2->response.value_series_view.front().GetTime());
    EXPECT_DOUBLE_EQ(0.0, sr2->response.value_series_view.front().GetValue());
    EXPECT_EQ(MockTime(6), sr2->response.value_series_view.back().GetTime());
    EXPECT_DOUBLE_EQ(2.0, sr2->response.value_series_view.back().GetValue());
    auto expected_ts_vector = std::vector<SolomonTimeSeriesResponse>{
        batch_response[0], batch_response[2], batch_response[1]};
    EXPECT_EQ(expected_ts_vector, sr2->response.raw_responses);

    EXPECT_EQ(SolomonResponse::Status::kNoData, sr3->response.status);
    EXPECT_EQ(SolomonResponse::Status::kNoData, sr4->response.status);
  }

  {
    std::unordered_set<size_t> indices{3};
    BatchResponse batch_response{
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value2"},
                             {"req3_key", "req3_key_value"},
                             {"another_key", "another_value"}},
                            MockSensorValues(3, 10, 1.0)),
    };
    EXPECT_NO_THROW(clients::SolomonHighLevelClient::MatchLowLevelResponse(
        requests, indices, {batch_response, {}}));

    EXPECT_EQ(SolomonResponse::Status::kOk, sr3->response.status);
    EXPECT_EQ(MockTime(3), sr3->response.value_series_view.front().GetTime());
    EXPECT_DOUBLE_EQ(1.0, sr3->response.value_series_view.front().GetValue());
    EXPECT_EQ(MockTime(7),  //ограничена 7, а не 9, т.к. 7 -- граница tr3
              sr3->response.value_series_view.back().GetTime());
    EXPECT_DOUBLE_EQ(1.0, sr3->response.value_series_view.back().GetValue());

    EXPECT_EQ(SolomonResponse::Status::kNoData, sr4->response.status);
  }

  {
    std::unordered_set<size_t> indices{4};
    BatchResponse batch_response{
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value1"},
                             {"req1_key1", "req1_key1_value"},
                             {"another_key", "another_value"}},
                            MockSensorValues(1, 5, 0.0)),
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value1"},
                             {"req2_key1", "req2_key1_value"},
                             {"another_key", "another_value2"}},
                            MockSensorValues(1, 3, 1.0)),
        MockSolomonResponse({{"common_key1", "common_key1_value1"},
                             {"common_key2", "common_key2_value1"},
                             {"req2_key1", "req2_key1_value"},
                             {"another_key", "another_value3"}},
                            MockSensorValues(3, 5, 2.0))};

    EXPECT_EQ(SolomonResponse::Status::kNoData, sr4->response.status);
  }
}

namespace sensors_data =
    ::clients::solomon_sensors::api_v2_projects_project_name_sensors_data::post;

class MockSolomonClient final : public clients::SolomonClient {
 public:
  virtual clients::BatchResponseInfo GetSensorsData(
      std::string_view, const hejmdal::time::TimePoint& from,
      const hejmdal::time::TimePoint& to, std::string&& program,
      const bool get_latest_data) const {
    EXPECT_FALSE(get_latest_data);
    static const std::string kProgram1 =
        "{common_key1='common_key1_value1',common_key2='common_key2_value1'}";
    static const std::string kProgram2 =
        "{common_key1='common_key1_value1',common_key2='common_key2_value2'}";
    if (from == MockTime(1) && to == MockTime(5)) {
      EXPECT_EQ(kProgram1, program);
    } else if (from == MockTime(3) && to == MockTime(9)) {
      EXPECT_EQ(kProgram2, program);
    } else {
      throw std::logic_error(
          "invalid arguments to MockSolomonClient::GetSensorsData()");
    }
    TimeSeries ts1{
        std::vector<SensorValue>{{time::From<time::Milliseconds>(1000), 0.0},
                                 {time::From<time::Milliseconds>(2000), 0.0},
                                 {time::From<time::Milliseconds>(3000), 0.0},
                                 {time::From<time::Milliseconds>(4000), 0.0}}};
    TimeSeries ts2{
        std::vector<SensorValue>{{time::From<time::Milliseconds>(3000), 1.0},
                                 {time::From<time::Milliseconds>(4000), 1.0},
                                 {time::From<time::Milliseconds>(5000), 1.0},
                                 {time::From<time::Milliseconds>(6000), 1.0},
                                 {time::From<time::Milliseconds>(7000), 1.0},
                                 {time::From<time::Milliseconds>(8000), 1.0}}};
    static std::unordered_map<std::string, clients::BatchResponseInfo>
        response_map{{kProgram1,
                      {{{"alias1",
                         "RATE",
                         {{"common_key1", "common_key1_value1"},
                          {"common_key2", "common_key2_value1"},
                          {"req1_key1", "req1_key1_value"}},
                         ts1}},
                       time::Now()}},
                     {kProgram2,
                      {{{"alias2",
                         "RATE",
                         {{"common_key1", "common_key1_value1"},
                          {"common_key2", "common_key2_value2"},
                          {"req3_key", "req3_key_value"}},
                         ts2}},
                       time::Now()}}};
    auto response = response_map.at(program);
    return response;
  }
};

TEST(SolomonHighlevelClient, GetSensorDataTest) {
  clients::utils::SolomonSelectorBuilder common_builder;
  common_builder.AddKeyValue("common_key1", "common_key1_value1");
  common_builder.AddKeyValue("common_key2", "common_key2_value1");
  auto req1_builder = common_builder;
  req1_builder.AddKeyValue("req1_key1", "req1_key1_value");
  clients::utils::SolomonSelectorBuilder common2_builder;
  common2_builder.AddKeyValue("common_key1", "common_key1_value1");
  common2_builder.AddKeyValue("common_key2", "common_key2_value2");
  auto req2_builder = common2_builder;
  req2_builder.AddKeyValue("req3_key", "req3_key_value");

  clients::utils::SolomonSelectorBuilder common3_builder;
  common3_builder.AddKeyValue("completely_different_key",
                              "completely_different_value");

  auto tr1 = MockTimeRange(1, 5);
  auto tr2 = MockTimeRange(3, 9);
  auto tr3 = MockTimeRange(5, 10);
  std::vector<std::shared_ptr<SolomonRequest>> requests{
      std::make_shared<SolomonRequest>(
          SolomonRequest{"project", req1_builder, tr1, common_builder, {}}),
      std::make_shared<SolomonRequest>(
          SolomonRequest{"project", req2_builder, tr2, common2_builder, {}}),
      std::make_shared<SolomonRequest>(SolomonRequest{
          "project", common3_builder, tr3, common3_builder, {}})};

  hejmdal::utils::SolomonSourceSettings source_settings{2, 0, {}};
  auto mock_client_ptr = std::make_shared<MockSolomonClient>();
  hejmdal::clients::SolomonHighLevelClient highlevel_client{mock_client_ptr,
                                                            source_settings};
  RunInCoro(
      [&highlevel_client, &requests]() {
        EXPECT_NO_THROW(highlevel_client.FetchSensorsData(requests));
      },
      1);

  EXPECT_EQ(SolomonResponse::Status::kOk, requests[0]->response.status);

  auto expected_values0 = MockSensorValues(1, 5, 0.0);
  EXPECT_EQ(expected_values0.size(),
            requests[0]->response.value_series_view.size());
  bool equal_in_view =
      std::equal(expected_values0.begin(), expected_values0.end(),
                 requests[0]->response.value_series_view.begin(),
                 requests[0]->response.value_series_view.end());
  EXPECT_TRUE(equal_in_view);
  SolomonTimeSeriesResponse expected_raw_response0{
      "alias1",
      "RATE",
      {{"common_key1", "common_key1_value1"},
       {"common_key2", "common_key2_value1"},
       {"req1_key1", "req1_key1_value"}},
      TimeSeries{std::move(expected_values0)}};

  EXPECT_EQ(std::vector<SolomonTimeSeriesResponse>{expected_raw_response0},
            requests[0]->response.raw_responses);

  EXPECT_EQ(SolomonResponse::Status::kOk, requests[1]->response.status);
  auto expected_values1 = MockSensorValues(3, 9, 1.0);
  EXPECT_EQ(expected_values1.size(),
            requests[1]->response.value_series_view.size());
  equal_in_view = std::equal(expected_values1.begin(), expected_values1.end(),
                             requests[1]->response.value_series_view.begin(),
                             requests[1]->response.value_series_view.end());
  EXPECT_TRUE(equal_in_view);
  SolomonTimeSeriesResponse expected_raw_response1{
      "alias2",
      "RATE",
      {{"common_key1", "common_key1_value1"},
       {"common_key2", "common_key2_value2"},
       {"req3_key", "req3_key_value"}},
      TimeSeries{std::move(expected_values1)}};

  EXPECT_EQ(std::vector<SolomonTimeSeriesResponse>{expected_raw_response1},
            requests[1]->response.raw_responses);

  EXPECT_EQ(SolomonResponse::Status::kError, requests[2]->response.status);
  EXPECT_EQ(
      "Exception during async request to solomon: invalid arguments to "
      "MockSolomonClient::GetSensorsData()",
      requests[2]->response.error);
};

}  // namespace hejmdal
