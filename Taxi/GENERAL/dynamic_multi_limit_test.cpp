#include "dynamic_multi_limit.hpp"

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/CANDIDATES_FEATURE_SWITCHES.hpp>
#include <taxi_config/variables/CANDIDATES_ORDER_MULTISEARCH_DEGRADATION.hpp>
#include <userver/utest/utest.hpp>
#include <utils/mock_dispatch_settings.hpp>

#include <candidates/search_settings/getter.hpp>
#include <filters/efficiency/fetch_reposition_status/fetch_reposition_status.hpp>
#include <filters/infrastructure/fetch_driver_orders/fetch_driver_orders.hpp>
#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include <filters/infrastructure/fetch_route_info/fetch_route_info.hpp>

namespace {

using candidates::filters::Context;
using candidates::filters::infrastructure::FetchDriverOrders;
using candidates::filters::infrastructure::FetchFinalClasses;
using candidates::filters::infrastructure::FetchRouteInfo;
using candidates::result_storages::DynamicMultiLimit;
namespace config = taxi_config::candidates_order_multisearch_dynamic_limits;

Context CreateContext(uint32_t score, const bool is_free,
                      const models::Classes& classes) {
  Context context(score);

  if (!is_free) {
    const auto orders = std::make_shared<models::driver_orders::Orders>();
    orders->emplace_back("1", "yandex", models::driver_orders::Status::Driving,
                         std::chrono::system_clock::now());
    FetchDriverOrders::Set(context, orders);
  }
  FetchFinalClasses::Set(context, classes);
  return context;
}

Context CreateContext(uint32_t score, const bool is_free,
                      const models::Classes& classes, bool is_reposition) {
  auto context = CreateContext(score, is_free, classes);
  candidates::filters::efficiency::FetchRepositionStatus::Set(
      context, clients::reposition::IndexEntry{false, false, is_reposition});
  return context;
}

dynamic_config::StorageMock CreateConfig(const std::string& val) {
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::CANDIDATES_ORDER_MULTISEARCH_DYNAMIC_LIMITS,
        formats::json::FromString(val)}});
}

dynamic_config::StorageMock CreateConfig(const std::string& limits,
                                         const std::string& degradation) {
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::CANDIDATES_ORDER_MULTISEARCH_DYNAMIC_LIMITS,
        formats::json::FromString(limits)},
       {taxi_config::CANDIDATES_ORDER_MULTISEARCH_DEGRADATION,
        formats::json::FromString(degradation)}});
}

}  // namespace

UTEST(DynamicMultiLimitStorage, ScoreClass) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_max_line_dist = 20;
  setting.query_limit_limit = 4;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["econom"] = setting;

  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("econom");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  auto config = CreateConfig(R"({
    "econom": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 10,
      "extra_time": 5
    }
  })");

  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config.GetSnapshot());

  DynamicMultiLimit storage(json, getter, {}, config.GetSnapshot(), nullptr,
                            {});
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 4);

  const auto context_econom = models::Classes{"econom"};
  storage.Add({{}, "id1"}, CreateContext(1, true, context_econom));

  auto search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id2"}, CreateContext(2, true, context_econom));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 12);

  storage.Add({{}, "id3"}, CreateContext(22, true, context_econom));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 12);

  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 3);
  EXPECT_EQ(storage.expected_count(), 1);
}

UTEST(DynamicMultiLimitStorage, ScoreClasses) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_max_line_dist = 9;
  setting.query_limit_limit = 4;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["econom"] = setting;

  setting.query_limit_max_line_dist = 20;
  settings["comfort"] = setting;

  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("econom");
  builder["allowed_classes"].PushBack("comfort");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  auto config = CreateConfig(R"({
    "econom": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 10,
      "extra_time": 5
    },
    "comfort": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 10,
      "extra_time": 5
    }
  })");

  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config.GetSnapshot());

  DynamicMultiLimit storage(json, getter, {}, config.GetSnapshot(), nullptr,
                            {});
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 8);

  storage.Add({{}, "id1"}, CreateContext(1, true, models::Classes{"econom"}));
  storage.Add({{}, "id3"}, CreateContext(1, true, models::Classes{"comfort"}));

  auto search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id2"}, CreateContext(2, true, models::Classes{"econom"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id4"}, CreateContext(3, true, models::Classes{"comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 13);

  storage.Add({{}, "id5"},
              CreateContext(5, true, models::Classes{"econom", "comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 13);

  storage.Add({{}, "id6"}, CreateContext(1, true, models::Classes{"comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 9);

  storage.Add({{}, "id7"},
              CreateContext(4, true, models::Classes{"econom", "comfort"}));
  EXPECT_TRUE(storage.full());
  storage.Add({{}, "id8"}, CreateContext(2, true, models::Classes{"comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 0);

  EXPECT_TRUE(storage.full());

  storage.Finish();
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 8);
  EXPECT_EQ(result[0].member.id, "id1");
  EXPECT_EQ(result[1].member.id, "id3");
  EXPECT_EQ(result[2].member.id, "id6");
  EXPECT_EQ(result[3].member.id, "id2");
  EXPECT_EQ(result[4].member.id, "id8");
  EXPECT_EQ(result[5].member.id, "id4");
  EXPECT_EQ(result[6].member.id, "id7");
  EXPECT_EQ(result[7].member.id, "id5");
}

UTEST(DynamicMultiLimitStorage, FullCounters) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_max_line_dist = 9;
  setting.query_limit_limit = 5;
  setting.no_reposition_preferred = 3;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["econom"] = setting;

  setting.query_limit_limit = 4;
  setting.query_limit_max_line_dist = 20;
  setting.no_reposition_preferred = 2;
  settings["comfort"] = setting;

  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("econom");
  builder["allowed_classes"].PushBack("comfort");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  auto config = CreateConfig(R"({
    "econom": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 3,
      "extra_time": 5
    },
    "comfort": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 10,
      "extra_time": 5
    }
  })");

  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config.GetSnapshot());

  DynamicMultiLimit storage(json, getter, {}, config.GetSnapshot(), nullptr,
                            {});
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 9);

  storage.Add({{}, "id1"}, CreateContext(1, true, models::Classes{"econom"}));
  storage.Add({{}, "id3"}, CreateContext(1, true, models::Classes{"comfort"}));

  auto search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id2"},
              CreateContext(2, true, models::Classes{"econom"}, true));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id4"},
              CreateContext(3, true, models::Classes{"comfort"}, true));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id5"}, CreateContext(3, true, models::Classes{"comfort"}));
  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 13);

  storage.Add({{}, "id6"},
              CreateContext(5, true, models::Classes{"econom", "comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 9);

  storage.Add({{}, "id7"},
              CreateContext(4, true, models::Classes{"econom", "comfort"}));
  EXPECT_FALSE(storage.full());

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 8);

  storage.Add({{}, "id8"}, CreateContext(2, true, models::Classes{"econom"}));

  EXPECT_TRUE(storage.full());

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 0);

  EXPECT_TRUE(storage.full());

  storage.Finish();
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 8);
  EXPECT_EQ(result[0].member.id, "id1");
  EXPECT_EQ(result[1].member.id, "id3");
  EXPECT_EQ(result[2].member.id, "id2");
  EXPECT_EQ(result[3].member.id, "id8");
  EXPECT_EQ(result[4].member.id, "id4");
  EXPECT_EQ(result[5].member.id, "id5");
  EXPECT_EQ(result[6].member.id, "id7");
  EXPECT_EQ(result[7].member.id, "id6");
}

UTEST(DynamicMultiLimitStorage, ExtendedRadius) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_max_line_dist = 9;
  setting.query_limit_limit = 4;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["econom"] = setting;

  setting.query_limit_max_line_dist = 20;
  settings["comfort"] = setting;

  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("econom");
  builder["allowed_classes"].PushBack("comfort");
  builder["zone_id"] = "zone";
  builder["search_settings"]["econom"]["extended_radius"] = true;
  builder["search_settings"]["comfort"]["extended_radius"] = true;
  auto json = builder.ExtractValue();

  auto config = CreateConfig(R"({
    "econom": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 10,
      "extra_time": 5
    },
    "comfort": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 20,
      "extra_time": 5
    }
  })");

  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config.GetSnapshot());

  DynamicMultiLimit storage(json, getter, {}, config.GetSnapshot(), nullptr,
                            {});
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 8);

  storage.Add({{}, "id1"}, CreateContext(1, true, models::Classes{"econom"}));
  storage.Add({{}, "id3"}, CreateContext(1, true, models::Classes{"comfort"}));

  auto search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 40);

  storage.Add({{}, "id2"}, CreateContext(10, true, models::Classes{"econom"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 40);

  storage.Add({{}, "id4"}, CreateContext(3, true, models::Classes{"comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id5"},
              CreateContext(5, true, models::Classes{"econom", "comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id6"}, CreateContext(1, true, models::Classes{"comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 18);

  storage.Add({{}, "id7"},
              CreateContext(4, true, models::Classes{"econom", "comfort"}));
  EXPECT_TRUE(storage.full());
  storage.Add({{}, "id8"}, CreateContext(2, true, models::Classes{"comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 0);

  EXPECT_TRUE(storage.full());

  storage.Finish();
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 8);
  EXPECT_EQ(result[0].member.id, "id1");
  EXPECT_EQ(result[1].member.id, "id3");
  EXPECT_EQ(result[2].member.id, "id6");
  EXPECT_EQ(result[3].member.id, "id8");
  EXPECT_EQ(result[4].member.id, "id4");
  EXPECT_EQ(result[5].member.id, "id7");
  EXPECT_EQ(result[6].member.id, "id5");
  EXPECT_EQ(result[7].member.id, "id2");
}

UTEST(DynamicMultiLimitStorage, Degradation) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_max_line_dist = 10;
  setting.query_limit_limit = 4;
  setting.max_robot_time = 20;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["econom"] = setting;

  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("econom");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  auto config = CreateConfig(R"({
    "econom": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 10,
      "extra_time": 10
    }
  })",
                             R"({
    "enabled": true,
    "increased_coef": {
        "extra_score": 0.7
    },
    "high_coef": {
        "extra_score": 0.5
    },
    "critical_coef": {
        "extra_score": 0.3
    }
  })");

  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config.GetSnapshot());

  DynamicMultiLimit storage(json, getter, {}, config.GetSnapshot(), nullptr,
                            {workers::SystemDiagnostics::CpuLoad::kCritical});
  EXPECT_FALSE(storage.full());

  auto context1 = CreateContext(1, true, models::Classes{"econom"});
  FetchRouteInfo::Set(context1, models::RouteInfo{});
  storage.Add({{}, "id1"}, std::move(context1));

  auto search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_route_time.count(), 20);

  auto context2 = CreateContext(3, true, models::Classes{"econom"});
  FetchRouteInfo::Set(context2, models::RouteInfo{});
  storage.Add({{}, "id2"}, std::move(context2));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_route_time.count(), 6);
}

UTEST(DynamicMultiLimitStorage, FullLimitCounters) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_max_line_dist = 9;
  setting.query_limit_limit = 2;
  setting.no_reposition_preferred = 2;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["econom"] = setting;

  setting.query_limit_limit = 2;
  setting.query_limit_max_line_dist = 20;
  setting.no_reposition_preferred = 2;
  settings["comfort"] = setting;

  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("econom");
  builder["allowed_classes"].PushBack("comfort");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  auto config = CreateConfig(R"({
    "econom": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 3,
      "extra_time": 5
    },
    "comfort": {
      "enabled": true,
      "min_count": 2,
      "extra_line_distance": 10,
      "extra_time": 5
    }
  })");

  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config.GetSnapshot());

  DynamicMultiLimit storage(json, getter, {}, config.GetSnapshot(), nullptr,
                            {});
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 4);

  storage.Add({{}, "id1"}, CreateContext(1, true, models::Classes{"econom"}));
  storage.Add({{}, "id3"}, CreateContext(1, true, models::Classes{"comfort"}));

  auto search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id2"},
              CreateContext(2, true, models::Classes{"econom"}, true));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id4"},
              CreateContext(3, true, models::Classes{"comfort"}, true));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 20);

  storage.Add({{}, "id5"}, CreateContext(3, true, models::Classes{"comfort"}));
  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 9);

  storage.Add({{}, "id6"},
              CreateContext(5, true, models::Classes{"econom", "comfort"}));

  search_limits = storage.GetSearchLimits();
  ASSERT_TRUE(search_limits);
  EXPECT_EQ(search_limits->max_distance, 0);

  EXPECT_TRUE(storage.full());

  storage.Finish();
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 5);
  EXPECT_EQ(result[0].member.id, "id1");
  EXPECT_EQ(result[1].member.id, "id3");
  EXPECT_EQ(result[2].member.id, "id2");
  EXPECT_EQ(result[3].member.id, "id4");
  EXPECT_EQ(result[4].member.id, "id6");
}
