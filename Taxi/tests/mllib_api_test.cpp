#include <gtest/gtest.h>

#include <clients/routehistory/client.hpp>
#include <clients/userplaces/client.hpp>
#include <models/mllib/common.hpp>
#include <testing/source_path.hpp>
#include <userver/formats/json.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/fs/blocking/read.hpp>
#include <userver/utest/utest.hpp>

namespace test::models::mllib {

using namespace umlaas_geo::models::mllib;
using clients::eats_ordershistory::GetOrdersResponse;
using clients::eats_ordershistory::OrderSource;
using clients::eats_ordershistory::OrderStatus;
using clients::routehistory::RouteHistoryGetResponse;
using clients::routehistory::RouteHistorySearchGetResponse;
using clients::userplaces::UserplacesListResponse;

formats::json::Value LoadJson(const std::string& file_name) {
  auto contents = fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("tests/static/" + file_name));
  return formats::json::FromString(contents);
}

TEST(TestMLLibApi, Userplaces) {
  auto contents = LoadJson("userplaces_list_response.json");
  auto userplaces_response = clients::userplaces::Parse(
      contents, formats::parse::To<UserplacesListResponse>());
  auto userplaces = mllib::ToUserplaces(std::move(userplaces_response));

  EXPECT_EQ(userplaces.size(), 2);
  EXPECT_EQ(userplaces[0].id, "id1");
  EXPECT_EQ(userplaces[0].version, 1);
  EXPECT_EQ(userplaces[0].created, utils::datetime::GuessStringtime(
                                       "2020-01-03T11:22:33+0000", "UTC"));
  EXPECT_EQ(userplaces[0].updated, utils::datetime::GuessStringtime(
                                       "2020-02-04T11:22:33+0000", "UTC"));
  EXPECT_EQ(userplaces[0].name, "name1");
  EXPECT_EQ(userplaces[0].place_type, "work");
  EXPECT_EQ(userplaces[0].comment, "Заезд во двор");
  EXPECT_EQ(userplaces[0].description, "Москва, Россия");
  EXPECT_EQ(userplaces[0].geoaddress.full_text,
            "Россия, Москва, Садовническая улица, 82с2");
  EXPECT_EQ(userplaces[0].geoaddress.short_text, "Садовническая ул., 82с2");
  EXPECT_EQ(userplaces[0].geoaddress.entrance, "4");
  EXPECT_EQ(userplaces[0].geoaddress.uri, "ymapsbm1://geo?exit1");
  EXPECT_EQ(userplaces[0].geoaddress.type, "address");
  EXPECT_DOUBLE_EQ(userplaces[0].geoaddress.geopoint.lon, 37.1);
  EXPECT_DOUBLE_EQ(userplaces[0].geoaddress.geopoint.lat, 55.1);
  EXPECT_EQ(userplaces[1].id, "id2");
  EXPECT_TRUE(static_cast<bool>(userplaces[1].geoaddress.full_text));
  EXPECT_TRUE(static_cast<bool>(userplaces[1].geoaddress.short_text));
  EXPECT_FALSE(static_cast<bool>(userplaces[1].geoaddress.entrance));
  EXPECT_FALSE(static_cast<bool>(userplaces[1].geoaddress.uri));
  EXPECT_FALSE(static_cast<bool>(userplaces[1].geoaddress.type));
  EXPECT_FALSE(static_cast<bool>(userplaces[1].place_type));
  EXPECT_FALSE(static_cast<bool>(userplaces[1].comment));
}

TEST(TestMLLibApi, Orders) {
  auto contents = LoadJson("routehistory_get_response.json");
  auto routehistory_response = clients::routehistory::Parse(
      contents, formats::parse::To<RouteHistoryGetResponse>());
  const auto created = routehistory_response.results[0].created;
  auto orders = mllib::ToOrders(std::move(routehistory_response));

  EXPECT_EQ(orders.size(), 2);
  EXPECT_EQ(orders[0].id, "id1");
  EXPECT_EQ(orders[0].created, created);
  EXPECT_EQ(orders[0].source.full_text, "Израиль, Тель-Авив, А-Калир, 12");
  EXPECT_EQ(orders[0].source.entrance, "2");
  EXPECT_EQ(orders[0].source.uri, "ymapsbm1://org?oid=123");
  EXPECT_EQ(orders[0].source.type, "organization");
  EXPECT_EQ(orders[0].source.personal_phone_id, "123");
  EXPECT_DOUBLE_EQ(orders[0].source.geopoint.lon, 34.77);
  EXPECT_DOUBLE_EQ(orders[0].source.geopoint.lat, 32.07);
  EXPECT_EQ(orders[0].destinations.size(), 1);
  EXPECT_EQ(orders[0].destinations[0].full_text,
            "Израиль, Тель-Авив, А-Пардес, 5");
  EXPECT_TRUE(static_cast<bool>(orders[0].completion_point));
  EXPECT_TRUE(static_cast<bool>(orders[0].adjusted_source));
  EXPECT_EQ(orders[0].comment, "Нужна сдача с 10 рублей");
  EXPECT_TRUE(orders[0].tariff_class.has_value());
  EXPECT_EQ(orders[0].tariff_class.value(), "express");
  EXPECT_EQ(orders[1].id, "id2");
  EXPECT_TRUE(static_cast<bool>(orders[1].source.full_text));
  EXPECT_FALSE(static_cast<bool>(orders[1].source.entrance));
  EXPECT_FALSE(static_cast<bool>(orders[1].source.uri));
  EXPECT_FALSE(static_cast<bool>(orders[1].source.type));
  EXPECT_EQ(orders[1].destinations.size(), 0);
  EXPECT_FALSE(static_cast<bool>(orders[1].completion_point));
  EXPECT_FALSE(static_cast<bool>(orders[1].adjusted_source));
  EXPECT_FALSE(static_cast<bool>(orders[1].comment));
}

TEST(TestMLLibApi, SearchRoutes) {
  auto searchhistory_response = clients::routehistory::Parse(
      LoadJson("searchhistory_get_response.json"),
      formats::parse::To<RouteHistorySearchGetResponse>());
  EXPECT_EQ(searchhistory_response.results.size(), 2);

  auto search_history =
      mllib::ToSearchRoutes(std::move(searchhistory_response));

  EXPECT_EQ(search_history.size(), 1);
  EXPECT_EQ(search_history[0].source.has_value(), true);
  EXPECT_EQ(search_history[0].destination.has_value(), true);
  EXPECT_DOUBLE_EQ(search_history[0].source.value().geopoint.lon, 34.77);
  EXPECT_DOUBLE_EQ(search_history[0].source.value().geopoint.lat, 32.07);
  EXPECT_EQ(search_history[0].source.value().full_text,
            std::string("Москва, улица Катбустовая, 42, Организация по борьбе "
                        "с эвристиками"));
}

TEST(TestMLLibApi, EatsOrders) {
  auto response = clients::eats_ordershistory::Parse(
      LoadJson("eats_ordershistory_get_response.json"),
      formats::parse::To<GetOrdersResponse>());
  EXPECT_EQ(response.orders.size(), 2);
  EXPECT_EQ(response.orders[0].order_id, "1234568");
  EXPECT_EQ(response.orders[0].place_id, 42);
  EXPECT_EQ(response.orders[0].status, OrderStatus::kDelivered);
  EXPECT_EQ(response.orders[0].source, OrderSource::kLavka);
  EXPECT_DOUBLE_EQ(response.orders[0]
                       .delivery_location.GetUnderlying()
                       .GetLatitudeAsDouble(),
                   55.341034);
  EXPECT_DOUBLE_EQ(response.orders[0]
                       .delivery_location.GetUnderlying()
                       .GetLongitudeAsDouble(),
                   37.578302);
  EXPECT_EQ(response.orders[0].total_amount, "40 гривен");
  EXPECT_TRUE(response.orders[0].is_asap);
  EXPECT_EQ(
      response.orders[0].created_at,
      utils::datetime::GuessStringtime("2020-09-09T17:18:19.000000Z", "UTC"));
  EXPECT_EQ(
      response.orders[0].delivered_at,
      utils::datetime::GuessStringtime("2020-09-09T18:18:19.000000Z", "UTC"));
  EXPECT_EQ(response.orders[0].cancel_reason, "stonks");

  auto eats_orders = ToEatsOrders(std::move(response));
  EXPECT_EQ(eats_orders.size(), 2);
  EXPECT_EQ(eats_orders[0].order_id, "1234568");
  EXPECT_EQ(eats_orders[0].status, "delivered");
  EXPECT_EQ(eats_orders[0].source, "lavka");
  EXPECT_DOUBLE_EQ(eats_orders[0].delivery_location.lat, 55.341034);
  EXPECT_DOUBLE_EQ(eats_orders[0].delivery_location.lon, 37.578302);
  EXPECT_TRUE(eats_orders[0].is_asap);
  EXPECT_EQ(eats_orders[0].created, utils::datetime::GuessStringtime(
                                        "2020-09-09T17:18:19.000000Z", "UTC"));
  EXPECT_EQ(
      eats_orders[0].delivered,
      utils::datetime::GuessStringtime("2020-09-09T18:18:19.000000Z", "UTC"));
  EXPECT_EQ(eats_orders[0].cancel_reason, "stonks");
}

}  // namespace test::models::mllib
