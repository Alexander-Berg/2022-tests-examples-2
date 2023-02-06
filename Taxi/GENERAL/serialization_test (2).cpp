#include <gtest/gtest.h>
#include <types/serialization.hpp>
#include <types/types.hpp>

namespace drwm = driver_route_watcher::models;
namespace {
std::vector<drwm::DestinationPoint> MakePoints() {
  return {{
              drwm::Position(100 * geometry::lat, 200 * geometry::lon),
              std::chrono::seconds(42),
              std::chrono::seconds(142),
              drwm::PointId("pointid1"),
              drwm::OrderId("orderid1"),
          },
          {
              drwm::Position(10 * geometry::lat, 20 * geometry::lon),
              std::chrono::seconds(43),
              std::chrono::seconds(143),
              drwm::PointId("pointid2"),
              drwm::OrderId("orderid2"),
          }};
}
}  // namespace

TEST(destination_operation_serialize, base) {
  const auto now = utils::datetime::Now();
  const auto source_position =
      drwm::Position(13 * ::geometry::lat, 24 * ::geometry::lon);
  driver_route_watcher::models::DestinationOperation orig;
  orig.destination = driver_route_watcher::models::Destination{
      MakePoints(),
      drwm::ServiceId("service_id"),
      "some-meta-info",
      now,
      drwm::TransportType::kPedestrian,
      drwm::OrderId("mainorder"),
      true,
      3.1415,
      drwm::ZoneId("mordor"),
      drwm::Country("gondor"),
      source_position};
  orig.operation =
      driver_route_watcher::models::StartStopOperation::kStartByOrders;

  auto serialized =
      Serialize(orig, formats::serialize::To<formats::json::Value>());
  auto deserialized =
      Parse(serialized, formats::parse::To<drwm::DestinationOperation>());

  ASSERT_EQ(deserialized.destination, orig.destination);
}
