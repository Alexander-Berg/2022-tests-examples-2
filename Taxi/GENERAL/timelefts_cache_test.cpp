#include "timelefts_cache.hpp"

#include <geobus/channels/timelefts/timelefts_generator.hpp>
#include <types/types.hpp>

#include <userver/utest/utest.hpp>

namespace {
using Timelefts = geobus::types::Timelefts;
using TimeleftsMessage = geobus::types::TimeleftsMessage;

using TimeleftsCache = driver_route_responder::internal::TimeleftsCache;
using OrderId = driver_route_responder::models::OrderId;
using DriverId = driver_route_responder::models::DriverId;
using ParsingSettings = driver_route_responder::internal::ParsingSettings;
}  // namespace

UTEST(TimeleftsCache, ProcessPayloadTest) {
  TimeleftsCache cache(std::chrono::seconds(7200), 10, 10,
                       std::chrono::seconds(7200));
  geobus::generators::TimeleftsRandomGenerator timelefts_gen;
  geobus::generators::DriverIdGenerator contractor_id_gen;

  geobus::types::DriverId contractor1 = contractor_id_gen.CreateDriverId(1);
  geobus::types::DriverId contractor2 = contractor_id_gen.CreateDriverId(2);
  geobus::types::DriverId contractor3 = contractor_id_gen.CreateDriverId(3);
  geobus::types::DriverId unknown_contractor =
      contractor_id_gen.CreateDriverId(564132);
  DriverId drw_contractor1 =
      DriverId(contractor1.GetDbid(), contractor1.GetUuid());
  DriverId drw_contractor2 =
      DriverId(contractor2.GetDbid(), contractor2.GetUuid());
  DriverId drw_contractor3 =
      DriverId(contractor3.GetDbid(), contractor3.GetUuid());
  DriverId unknown_drw_contractor =
      DriverId(unknown_contractor.GetDbid(), unknown_contractor.GetUuid());
  OrderId order_id1 = OrderId("order_id1");
  OrderId order_id2 = OrderId("order_id2");
  OrderId order_id3 = OrderId("order_id3");
  OrderId order_id4 = OrderId("order_id4");
  OrderId order_id5 = OrderId("order_id5");
  OrderId order_id6 = OrderId("order_id6");
  OrderId order_id7 = OrderId("order_id7");
  OrderId unknown_order_id = OrderId("unknown_order_id");
  Timelefts timelefts1 = timelefts_gen.CreateElementForDriver(contractor1);
  timelefts1.timestamp = utils::datetime::Now();
  timelefts1.timeleft_data[0].order_id = order_id1.GetUnderlying();
  timelefts1.timeleft_data[1].order_id = order_id2.GetUnderlying();
  Timelefts timelefts2 = timelefts_gen.CreateElementForDriver(contractor2);
  timelefts2.timestamp = utils::datetime::Now();
  timelefts2.timeleft_data[0].order_id = order_id3.GetUnderlying();
  timelefts2.timeleft_data[1].order_id = order_id4.GetUnderlying();

  TimeleftsMessage message1;
  message1.data = {timelefts1, timelefts2};
  message1.timestamp = utils::datetime::Now();

  cache.ProcessPayload(std::move(message1));
  /// Check contractors map
  EXPECT_EQ(cache.ContractorsMapSize(), 2);
  ASSERT_TRUE(cache.GetTimelefts(drw_contractor1));
  EXPECT_EQ(*cache.GetTimelefts(drw_contractor1), timelefts1);
  ASSERT_TRUE(cache.GetTimelefts(drw_contractor2));
  EXPECT_EQ(*cache.GetTimelefts(drw_contractor2), timelefts2);
  EXPECT_FALSE(cache.GetTimelefts(unknown_drw_contractor));
  /// Check orders map
  EXPECT_EQ(cache.OrdersMapSize(), 4);
  ASSERT_TRUE(cache.GetTimelefts(order_id1));
  EXPECT_EQ(*cache.GetTimelefts(order_id1), timelefts1);
  ASSERT_TRUE(cache.GetTimelefts(order_id2));
  EXPECT_EQ(*cache.GetTimelefts(order_id2), timelefts1);
  ASSERT_TRUE(cache.GetTimelefts(order_id3));
  EXPECT_EQ(*cache.GetTimelefts(order_id3), timelefts2);
  ASSERT_TRUE(cache.GetTimelefts(order_id4));
  EXPECT_EQ(*cache.GetTimelefts(order_id4), timelefts2);
  EXPECT_FALSE(cache.GetTimelefts(unknown_order_id));

  std::weak_ptr<Timelefts> w_ptr_timelefts1(
      cache.GetTimelefts(drw_contractor1));

  Timelefts timelefts3 = timelefts_gen.CreateElementForDriver(contractor1);
  timelefts3.timestamp = utils::datetime::Now();
  timelefts3.timeleft_data[0].order_id = order_id1.GetUnderlying();
  timelefts3.timeleft_data[1].order_id = order_id5.GetUnderlying();
  Timelefts timelefts4 = timelefts_gen.CreateElementForDriver(contractor3);
  timelefts4.timestamp = utils::datetime::Now();
  timelefts4.timeleft_data[0].order_id = order_id6.GetUnderlying();
  timelefts4.timeleft_data[1].order_id = order_id7.GetUnderlying();

  TimeleftsMessage message2;
  message2.data = {timelefts3, timelefts4};
  message2.timestamp = utils::datetime::Now();
  cache.ProcessPayload(std::move(message2));
  /// Check contractors map
  EXPECT_EQ(cache.ContractorsMapSize(), 3);
  ASSERT_TRUE(cache.GetTimelefts(drw_contractor1));
  EXPECT_EQ(*cache.GetTimelefts(drw_contractor1), timelefts3);
  ASSERT_TRUE(cache.GetTimelefts(drw_contractor2));
  EXPECT_EQ(*cache.GetTimelefts(drw_contractor2), timelefts2);
  ASSERT_TRUE(cache.GetTimelefts(drw_contractor3));
  EXPECT_EQ(*cache.GetTimelefts(drw_contractor3), timelefts4);
  EXPECT_FALSE(cache.GetTimelefts(unknown_drw_contractor));
  EXPECT_TRUE(w_ptr_timelefts1.expired());
  /// Check orders map
  EXPECT_EQ(cache.OrdersMapSize(), 7);
  ASSERT_TRUE(cache.GetTimelefts(order_id1));
  EXPECT_EQ(*cache.GetTimelefts(order_id1), timelefts3);
  EXPECT_FALSE(cache.GetTimelefts(order_id2));
  ASSERT_TRUE(cache.GetTimelefts(order_id3));
  EXPECT_EQ(*cache.GetTimelefts(order_id3), timelefts2);
  ASSERT_TRUE(cache.GetTimelefts(order_id4));
  EXPECT_EQ(*cache.GetTimelefts(order_id4), timelefts2);
  ASSERT_TRUE(cache.GetTimelefts(order_id5));
  EXPECT_EQ(*cache.GetTimelefts(order_id5), timelefts3);
  ASSERT_TRUE(cache.GetTimelefts(order_id6));
  EXPECT_EQ(*cache.GetTimelefts(order_id6), timelefts4);
  ASSERT_TRUE(cache.GetTimelefts(order_id7));
  EXPECT_EQ(*cache.GetTimelefts(order_id7), timelefts4);
  EXPECT_FALSE(cache.GetTimelefts(unknown_order_id));

  cache.Clear();
  EXPECT_EQ(cache.ContractorsMapSize(), 0);
  EXPECT_EQ(cache.OrdersMapSize(), 0);
}

UTEST(TimeleftsCache, CleanCacheTest) {
  TimeleftsCache cache(std::chrono::seconds(7200), 10, 10,
                       std::chrono::seconds(1));
  geobus::generators::TimeleftsRandomGenerator timelefts_gen;
  geobus::generators::DriverIdGenerator contractor_id_gen;

  geobus::types::DriverId contractor1 = contractor_id_gen.CreateDriverId(1);
  geobus::types::DriverId contractor2 = contractor_id_gen.CreateDriverId(2);
  geobus::types::DriverId contractor3 = contractor_id_gen.CreateDriverId(3);
  geobus::types::DriverId unknown_contractor =
      contractor_id_gen.CreateDriverId(564132);
  DriverId drw_contractor1 =
      DriverId(contractor1.GetDbid(), contractor1.GetUuid());
  DriverId drw_contractor2 =
      DriverId(contractor2.GetDbid(), contractor2.GetUuid());
  DriverId drw_contractor3 =
      DriverId(contractor3.GetDbid(), contractor3.GetUuid());
  DriverId unknown_drw_contractor =
      DriverId(unknown_contractor.GetDbid(), unknown_contractor.GetUuid());
  OrderId order_id1 = OrderId("order_id1");
  OrderId order_id2 = OrderId("order_id2");
  OrderId order_id3 = OrderId("order_id3");
  OrderId order_id4 = OrderId("order_id4");
  OrderId order_id5 = OrderId("order_id5");
  OrderId order_id6 = OrderId("order_id6");
  OrderId order_id7 = OrderId("order_id7");
  OrderId order_id8 = OrderId("order_id8");
  OrderId unknown_order_id = OrderId("unknown_order_id");
  Timelefts timelefts1 = timelefts_gen.CreateElementForDriver(contractor1);
  timelefts1.timestamp = utils::datetime::Now() - std::chrono::seconds(1);
  timelefts1.timeleft_data[0].order_id = order_id1.GetUnderlying();
  timelefts1.timeleft_data[1].order_id = order_id2.GetUnderlying();
  Timelefts timelefts2 = timelefts_gen.CreateElementForDriver(contractor2);
  timelefts2.timestamp = utils::datetime::Now() - std::chrono::seconds(1);
  timelefts2.timeleft_data[0].order_id = order_id3.GetUnderlying();
  timelefts2.timeleft_data[1].order_id = order_id4.GetUnderlying();

  TimeleftsMessage message1;
  message1.data = {timelefts1, timelefts2};
  message1.timestamp = utils::datetime::Now() - std::chrono::seconds(1);

  cache.ProcessPayload(std::move(message1));
  /// Check contractors map
  EXPECT_EQ(cache.ContractorsMapSize(), 2);
  ASSERT_TRUE(cache.GetTimelefts(drw_contractor1));
  EXPECT_EQ(*cache.GetTimelefts(drw_contractor1), timelefts1);
  ASSERT_TRUE(cache.GetTimelefts(drw_contractor2));
  EXPECT_EQ(*cache.GetTimelefts(drw_contractor2), timelefts2);
  EXPECT_EQ(cache.GetTimelefts(unknown_drw_contractor), nullptr);
  /// Check orders map
  EXPECT_EQ(cache.OrdersMapSize(), 4);
  ASSERT_TRUE(cache.GetTimelefts(order_id1));
  EXPECT_EQ(*cache.GetTimelefts(order_id1), timelefts1);
  ASSERT_TRUE(cache.GetTimelefts(order_id2));
  EXPECT_EQ(*cache.GetTimelefts(order_id2), timelefts1);
  ASSERT_TRUE(cache.GetTimelefts(order_id3));
  EXPECT_EQ(*cache.GetTimelefts(order_id3), timelefts2);
  ASSERT_TRUE(cache.GetTimelefts(order_id4));
  EXPECT_EQ(*cache.GetTimelefts(order_id4), timelefts2);
  EXPECT_FALSE(cache.GetTimelefts(unknown_order_id));

  std::weak_ptr<Timelefts> w_ptr_timelefts1(
      cache.GetTimelefts(drw_contractor1));
  std::weak_ptr<Timelefts> w_ptr_timelefts2(
      cache.GetTimelefts(drw_contractor2));
  EXPECT_FALSE(w_ptr_timelefts1.expired());
  EXPECT_FALSE(w_ptr_timelefts2.expired());

  cache.CleanCache();
  EXPECT_TRUE(w_ptr_timelefts1.expired());
  EXPECT_TRUE(w_ptr_timelefts2.expired());

  Timelefts timelefts3 = timelefts_gen.CreateElementForDriver(contractor1);
  timelefts3.timestamp = utils::datetime::Now();
  timelefts3.timeleft_data[0].order_id = order_id5.GetUnderlying();
  timelefts3.timeleft_data[1].order_id = order_id6.GetUnderlying();
  Timelefts timelefts4 = timelefts_gen.CreateElementForDriver(contractor3);
  timelefts4.timestamp = utils::datetime::Now();
  timelefts4.timeleft_data[0].order_id = order_id7.GetUnderlying();
  timelefts4.timeleft_data[1].order_id = order_id8.GetUnderlying();

  TimeleftsMessage message2;
  message2.data = {timelefts3, timelefts4};
  message2.timestamp = utils::datetime::Now();

  cache.ProcessPayload(std::move(message2));
  /// Check contractors map
  EXPECT_EQ(cache.ContractorsMapSize(), 3);
  ASSERT_TRUE(cache.GetTimelefts(drw_contractor1));
  EXPECT_EQ(*cache.GetTimelefts(drw_contractor1), timelefts3);
  EXPECT_EQ(cache.GetTimelefts(drw_contractor2), nullptr);
  ASSERT_TRUE(cache.GetTimelefts(drw_contractor3));
  EXPECT_EQ(*cache.GetTimelefts(drw_contractor3), timelefts4);
  EXPECT_EQ(cache.GetTimelefts(unknown_drw_contractor), nullptr);
  /// Check orders map
  EXPECT_EQ(cache.OrdersMapSize(), 8);
  EXPECT_FALSE(cache.GetTimelefts(order_id1));
  EXPECT_FALSE(cache.GetTimelefts(order_id2));
  EXPECT_FALSE(cache.GetTimelefts(order_id3));
  EXPECT_FALSE(cache.GetTimelefts(order_id4));
  ASSERT_TRUE(cache.GetTimelefts(order_id5));
  EXPECT_EQ(*cache.GetTimelefts(order_id5), timelefts3);
  ASSERT_TRUE(cache.GetTimelefts(order_id6));
  EXPECT_EQ(*cache.GetTimelefts(order_id6), timelefts3);
  ASSERT_TRUE(cache.GetTimelefts(order_id7));
  EXPECT_EQ(*cache.GetTimelefts(order_id7), timelefts4);
  ASSERT_TRUE(cache.GetTimelefts(order_id8));
  EXPECT_EQ(*cache.GetTimelefts(order_id8), timelefts4);
  EXPECT_FALSE(cache.GetTimelefts(unknown_order_id));

  cache.CleanCache();
  /// Check erasing keys from orders map
  EXPECT_EQ(cache.OrdersMapSize(), 4);
  ASSERT_TRUE(cache.GetTimelefts(order_id5));
  EXPECT_EQ(*cache.GetTimelefts(order_id5), timelefts3);
  ASSERT_TRUE(cache.GetTimelefts(order_id6));
  EXPECT_EQ(*cache.GetTimelefts(order_id6), timelefts3);
  ASSERT_TRUE(cache.GetTimelefts(order_id7));
  EXPECT_EQ(*cache.GetTimelefts(order_id7), timelefts4);
  ASSERT_TRUE(cache.GetTimelefts(order_id8));
  EXPECT_EQ(*cache.GetTimelefts(order_id8), timelefts4);

  cache.Clear();
  EXPECT_EQ(cache.ContractorsMapSize(), 0);
  EXPECT_EQ(cache.OrdersMapSize(), 0);
}

TEST(DriverInsideTestBorders, CorrectBorders) {
  ::geometry::Position driver_pos(::geometry::Latitude(35.32),
                                  ::geometry::Longitude(-23.8));
  ParsingSettings settings{true, 1, 1, {}, {}, {}, {}};
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));

  // is 35.32 included in ranage (34, 36)
  settings.lat_less = ::geometry::Latitude(34);
  settings.lat_more = ::geometry::Latitude(36);
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));

  // is 35.32 included in ranage (-23, 16.2)
  settings.lat_less = ::geometry::Latitude(-23);
  settings.lat_more = ::geometry::Latitude(16.2);
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  // is 35.32 included in ranage (-180, -46) || (2, 180)
  settings.lat_less = ::geometry::Latitude(2);
  settings.lat_more = ::geometry::Latitude(-46);
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));

  // is -82 included in ranage (-180, -46) || (2, 180)
  driver_pos.latitude = ::geometry::Latitude(-82);
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));

  // is 35.32 included in ranage (-180, 34) || (36, 180)
  driver_pos.latitude = ::geometry::Latitude(35.32);
  settings.lat_less = ::geometry::Latitude(36);
  settings.lat_more = ::geometry::Latitude(34);
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  // is -15 included in ranage (-180, -46) || (3, 180)
  driver_pos.latitude = ::geometry::Latitude(-15);
  settings.lat_less = ::geometry::Latitude(3);
  settings.lat_more = ::geometry::Latitude(-46);
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  driver_pos.latitude = ::geometry::Latitude(35.32);
  settings.lat_less = {};
  settings.lat_more = {};

  // is -23.8 included in ranage (34, 36)
  settings.lon_less = ::geometry::Longitude(34);
  settings.lon_more = ::geometry::Longitude(36);
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  // is -23.8 included in ranage (-24, 16.2)
  settings.lon_less = ::geometry::Longitude(-24);
  settings.lon_more = ::geometry::Longitude(16.2);
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));

  // is -23.8 included in ranage (-180, -46) || (2, 180)
  settings.lon_less = ::geometry::Longitude(2);
  settings.lon_more = ::geometry::Longitude(-46);
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  // is -23.8 included in ranage (-180, -23) || (36, 180)
  settings.lon_less = ::geometry::Longitude(36);
  settings.lon_more = ::geometry::Longitude(-23);
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));

  // is -23.8 included in ranage (-180, -24) || (36, 180)
  settings.lon_less = ::geometry::Longitude(36);
  settings.lon_more = ::geometry::Longitude(-24);
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  // is -23.8 included in ranage (-180, -80) || (-24, 180)
  settings.lon_less = ::geometry::Longitude(-24);
  settings.lon_more = ::geometry::Longitude(-80);
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));

  // is -23.8(lon) included in ranage (-180, -80) || (-24, 180) && is 35.32(lat)
  // included in ranage (34, 36)
  settings.lat_less = ::geometry::Latitude(34);
  settings.lat_more = ::geometry::Latitude(36);
  settings.lon_less = ::geometry::Longitude(-24);
  settings.lon_more = ::geometry::Longitude(-80);
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));

  // is -23.8(lon) included in ranage (-180, -80) || (-24, 180) && is 35.32(lat)
  // included in ranage (-180, 34) || (36, 180)
  settings.lat_less = ::geometry::Latitude(36);
  settings.lat_more = ::geometry::Latitude(34);
  settings.lon_less = ::geometry::Longitude(-24);
  settings.lon_more = ::geometry::Longitude(-80);
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  // is -23.8(lon) included in ranage (-180, -80) || (-24, 180) && is 35.32(lat)
  // included in ranage (-180, 2) || (12, 180)
  settings.lat_less = ::geometry::Latitude(12);
  settings.lat_more = ::geometry::Latitude(2);
  settings.lon_less = ::geometry::Longitude(-24);
  settings.lon_more = ::geometry::Longitude(-80);
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));

  // is -23.8(lon) included in ranage (-24, -22) && is 35.32(lat) included in
  // ranage (-180, 180)
  settings.lat_less = ::geometry::Latitude(-180);
  settings.lat_more = ::geometry::Latitude(180);
  settings.lon_less = ::geometry::Longitude(-24);
  settings.lon_more = ::geometry::Longitude(-22);
  EXPECT_TRUE(DriverInsideTestBorders(settings, driver_pos));
}

TEST(DriverInsideTestBorders, IncorrectBorders) {
  ::geometry::Position driver_pos(::geometry::Latitude(35.32),
                                  ::geometry::Longitude(-23.8));
  ParsingSettings settings{
      true, 1, 1, ::geometry::Longitude(35.2), ::geometry::Latitude(2), {}, {}};
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  settings.lat_less = {};
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  settings.lat_less = ::geometry::Latitude(2.3);
  settings.lon_less = {};
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));

  settings.lat_less = {};
  settings.lat_more = ::geometry::Latitude(2.3);
  EXPECT_FALSE(DriverInsideTestBorders(settings, driver_pos));
}
