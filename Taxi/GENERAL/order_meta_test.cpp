#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <models/driverid.hpp>
#include <order-access/models/taxi_status_serialization.hpp>
#include <userver/formats/bson.hpp>
#include <userver/formats/serialize/common_containers.hpp>

#include <common/pack/bson/busy_drivers_order_event.hpp>
#include "order_meta.hpp"

namespace {

const std::string kEvent = "event";
const std::string kOrderMeta = "order_meta";
const std::string kOrderId = "order_id";
const std::string kDbid = "dbid";
const std::string kUuid = "uuid";
const std::string kPerformer = "performer";
const std::string kDestinations = "destinations";
const std::string kDestinationsStatuses = "destinations_statuses";
const std::string kUpdated = "updated";
const std::string kEventIndex = "event_index";
const std::string kMysteryShopper = "mystery_shopper";
const std::string kTaxiStatus = "taxi_status";
const std::string kTariffClass = "tariff_class";
const std::string kTariffZone = "tariff_zone";
const std::string kSpecialRequirements = "special_requirements";
const std::string kCargoRefId = "cargo_ref_id";
const std::string kTransportType = "transport_type";

using OrderMeta = busy_drivers::models::OrderMeta;
using BusyDriverFlag = busy_drivers::models::BusyDriverFlag;

const geometry::Position kPointOne{12.34 * geometry::lat,
                                   56.78 * geometry::lon};
const geometry::Position kPointTwo{87.65 * geometry::lat,
                                   43.21 * geometry::lon};

MATCHER_P(IsClosePosition, position, "") {
  return geometry::AreClosePositions(arg, position);
}

auto IsEqualOrderMeta(const OrderMeta& expected) {
  std::vector<testing::Matcher<geometry::Position>> destinations_matchers;
  std::transform(
      expected.destinations.begin(), expected.destinations.end(),
      std::back_inserter(destinations_matchers),
      [](const auto& destination) { return IsClosePosition(destination); });

  return testing::AllOf(
      testing::Field(&OrderMeta::order_event, expected.order_event),
      testing::Field(&OrderMeta::order_id, expected.order_id),
      testing::Field(&OrderMeta::driver_id, expected.driver_id),
      testing::Field(&OrderMeta::destinations,
                     testing::ElementsAreArray(destinations_matchers)),
      testing::Field(&OrderMeta::destinations_statuses,
                     expected.destinations_statuses),
      testing::Field(&OrderMeta::event_index, expected.event_index),
      testing::Field(&OrderMeta::taxi_status, expected.taxi_status),
      testing::Field(&OrderMeta::flags, expected.flags),
      testing::Field(&OrderMeta::tariff_class, expected.tariff_class),
      testing::Field(&OrderMeta::tariff_zone, expected.tariff_zone));
}

void Parse(const busy_drivers::models::OrderMeta& expected) {
  formats::bson::ValueBuilder builder;

  builder[kEvent] = expected.order_event;

  builder[kOrderMeta][kOrderId] = expected.order_id;
  builder[kOrderMeta][kPerformer] = formats::bson::MakeDoc();

  if (expected.transport_type) {
    builder[kOrderMeta][kPerformer][kTransportType] = *expected.transport_type;
  }

  auto driver_id = models::DriverId::FromDbidUuid(expected.driver_id);
  builder[kOrderMeta][kPerformer][kDbid] = driver_id.dbid;
  builder[kOrderMeta][kPerformer][kUuid] = driver_id.uuid;

  builder[kOrderMeta][kPerformer][kTariffClass] = expected.tariff_class;
  builder[kOrderMeta][kTariffZone] = expected.tariff_zone;

  builder[kOrderMeta][kDestinations] = formats::bson::MakeArray();
  for (const auto& destination : expected.destinations) {
    builder[kOrderMeta][kDestinations].PushBack(std::vector{
        destination.longitude.value(), destination.latitude.value()});
  }

  builder[kOrderMeta][kDestinationsStatuses] = formats::bson::MakeArray();
  for (bool status : expected.destinations_statuses) {
    builder[kOrderMeta][kDestinationsStatuses].PushBack(status);
  }

  builder[kOrderMeta][kTaxiStatus] = expected.taxi_status;
  builder[kOrderMeta][kUpdated] = expected.updated;
  builder[kOrderMeta][kEventIndex] = expected.event_index;
  builder[kOrderMeta][kMysteryShopper] =
      expected.flags[BusyDriverFlag::kMysteryShopper];

  builder[kOrderMeta][kSpecialRequirements] = expected.special_requirements;

  if (expected.cargo_ref_id) {
    builder[kOrderMeta][kCargoRefId] = *expected.cargo_ref_id;
  }

  auto parsed = busy_drivers::models::Parse(builder.ExtractValue(),
                                            formats::parse::To<OrderMeta>{});

  EXPECT_THAT(parsed, IsEqualOrderMeta(expected));

  std::vector<std::pair<formats::bson::ValueBuilder, std::string>>
      mandatory_fields{{builder, kEvent},
                       {builder[kOrderMeta], kOrderId},
                       {builder[kOrderMeta], kPerformer},
                       {builder[kOrderMeta][kPerformer], kDbid},
                       {builder[kOrderMeta][kPerformer], kUuid},
                       {builder[kOrderMeta][kPerformer], kTariffClass},
                       {builder[kOrderMeta], kTariffZone},
                       {builder[kOrderMeta], kTaxiStatus},
                       {builder[kOrderMeta], kUpdated},
                       {builder[kOrderMeta], kEventIndex},
                       {builder[kOrderMeta], kSpecialRequirements}};

  for (auto& [b, field] : mandatory_fields) {
    auto prev = b[field];
    b.Remove(field);
    EXPECT_THROW(busy_drivers::models::Parse(builder.ExtractValue(),
                                             formats::parse::To<OrderMeta>{}),
                 formats::bson::MemberMissingException);
    b[field] = prev;
  }
}

using OrderEvent = ::busy_drivers::models::BusyDriversOrderEvent;

}  // namespace

TEST(OrderMeta, Parse) {
  Parse({OrderEvent::kAssign,
         "order_id",
         "dbid_uuid",
         "econom",
         "moscow",
         {kPointOne, kPointTwo},
         {false, true},
         order_access::models::TaxiStatus::Driving,
         std::chrono::system_clock::now(),
         0,
         {BusyDriverFlag::kMysteryShopper},
         {},
         "cargo_ref_id",
         "transport_type"});

  Parse({OrderEvent::kChange,
         "order_id",
         "dbid_uuid",
         "business",
         "moscow",
         {kPointOne},
         {false},
         order_access::models::TaxiStatus::Transporting,
         std::chrono::system_clock::now(),
         1,
         {BusyDriverFlag::kMysteryShopper},
         {"thermobag_delivery"},
         {},
         {}});

  Parse({OrderEvent::kFinish,
         "order_id",
         "dbid_uuid",
         "cargo",
         "moscow",
         {},
         {},
         order_access::models::TaxiStatus::Waiting,
         std::chrono::system_clock::now(),
         2,
         {},
         {"thermobag_delivery"},
         "cargo_ref_id",
         "transport_type"});
}
