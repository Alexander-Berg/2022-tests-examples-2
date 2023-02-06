#include <gtest/gtest.h>

#include <candidates/search_settings/getter.hpp>
#include <dispatch-settings/dispatch_settings.hpp>
#include <filters/efficiency/fetch_reposition_status/fetch_reposition_status.hpp>
#include <filters/infrastructure/fetch_driver_orders/fetch_driver_orders.hpp>
#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>
#include <utils/mock_dispatch_settings.hpp>
#include "multi_limit.hpp"

namespace {

using candidates::filters::Context;
using candidates::filters::infrastructure::FetchDriverOrders;
using candidates::filters::infrastructure::FetchFinalClasses;
using candidates::result_storages::MultiLimit;

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

}  // namespace

UTEST(MultiLimitStorage, WithoutTotalLimit) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_limit = 2;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["comfort"] = setting;
  setting.query_limit_limit = 3;
  settings["econom"] = setting;
  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("comfort");
  builder["allowed_classes"].PushBack("econom");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  const auto& config = dynamic_config::GetDefaultSnapshot();
  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config);

  MultiLimit storage(json, getter, models::Classes{}, nullptr);
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 5);

  const auto context_econom = models::Classes{"econom"};
  storage.Add({{}, "id1"}, CreateContext(9, false, context_econom));
  storage.Add({{}, "id2"}, CreateContext(8, false, context_econom));
  storage.Add({{}, "id3"}, CreateContext(6, false, context_econom));
  storage.Add({{}, "id4"}, CreateContext(7, false, context_econom));
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 4);
  EXPECT_EQ(storage.expected_count(), 2);

  const auto context_comfort = models::Classes{"comfort"};
  storage.Add({{}, "id5"}, CreateContext(9, false, context_comfort));
  storage.Add({{}, "id6"}, CreateContext(8, false, context_comfort));
  storage.Add({{}, "id7"}, CreateContext(6, false, context_comfort));
  storage.Add({{}, "id8"}, CreateContext(7, false, context_comfort));
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 8);
  EXPECT_EQ(storage.expected_count(), 1);

  const auto ctx_econom_comfort = models::Classes{"econom", "comfort"};
  storage.Add({{}, "id9"}, CreateContext(7, true, ctx_econom_comfort));
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 9);
  EXPECT_EQ(storage.expected_count(), 1);

  storage.Add({{}, "id10"}, CreateContext(10, true, ctx_econom_comfort));
  EXPECT_TRUE(storage.full());
  EXPECT_EQ(storage.size(), 9);
  EXPECT_EQ(storage.expected_count(), 0);

  storage.Finish();
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 5);
  EXPECT_EQ(result[0].member.id, "id3");
  EXPECT_EQ(result[1].member.id, "id7");
  EXPECT_EQ(result[2].member.id, "id4");
  EXPECT_EQ(result[3].member.id, "id8");
  EXPECT_EQ(result[4].member.id, "id9");
}

UTEST(MultiLimitStorage, ZeroLimit) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_limit = 2;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["comfort"] = setting;
  setting.query_limit_limit = 0;
  settings["econom"] = setting;
  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("comfort");
  builder["allowed_classes"].PushBack("econom");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  const auto& config = dynamic_config::GetDefaultSnapshot();
  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config);

  MultiLimit storage(json, getter, models::Classes{}, nullptr);
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 2);

  const auto context_comfort = models::Classes{"comfort"};
  storage.Add({{}, "id1"}, CreateContext(1, true, context_comfort));
  storage.Add({{}, "id2"}, CreateContext(2, true, context_comfort));
  EXPECT_TRUE(storage.full());
  EXPECT_EQ(storage.size(), 2);
  EXPECT_EQ(storage.expected_count(), 0);
}

UTEST(MultiLimitStorage, RequiredLimits) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_limit = 2;
  std::unordered_map<std::string, dispatch_settings::models::SettingsValues>
      settings;
  settings["comfort"] = setting;
  setting.query_limit_limit = 2;
  settings["econom"] = setting;
  formats::json::ValueBuilder builder;
  builder["allowed_classes"].PushBack("comfort");
  builder["allowed_classes"].PushBack("econom");
  builder["zone_id"] = "zone";
  auto json = builder.ExtractValue();

  const auto& config = dynamic_config::GetDefaultSnapshot();
  candidates::search_settings::Getter getter(
      json, std::make_shared<utils::MockDispatchSettings>(std::move(settings)),
      nullptr, nullptr, config);

  models::Classes optional_classes({"comfort"});
  MultiLimit storage(json, getter, optional_classes, nullptr);
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 2);

  const auto context_econom = models::Classes{"econom"};
  storage.Add({{}, "id1"}, CreateContext(1, true, context_econom));
  storage.Add({{}, "id2"}, CreateContext(2, true, context_econom));
  EXPECT_TRUE(storage.full());
  EXPECT_EQ(storage.size(), 2);
  EXPECT_EQ(storage.expected_count(), 0);
}

UTEST(MultiLimitStorage, NonReposition) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_limit = 2;
  setting.no_reposition_preferred = 1;
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

  MultiLimit storage(json, getter, models::Classes{}, nullptr);
  EXPECT_FALSE(storage.full());
  EXPECT_EQ(storage.size(), 0);

  const auto context_comfort = models::Classes{"comfort"};
  storage.Add({{}, "id1"}, CreateContext(1, false, context_comfort, true));
  storage.Add({{}, "id2"}, CreateContext(4, false, context_comfort, true));
  EXPECT_FALSE(storage.full());
  storage.Add({{}, "id3"}, CreateContext(5, true, context_comfort, false));
  EXPECT_TRUE(storage.full());
  storage.Add({{}, "id4"}, CreateContext(2, false, context_comfort, true));
  storage.Add({{}, "id5"}, CreateContext(3, true, context_comfort, false));
  EXPECT_TRUE(storage.full());
  storage.Finish();
  const auto& result = storage.Get();
  ASSERT_EQ(result.size(), 3);
  EXPECT_EQ(result[0].member.id, "id1");
  EXPECT_EQ(result[1].member.id, "id4");
  EXPECT_EQ(result[2].member.id, "id5");
}

UTEST(MultiLimitStorage, ZeroLimit2) {
  dispatch_settings::models::SettingsValues setting;
  setting.query_limit_limit = 0;
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

  MultiLimit storage(json, getter, models::Classes{}, nullptr);
  EXPECT_TRUE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 0);

  const auto context_econom = models::Classes{"econom"};
  storage.Add({{}, "id1"}, CreateContext(1, true, context_econom));
  storage.Add({{}, "id2"}, CreateContext(2, true, context_econom));
  EXPECT_TRUE(storage.full());
  EXPECT_EQ(storage.size(), 0);
  EXPECT_EQ(storage.expected_count(), 0);
}
