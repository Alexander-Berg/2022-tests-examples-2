#include <gtest/gtest.h>

#include <memory>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <defs/definitions/location_settings.hpp>
#include <metrix/writer.hpp>
#include <models/history_points.hpp>

#include <taxi_config/variables/METRIX_AGGREGATION.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/dynamic_config/source.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json.hpp>

#include "on_jump_or_divergence_select_by_priority.hpp"

namespace {
using namespace coord_control;
using namespace coord_control::components;
using namespace ::geometry;

using Min = std::chrono::minutes;
using Sec = std::chrono::seconds;
using Milli = std::chrono::milliseconds;

const std::string kZoneName{"test_zone"};
const std::string kMetricZone{"metric_test_zone"};

const std::string kMetrixConfig{R"json(
[{
    "rule": {
        "and": [{"none_of": [""]}]},
    "value": [
        {
            "rule_type": "grouping",
            "label_name": "tariff_group",
            "groups": [
                {
                    "group_name": "econom_group",
                    "values": ["econom", "uberstart"]
                },
                {
                    "group_name": "business_group",
                    "values": ["business", "comfortplus"]
                }
            ],
            "use_others": false
        }
    ]
}])json"};
}  // namespace

UTEST(strategies_jump_by_priority, choose_primary) {
  auto now = ::utils::datetime::Now();
  ::utils::datetime::MockNowSet(now);

  coord_control::models::PointsStorage history_points;
  history_points.points[0].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 37.634453 * lon)}}};
  history_points.points[1].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 37.634453 * lon)}}};
  history_points.points[5].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 37.634453 * lon)}}};

  PositionsHistory::HistoryPtr concurrent_history_ptr =
      std::make_shared<PositionsHistory::ConcurrentHistoryValue>(
          std::move(history_points));
  PositionsHistory::PrimaryGroupPtr concurrent_primary_group_ptr =
      std::make_shared<PositionsHistory::ConcurrentPrimaryGroupValue>();
  PositionsHistory::BadAreaDict::ValuePtr bad_area_ptr{
      std::make_shared<PositionsHistory::BadAreaDict::ConcurrentValue>()};

  coord_control::models::PriorityStrategyBackend backend_settings;
  backend_settings.strategy_type =
      handlers::StrategyType::kOnJumpOrDivergenceSelectByPriority;
  backend_settings.primarygroup = {handlers::SourceType::kAndroidGps};
  backend_settings.alternativegroups = {
      {handlers::SourceType::kAndroidNetwork}};
  backend_settings.referencegroups = {{handlers::SourceType::kYandexLbsGsm}};

  backend_settings.referencemaxspeedms = 500;
  backend_settings.referencejitterthresholdms = Milli(10000);
  backend_settings.referencejumpdiscardtimeoutms = Milli(60000);

  coord_control::models::PriorityStrategyClient client_settings;
  client_settings.maxspeedms = 500;
  client_settings.jitterthresholdms = Milli(10000);
  client_settings.locationtimeoutms = Milli(30000);
  client_settings.referencetimeoutms = Milli(60000);
  client_settings.jumpdiscardtimeoutms = Milli(60000);

  const dynamic_config::StorageMock storage_{
      {taxi_config::METRIX_AGGREGATION,
       formats::json::FromString(kMetrixConfig)}};
  auto metrix_writer_ptr =
      std::make_shared<metrix::Writer>(storage_.GetSource());

  coord_control::models::StrategyContext strategy_context{
      concurrent_history_ptr,
      concurrent_primary_group_ptr,
      bad_area_ptr,
      backend_settings,
      client_settings,
      coord_control::models::StrategyType::kRealtime,
      kZoneName,
      kMetricZone,
      *metrix_writer_ptr,
      nullptr};

  auto response =
      ::utils::Async("test_strategy", [&]() {
        return strategy::CalculateOnJumpOrDivergenceSelectByPriority(
            strategy_context);
      }).Get();

  coord_control::models::PriorityStrategy true_response;

  true_response.strategy_type =
      handlers::StrategyType::kOnJumpOrDivergenceSelectByPriority;
  true_response.primarygroup = {handlers::SourceType::kAndroidGps};
  true_response.alternativegroups = {{handlers::SourceType::kAndroidNetwork}};
  true_response.referencegroups = {{handlers::SourceType::kYandexLbsGsm}};

  true_response.maxspeedms = 500;
  true_response.jitterthresholdms = Milli(10000);
  true_response.locationtimeoutms = Milli(30000);
  true_response.referencetimeoutms = Milli(60000);
  true_response.jumpdiscardtimeoutms = Milli(60000);

  EXPECT_EQ(response, true_response);
}

UTEST(strategies_jump_by_priority, bad_primary_detect_jump) {
  auto now = ::utils::datetime::Now();
  ::utils::datetime::MockNowSet(now);

  coord_control::models::PointsStorage history_points;
  // primary
  // jump
  history_points.points[0].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 38.634453 * lon)}},
  };
  // alternative
  history_points.points[1].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 37.634453 * lon)}},
  };
  // jump
  history_points.points[2].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 38.634453 * lon)}},
  };
  history_points.points[3].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 37.634453 * lon)}},
  };
  // reference
  history_points.points[5].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 37.634453 * lon)}},
  };

  PositionsHistory::HistoryPtr concurrent_history_ptr =
      std::make_shared<PositionsHistory::ConcurrentHistoryValue>(
          std::move(history_points));
  PositionsHistory::PrimaryGroupPtr concurrent_primary_group_ptr =
      std::make_shared<PositionsHistory::ConcurrentPrimaryGroupValue>();
  PositionsHistory::BadAreaDict::ValuePtr bad_area_ptr{
      std::make_shared<PositionsHistory::BadAreaDict::ConcurrentValue>()};

  coord_control::models::PriorityStrategyBackend backend_settings;
  backend_settings.strategy_type =
      handlers::StrategyType::kOnJumpOrDivergenceSelectByPriority;
  backend_settings.primarygroup = {handlers::SourceType::kAndroidGps};
  backend_settings.alternativegroups = {
      {handlers::SourceType::kAndroidNetwork},
      {handlers::SourceType::kAndroidFused,
       handlers::SourceType::kAndroidPassive}};
  backend_settings.referencegroups = {{handlers::SourceType::kYandexLbsGsm}};

  backend_settings.referencemaxspeedms = 500;
  backend_settings.referencejitterthresholdms = Milli(10000);
  backend_settings.referencejumpdiscardtimeoutms = Milli(60000);

  coord_control::models::PriorityStrategyClient client_settings;
  client_settings.maxspeedms = 500;
  client_settings.jitterthresholdms = Milli(10000);
  client_settings.locationtimeoutms = Milli(30000);
  client_settings.jumpdiscardtimeoutms = Milli(60000);

  const dynamic_config::StorageMock storage_{
      {taxi_config::METRIX_AGGREGATION,
       formats::json::FromString(kMetrixConfig)}};
  auto metrix_writer_ptr =
      std::make_shared<metrix::Writer>(storage_.GetSource());

  coord_control::models::StrategyContext strategy_context{
      concurrent_history_ptr,
      concurrent_primary_group_ptr,
      bad_area_ptr,
      backend_settings,
      client_settings,
      coord_control::models::StrategyType::kRealtime,
      kZoneName,
      kMetricZone,
      *metrix_writer_ptr,
      nullptr};
  auto response =
      ::utils::Async("test_strategy", [&strategy_context]() {
        return strategy::CalculateOnJumpOrDivergenceSelectByPriority(
            strategy_context);
      }).Get();

  coord_control::models::PriorityStrategy true_response;

  true_response.strategy_type =
      handlers::StrategyType::kOnJumpOrDivergenceSelectByPriority;
  true_response.primarygroup = {handlers::SourceType::kAndroidNetwork};
  true_response.alternativegroups = {{handlers::SourceType::kAndroidPassive}};
  true_response.referencegroups = {{handlers::SourceType::kYandexLbsGsm}};

  true_response.maxspeedms = 500;
  true_response.jitterthresholdms = Milli(10000);
  true_response.locationtimeoutms = Milli(30000);
  true_response.jumpdiscardtimeoutms = Milli(60000);

  EXPECT_EQ(response, true_response);
}

UTEST(strategies_jump_by_priority, exclude_by_reference) {
  auto now = ::utils::datetime::Now();
  ::utils::datetime::MockNowSet(now);

  coord_control::models::PointsStorage history_points;
  // primary
  // far away from reference
  history_points.points[0].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 37.634453 * lon)}},
  };
  // alternative
  history_points.points[1].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 38.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 38.634453 * lon)}},
  };
  // far away from reference
  history_points.points[2].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 37.634453 * lon)}},
  };
  // jump
  history_points.points[3].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 37.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 38.634453 * lon)}},
  };
  // reference
  history_points.points[5].map = {
      {now - Sec(5), {geometry::Position(55.731637 * lat, 38.635328 * lon)}},
      {now - Sec(10), {geometry::Position(55.732957 * lat, 38.634453 * lon)}},
  };

  PositionsHistory::HistoryPtr concurrent_history_ptr =
      std::make_shared<PositionsHistory::ConcurrentHistoryValue>(
          history_points);
  PositionsHistory::PrimaryGroupPtr concurrent_primary_group_ptr =
      std::make_shared<PositionsHistory::ConcurrentPrimaryGroupValue>();
  PositionsHistory::BadAreaDict::ValuePtr bad_area_ptr{
      std::make_shared<PositionsHistory::BadAreaDict::ConcurrentValue>()};

  coord_control::models::PriorityStrategyBackend backend_settings;
  backend_settings.strategy_type =
      handlers::StrategyType::kOnJumpOrDivergenceSelectByPriority;
  backend_settings.primarygroup = {handlers::SourceType::kAndroidGps};
  backend_settings.alternativegroups = {
      {handlers::SourceType::kAndroidNetwork},
      {handlers::SourceType::kAndroidFused,
       handlers::SourceType::kAndroidPassive}};
  backend_settings.referencegroups = {{handlers::SourceType::kYandexLbsGsm}};

  backend_settings.referencemaxspeedms = 500;
  backend_settings.referencejitterthresholdms = Milli(10000);
  backend_settings.referencejumpdiscardtimeoutms = Milli(60000);

  coord_control::models::PriorityStrategyClient client_settings;
  client_settings.maxspeedms = 500;
  client_settings.jitterthresholdms = Milli(10000);
  client_settings.locationtimeoutms = Milli(30000);
  client_settings.jumpdiscardtimeoutms = Milli(60000);

  const dynamic_config::StorageMock storage_{
      {taxi_config::METRIX_AGGREGATION,
       formats::json::FromString(kMetrixConfig)}};
  auto metrix_writer_ptr =
      std::make_shared<metrix::Writer>(storage_.GetSource());

  coord_control::models::StrategyContext strategy_context{
      concurrent_history_ptr,
      concurrent_primary_group_ptr,
      bad_area_ptr,
      backend_settings,
      client_settings,
      coord_control::models::StrategyType::kRealtime,
      kZoneName,
      kMetricZone,
      *metrix_writer_ptr,
      nullptr};
  auto response =
      ::utils::Async("test_strategy", [&strategy_context]() {
        return strategy::CalculateOnJumpOrDivergenceSelectByPriority(
            strategy_context);
      }).Get();

  coord_control::models::PriorityStrategy true_response;

  true_response.strategy_type =
      handlers::StrategyType::kOnJumpOrDivergenceSelectByPriority;
  true_response.primarygroup = {handlers::SourceType::kAndroidNetwork};
  true_response.referencegroups = {{handlers::SourceType::kYandexLbsGsm}};

  true_response.maxspeedms = 500;
  true_response.jitterthresholdms = Milli(10000);
  true_response.locationtimeoutms = Milli(30000);
  true_response.jumpdiscardtimeoutms = Milli(60000);

  EXPECT_EQ(response, true_response);

  concurrent_history_ptr =
      std::make_shared<PositionsHistory::ConcurrentHistoryValue>(
          std::move(history_points));
  backend_settings.referencemaxspeedms = 2500;
  backend_settings.referencejitterthresholdms = Milli(30000);
  backend_settings.referencejumpdiscardtimeoutms = Milli(60000);

  coord_control::models::StrategyContext strategy_context_changed{
      concurrent_history_ptr,
      concurrent_primary_group_ptr,
      bad_area_ptr,
      backend_settings,
      client_settings,
      coord_control::models::StrategyType::kRealtime,
      kZoneName,
      kMetricZone,
      *metrix_writer_ptr,
      nullptr};
  response = ::utils::Async("test_strategy", [&strategy_context_changed]() {
               return strategy::CalculateOnJumpOrDivergenceSelectByPriority(
                   strategy_context_changed);
             }).Get();

  true_response.primarygroup = {handlers::SourceType::kAndroidGps};
  true_response.alternativegroups = backend_settings.alternativegroups;

  EXPECT_EQ(response, true_response);
}
