#include "view.hpp"

#include <handlers/dependencies.hpp>

#include <userver/utils/datetime.hpp>

namespace handlers::launch_test_test_name::get {

void TestSendPositions1(Dependencies& dependencies) {
  using namespace geometry::literals;
  fts::client::IncomingSignal signal;
  signal.timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
      utils::datetime::Now().time_since_epoch());
  signal.source = "verified";
  signal.geodata = clients::fleet_tracking_system::Position{
      .lat = 37.0_lat,
      .lon = 55.0_lon,
      .speed = 16.6 * geometry::meters_per_second};
  dependencies.fts_client->SendPositions("test_uuid", {signal});
}

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  switch (request.test_name) {
    case decltype(request.test_name)::kSendPositions1:
      TestSendPositions1(dependencies);
      break;

    default:
      throw std::runtime_error("Unknwon test name");
  }
  return response;
}

}  // namespace handlers::launch_test_test_name::get
