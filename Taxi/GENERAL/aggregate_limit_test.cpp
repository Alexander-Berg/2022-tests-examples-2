#include <gtest/gtest.h>

#include <candidates/search_settings/getter.hpp>
#include <dispatch-settings/dispatch_settings.hpp>
#include <filters/efficiency/fetch_chain_info/fetch_chain_info.hpp>
#include <filters/infrastructure/fetch_driver_orders/fetch_driver_orders.hpp>
#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>
#include <utils/mock_dispatch_settings.hpp>
#include "aggregate_limit.hpp"

namespace {

using candidates::filters::Context;
using candidates::filters::efficiency::FetchChainInfo;
using candidates::filters::infrastructure::FetchDriverOrders;
using candidates::filters::infrastructure::FetchFinalClasses;
using candidates::result_storages::AggregateLimit;

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

}  // namespace

UTEST(AggregateLimitStorage, WithTotalLimit) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_limit = 5;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["econom"] = setting;
  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("econom");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  const auto& config = dynamic_config::GetDefaultSnapshot();
  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config);

  AggregateLimit storage(json, getter, nullptr);
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 5);
  EXPECT_EQ(storage.worst_score(), std::nullopt);

  const auto context_econom = models::Classes{"econom"};
  storage.Add({{}, "id1"}, CreateContext(9, false, context_econom));
  storage.Add({{}, "id2"}, CreateContext(8, false, context_econom));
  storage.Add({{}, "id3"}, CreateContext(6, false, context_econom));
  storage.Add({{}, "id4"}, CreateContext(7, false, context_econom));
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 4);
  EXPECT_EQ(storage.expected_count(), 1);
  EXPECT_EQ(*storage.worst_score(), 9);

  const auto context_comfort = models::Classes{"comfort"};
  storage.Add({{}, "id5"}, CreateContext(9, false, context_comfort));
  storage.Add({{}, "id6"}, CreateContext(8, false, context_comfort));
  storage.Add({{}, "id7"}, CreateContext(6, false, context_comfort));
  storage.Add({{}, "id8"}, CreateContext(7, false, context_comfort));
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 8);
  EXPECT_EQ(storage.expected_count(), 1);
  EXPECT_EQ(*storage.worst_score(), 9);

  const auto ctx_econom_comfort = models::Classes{"econom", "comfort"};
  storage.Add({{}, "id9"}, CreateContext(7, true, ctx_econom_comfort));
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 9);
  EXPECT_EQ(storage.expected_count(), 1);
  EXPECT_EQ(*storage.worst_score(), 9);

  storage.Add({{}, "id10"}, CreateContext(10, true, ctx_econom_comfort));
  EXPECT_TRUE(storage.full());
  EXPECT_EQ(storage.size(), 9);
  EXPECT_EQ(storage.expected_count(), 0);
  EXPECT_EQ(*storage.worst_score(), 9);

  storage.Finish();
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 5);
  EXPECT_EQ(result[0].member.id, "id3");
  EXPECT_EQ(result[1].member.id, "id7");
  EXPECT_EQ(result[2].member.id, "id4");
  EXPECT_EQ(result[3].member.id, "id8");
  EXPECT_EQ(result[4].member.id, "id9");
}

UTEST(AggregateLimitStorage, ZeroLimits) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_limit = 0;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["comfort"] = setting;
  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("comfort");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  const auto& config = dynamic_config::GetDefaultSnapshot();
  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config);

  AggregateLimit storage(json, getter, nullptr);
  EXPECT_TRUE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 0);

  const auto context_comfort = models::Classes{"comfort"};
  storage.Add({{}, "id1"}, CreateContext(1, true, context_comfort));
  EXPECT_TRUE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 0);
}

UTEST(AggregateLimitStorage, ParkCounter) {
  formats::json::Value params = formats::json::FromString(R"=(
  {
    "order": {
      "request": {
        "white_label_requirements": {
          "source_park_id": "dbid0",
          "dispatch_requirement": "source_park_and_all"
        }
      }
    }
  }
  )=");
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_limit = 4;
  setting.same_park_preferred = 3;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["comfort"] = setting;
  formats::json::ValueBuilder builder(params);
  builder["allowed_classes"].PushBack("comfort");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  const auto& config = dynamic_config::GetDefaultSnapshot();
  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config);

  AggregateLimit storage(json, getter, nullptr);

  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);

  const auto context = models::Classes{"comfort"};
  storage.Add({{}, "dbid0_uuid0"}, CreateContext(1, true, context));
  storage.Add({{}, "dbid0_uuid1"}, CreateContext(4, true, context));
  EXPECT_FALSE(storage.full());
  storage.Add({{}, "dbid1_uuid0"}, CreateContext(5, true, context));
  storage.Add({{}, "dbid1_uuid1"}, CreateContext(6, true, context));
  EXPECT_FALSE(storage.full());
  storage.Add({{}, "dbid0_uuid2"}, CreateContext(8, true, context));
  EXPECT_TRUE(storage.full());
  storage.Finish();
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 4);
  EXPECT_EQ(result[0].member.id, "dbid0_uuid0");
  EXPECT_EQ(result[1].member.id, "dbid0_uuid1");
  EXPECT_EQ(result[2].member.id, "dbid1_uuid0");
  EXPECT_EQ(result[3].member.id, "dbid0_uuid2");
}

UTEST(AggregateLimitStorage, PerfectChainCounter) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_limit = 2;
  setting.chain_preferred = 1;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["comfort"] = setting;
  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("comfort");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  const auto& config = dynamic_config::GetDefaultSnapshot();
  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config);

  AggregateLimit storage(json, getter, nullptr);

  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);

  models::Classes classes{"comfort"};
  storage.Add({{}, "dbid0_uuid0"}, CreateContext(1, true, classes));

  auto chain_context = CreateContext(5, true, classes);
  FetchChainInfo::Set(chain_context,
                      std::make_shared<models::ChainBusyDriver>());
  storage.Add({{}, "dbid1_uuid0"}, std::move(chain_context));
  EXPECT_TRUE(storage.full());

  storage.Add({{}, "dbid0_uuid1"}, CreateContext(4, true, classes));
  EXPECT_EQ(storage.size(), 3);
  EXPECT_TRUE(storage.full());

  storage.Finish();

  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 2);
  EXPECT_EQ(result[0].member.id, "dbid0_uuid0");
  EXPECT_EQ(result[1].member.id, "dbid1_uuid0");
}
