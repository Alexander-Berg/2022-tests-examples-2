#include <userver/utest/utest.hpp>

#include <clients/billing-docs/definitions.hpp>
#include <userver/formats/serialize/common_containers.hpp>

#include <common/types.hpp>
#include <gateways/driver_work_modes/mappers.hpp>
#include <iostream>
#include <models/driver_mode.hpp>

namespace models = billing_time_events::models;
namespace mappers = billing_time_events::gateways::driver_work_modes::mappers;
namespace types = billing_time_events::types;

using Seconds = std::chrono::seconds;
using Hours = std::chrono::hours;

TEST(DriverModeTest, MapDriverModes) {
  ::clients::billing_docs::DocProjection orders_mode{};
  orders_mode.doc_id = 6;
  orders_mode.event_at = utils::datetime::GuessStringtime(
      "2018-05-09T20:00:00.000000+00:00", "UTC");
  {
    ::formats::json::ValueBuilder builder{::formats::json::Type::kObject};
    builder["driver"] = std::map<std::string, std::string>{
        {"driver_id", "uuid"}, {"park_id", "park_id"}};
    builder["mode"] = "orders";
    builder["mode_rule"] = "uberdriver";
    orders_mode.data = ::clients::billing_docs::DocProjectionData{};
    orders_mode.data->extra = builder.ExtractValue();
  }

  ::clients::billing_docs::DocProjection df_mode{};
  df_mode.doc_id = 28;
  df_mode.event_at = utils::datetime::GuessStringtime(
      "2018-05-10T20:00:00.000000+00:00", "UTC");
  {
    ::formats::json::ValueBuilder builder{::formats::json::Type::kObject};
    builder["driver"] = std::map<std::string, std::string>{
        {"driver_id", "uuid"}, {"park_id", "park_id"}};
    builder["mode"] = "driver_fix";
    builder["settings"] = std::map<std::string, std::string>{
        {"rule_id", "_id/28"}, {"shift_close_time", "00:00:00+03:00"}};
    df_mode.data = ::clients::billing_docs::DocProjectionData{};
    df_mode.data->extra = builder.ExtractValue();
  }

  ::clients::billing_docs::DocProjection no_mode{};
  no_mode.doc_id = 496;
  no_mode.event_at = utils::datetime::GuessStringtime(
      "2018-05-11T20:00:00.000000+00:00", "UTC");
  no_mode.data = ::clients::billing_docs::DocProjectionData{};
  no_mode.data->extra = ::formats::json::ValueBuilder{}.ExtractValue();

  auto modes = mappers::MapDocsToDriverModes({{orders_mode, df_mode, no_mode}});

  ASSERT_EQ(modes.size(), 3);

  EXPECT_EQ(modes[0].validity.lower(), orders_mode.event_at);
  EXPECT_EQ(modes[0].validity.upper(), df_mode.event_at);
  EXPECT_EQ(modes[0].name, models::DriverModeName::kOrders);
  EXPECT_EQ(modes[1].subscription_ref, "subscription/doc_id/28");

  EXPECT_EQ(modes[1].validity.lower(), df_mode.event_at);
  EXPECT_EQ(modes[1].validity.upper(), no_mode.event_at);
  ASSERT_TRUE(modes[1].settings);
  auto details = *modes[1].settings;
  EXPECT_EQ(details.shift_close_time, Seconds{Hours{21}});
  EXPECT_EQ(details.rule_id, "_id/28");

  EXPECT_EQ(modes[2].validity.lower(), no_mode.event_at);
  EXPECT_EQ(modes[2].validity.upper(), types::TimePoint::max());
  EXPECT_EQ(modes[2].name, models::DriverModeName::kOrders);
}

TEST(DriverModeTest, TestDocsOrdering) {
  ::clients::billing_docs::DocProjection first{};
  first.doc_id = 6;
  first.event_at = utils::datetime::GuessStringtime(
      "2018-05-09T20:00:00.000000+00:00", "UTC");
  first.data = ::clients::billing_docs::DocProjectionData{};
  first.data->extra = ::formats::json::ValueBuilder{}.ExtractValue();

  ::clients::billing_docs::DocProjection second{};
  second.doc_id = 28;
  second.event_at = utils::datetime::GuessStringtime(
      "2018-05-10T20:00:00.000000+00:00", "UTC");
  second.data = ::clients::billing_docs::DocProjectionData{};
  second.data->extra = ::formats::json::ValueBuilder{}.ExtractValue();

  ::clients::billing_docs::DocProjection third{};
  third.doc_id = 496;
  third.event_at = utils::datetime::GuessStringtime(
      "2018-05-11T20:00:00.000000+00:00", "UTC");
  third.data = ::clients::billing_docs::DocProjectionData{};
  third.data->extra = ::formats::json::ValueBuilder{}.ExtractValue();

  auto modes = mappers::MapDocsToDriverModes({{third, first, second}});

  ASSERT_EQ(modes.size(), 3);

  EXPECT_EQ(modes[0].validity.lower(), first.event_at);
  EXPECT_EQ(modes[0].validity.upper(), second.event_at);

  EXPECT_EQ(modes[1].validity.lower(), second.event_at);
  EXPECT_EQ(modes[1].validity.upper(), third.event_at);

  EXPECT_EQ(modes[2].validity.lower(), third.event_at);
  EXPECT_EQ(modes[2].validity.upper(), types::TimePoint::max());
}
