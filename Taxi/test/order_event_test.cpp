#include <gtest/gtest.h>
#include <cmath>
#include <vector>

#include <userver/formats/json/value.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/formats/serialize/common_containers.hpp>

#include <eventus/pipeline/event.hpp>

namespace models::order_event {

using DestinationPoints = std::vector<std::vector<double>>;

struct OrderEventHelper {
  std::string db_id;
  DestinationPoints destinations_geopoint;
  std::string driver_uuid;
  std::string event_key;
  std::string nz;
  std::string order_id;
  double status_updated;
  std::string user_id;
  std::string user_locale;
  std::string user_phone_id;
};

// Helper to convert to cpp-like
eventus::pipeline::Event Into(const OrderEventHelper& oeh) {
  formats::json::ValueBuilder b;
  b["db_id"] = oeh.db_id;
  b["destinations_geopoint"] = oeh.destinations_geopoint;
  b["driver_uuid"] = oeh.driver_uuid;
  b["event_key"] = oeh.event_key;
  b["nz"] = oeh.nz;
  b["order_id"] = oeh.order_id;
  b["status_updated"] = oeh.status_updated;
  b["user_id"] = oeh.user_id;
  b["user_locale"] = oeh.user_locale;
  b["user_phone_id"] = oeh.user_phone_id;
  return eventus::pipeline::Event(b.ExtractValue());
}

template <typename T>
std::ostream& operator<<(std::ostream& os, const std::vector<T>& vec) {
  os << "{";
  size_t end = vec.size();
  for (auto& v : vec) {
    os << v;
    if (--end) os << ", ";
  }
  os << "}";
  return os;
}

std::ostream& operator<<(std::ostream& os, const eventus::pipeline::Event& oe) {
  os << "OrderEvent{"                                              //
     << "db_id=\"" << oe.GetOr<std::string>("db_id", "") << "\","  //
     << "destinations_geopoint="
     << oe.Get<DestinationPoints>("destinations_geopoint") << ","  //
     << "driver_uuid=\"" << oe.GetOr<std::string>("driver_uuid", "")
     << "\","                                                               //
     << "event_key=\"" << oe.Get<std::string>("event_key") << "\","         //
     << "nz=\"" << oe.Get<std::string>("nz") << "\","                       //
     << "order_id=\"" << oe.Get<std::string>("order_id") << "\","           //
     << "status_updated=" << oe.Get<double>("status_updated") << ","        //
     << "user_id=\"" << oe.Get<std::string>("user_id") << "\""              //
     << "user_phone_id=\"" << oe.Get<std::string>("user_phone_id") << "\""  //
     << "}";
  return os;
}

bool operator==(const eventus::pipeline::Event& lhs,
                const eventus::pipeline::Event& rhs) {
  // auto lstatus_updated = lhs.Get<double>("status_updated");
  // auto rstatus_updated = rhs.Get<double>("status_updated");
  return (
      lhs.Get<std::string>("event_key") ==
          rhs.Get<std::string>("event_key") &&  //
      std::fabs(lhs.Get<double>("status_updated") -
                rhs.Get<double>("status_updated")) < 0.01 &&  //
      lhs.Get<std::string>("order_id") ==
          rhs.Get<std::string>("order_id") &&                                //
      lhs.Get<std::string>("user_id") == rhs.Get<std::string>("user_id") &&  //
      lhs.Get<std::string>("user_phone_id") ==
          rhs.Get<std::string>("user_phone_id") &&  //
      lhs.GetOr<std::string>("db_id", "") ==
          rhs.GetOr<std::string>("db_id", "") &&  //
      lhs.GetOr<std::string>("driver_uuid", "") ==
          rhs.GetOr<std::string>("driver_uuid", "") &&  //
      lhs.Get<DestinationPoints>("destinations_geopoint") ==
          rhs.Get<DestinationPoints>("destinations_geopoint") &&  //
      lhs.Get<std::string>("nz") == rhs.Get<std::string>("nz")    //
  );
}

// TODO @arkcoon: add similar unittests for ParserType::kJson

}  // namespace models::order_event
