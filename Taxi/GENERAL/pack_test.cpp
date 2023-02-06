#include <gtest/gtest.h>

#include <utils/helpers/params.hpp>

#include "driver/pack/fbs/airport.hpp"
#include "driver/pack/fbs/busy_info.hpp"
#include "driver/pack/fbs/car.hpp"
#include "driver/pack/fbs/indexed_driver.hpp"
#include "driver/pack/fbs/pool.hpp"
#include "driver/pack/fbs/profile.hpp"
#include "driver/pack/fbs/reposition.hpp"
#include "driver/pack/fbs/requirements.hpp"
#include "driver/pack/fbs/routed_driver.hpp"
#include "driver/pack/fbs/status.hpp"
#include "driver/pack/fbs/workshift.hpp"
#include "driver/pack/json/airport.hpp"
#include "driver/pack/json/busy_info.hpp"
#include "driver/pack/json/car.hpp"
#include "driver/pack/json/indexed_driver.hpp"
#include "driver/pack/json/pool.hpp"
#include "driver/pack/json/profile.hpp"
#include "driver/pack/json/reposition.hpp"
#include "driver/pack/json/requirements.hpp"
#include "driver/pack/json/routed_driver.hpp"
#include "driver/pack/json/status.hpp"
#include "driver/pack/json/workshift.hpp"

namespace {

template <typename T>
bool IsEq(const std::shared_ptr<T>& l, const std::shared_ptr<T>& r);

template <typename T>
bool IsEq(const boost::optional<T>& l, const boost::optional<T>& r);

bool IsEq(const std::string& l, const std::string& r) { return l == r; }

bool IsEq(const models::driver::ProfileCar& c1,
          const models::driver::ProfileCar& c2) {
  return c1.number == c2.number && c1.model == c2.model &&
         c1.mark_code == c2.mark_code && c1.age == c2.age &&
         c1.color == c2.color && c1.color_code == c2.color_code &&
         c1.capacity == c2.capacity &&
         c1.capacity_luggage == c2.capacity_luggage && c1.years == c2.years &&
         c1.price == c2.price;
}

bool IsEq(const models::driver::Car& c1, const models::driver::Car& c2) {
  return c1.number == c2.number and c1.blacklisted == c2.blacklisted and
         c1.blacklisted_till == c2.blacklisted_till and
         c1.manually_assigned_classes == c2.manually_assigned_classes;
}

bool IsEq(const models::driver::Workshift& w1,
          const models::driver::Workshift& w2) {
  return w1.driver_id == w2.driver_id && w1.created == w2.created &&
         w1.date_finish == w2.date_finish && w1.home_zone == w2.home_zone &&
         w1.zones == w2.zones;
}

bool IsEq(const models::driver::Workshifts& w1,
          const models::driver::Workshifts& w2) {
  if (w1.size() != w2.size()) return false;
  for (const auto& kv1 : w1) {
    const auto it2 = w2.find(kv1.first);
    if (it2 == w2.cend()) return false;
    if (!IsEq(kv1.second, it2->second)) return false;
  }
  return true;
}

bool IsEq(const models::Requirements& r1, const models::Requirements& r2) {
  return r1.GetBoolRequirements() == r2.GetBoolRequirements() &&
         r1.GetIntRequirements() == r2.GetIntRequirements();
}

bool IsEq(const models::DriverRequirements& r1,
          const models::DriverRequirements& r2) {
  return IsEq(static_cast<const models::Requirements&>(r1),
              static_cast<const models::Requirements&>(r2)) &&
         r1.GetChildChairRequirement().chairs ==
             r2.GetChildChairRequirement().chairs;
}

bool IsEq(const models::driver_metrics::State& p1,
          const models::driver_metrics::State& p2) {
  return p1.blocked == p2.blocked &&
         IsEq(p1.blocking_reason, p2.blocking_reason) &&
         IsEq(p1.blocked_until, p2.blocked_until);
}

bool IsEq(const utils::TimePoint& p1, const utils::TimePoint& p2) {
  return p1 == p2;
}

bool IsEq(const models::driver::Profile& p1,
          const models::driver::Profile& p2) {
  return p1.is_active == p2.is_active &&
         p1.driver_id.uuid == p2.driver_id.uuid &&
         p1.driver_id.clid == p2.driver_id.clid && p1.license == p2.license &&
         p1.driver_id.dbid == p2.driver_id.dbid && p1.locale == p2.locale &&
         p1.city == p2.city && p1.taximeter_version == p2.taximeter_version &&
         p1.mqc_passed == p2.mqc_passed && IsEq(p1.car, p2.car) &&
         IsEq(p1.requirements, p2.requirements) &&
         p1.allowed_classes == p2.allowed_classes &&
         p1.allowed_classes_orig == p2.allowed_classes_orig &&
         p1.mqc_status == p2.mqc_status &&
         p1.supported_payment_methods == p2.supported_payment_methods &&
         p1.allowed_payment_methods == p2.allowed_payment_methods &&
         p1.grades.by_class.GetEnabledClasses() ==
             p2.grades.by_class.GetEnabledClasses() &&
         p1.grades.by_class.GetDisabledClasses() ==
             p2.grades.by_class.GetDisabledClasses() &&
         p1.grades.by_class_air.GetEnabledClasses() ==
             p2.grades.by_class_air.GetEnabledClasses() &&
         p1.grades.by_class_air.GetDisabledClasses() ==
             p2.grades.by_class_air.GetDisabledClasses() &&
         p1.park_deactivated == p2.park_deactivated &&
         IsEq(p1.workshifts, p2.workshifts);
}

bool IsEq(const models::driver::Score& s1, const models::driver::Score& s2) {
  return s1.base == s2.base && s1.total == s2.total;
}

bool IsEq(const models::driver::UniqueDriver& d1,
          const models::driver::UniqueDriver& d2) {
  return d1.id == d2.id && d1.courses == d2.courses &&
         d1.licenses == d2.licenses && d1.blacklisted == d2.blacklisted &&
         d1.blacklisted_till == d2.blacklisted_till &&
         d1.exam_score == d2.exam_score &&
         d1.acknowledged_time == d2.acknowledged_time &&
         d1.registration_time == d2.registration_time &&
         d1.first_order_complete_time == d2.first_order_complete_time &&
         d1.mystery_shopper_passed == d2.mystery_shopper_passed &&
         d1.courses == d2.courses &&
         IsEq(d1.driver_metrics_state, d2.driver_metrics_state);
}

bool IsEq(const models::driver::meta::Status& s1,
          const models::driver::meta::Status& s2) {
  return s1.timestamp == s2.timestamp && s1.status == s2.status &&
         s1.robot_status == s2.robot_status && s1.tx_status == s2.tx_status &&
         s1.order_provider == s2.order_provider &&
         s1.switched_on_classes == s2.switched_on_classes &&
         s1.disabled_Yandex == s2.disabled_Yandex &&
         s1.online_seconds == s2.online_seconds &&
         s1.dont_chain == s2.dont_chain && s1.only_card == s2.only_card;
}

bool IsEq(const models::driver::BusyInfo& l,
          const models::driver::BusyInfo& r) {
  return l.order_id == r.order_id && l.destination == r.destination &&
         l.approximate == r.approximate && l.left_time == r.left_time &&
         l.left_dist == r.left_dist && l.flags == r.flags;
}

bool IsEq(const models::driver::pool::Order& l,
          const models::driver::pool::Order& r) {
  return l.order_id == r.order_id && l.source == r.source &&
         l.destination == r.destination &&
         l.passengers_count == r.passengers_count &&
         l.luggage_count == r.luggage_count &&
         l.transporting == r.transporting && l.start_time == r.start_time;
}

bool IsEq(const models::driver::pool::Info& l,
          const models::driver::pool::Info& r) {
  if (l.umbrella_order_id != r.umbrella_order_id) return false;
  if (l.orders.size() != r.orders.size()) return false;
  for (size_t i = 0; i != l.orders.size(); ++i) {
    if (!IsEq(l.orders[i], r.orders[i])) return false;
  }
  return true;
}

bool IsEq(const models::driver::airport::QueuePosition::ClassInfo& l,
          const models::driver::airport::QueuePosition::ClassInfo& r) {
  return l.time_virtual_enabled == r.time_virtual_enabled &&
         l.virtual_positions_before == r.virtual_positions_before &&
         l.drivers_before == r.drivers_before;
}
bool IsEq(const models::driver::airport::QueuePosition& l,
          const models::driver::airport::QueuePosition& r) {
  if (l.classes_info.size() != r.classes_info.size()) return false;
  for (const auto& kv : l.classes_info) {
    if (!r.classes_info.count(kv.first)) return false;
    if (!IsEq(kv.second, r.classes_info.at(kv.first))) return false;
  }

  return l.id == r.id && l.driver_id == r.driver_id && l.zone_id == r.zone_id &&
         l.real_parking_id == r.real_parking_id &&
         l.recommended_parking_id == r.recommended_parking_id &&
         l.profile_db_id == r.profile_db_id && l.created == r.created &&
         l.updated == r.updated && l.count_rejects == r.count_rejects &&
         l.time_activated == r.time_activated &&
         l.time_deactivated == r.time_deactivated &&
         l.time_exited == r.time_exited && l.time_online == r.time_online &&
         l.time_busy == r.time_busy && l.time_busy_reset == r.time_busy_reset &&
         l.busy_penalty == r.busy_penalty &&
         l.status_reason == r.status_reason &&
         l.active_classes_times == r.active_classes_times &&
         l.active_classes == r.active_classes &&
         l.available_classes == r.available_classes &&
         l.is_available_classes_only == r.is_available_classes_only &&
         l.virtual_updated == r.virtual_updated &&
         l.frauder_list == r.frauder_list &&
         l.frauder_unbanned == r.frauder_unbanned;
}

bool IsEq(const utils::geometry::TrackPoint& l,
          const utils::geometry::TrackPoint& r) {
  return static_cast<const utils::geometry::Point&>(l) ==
             static_cast<const utils::geometry::Point&>(r) &&
         l.direction == r.direction && l.speed == r.speed &&
         l.timestamp == r.timestamp && l.source == r.source &&
         l.accuracy == r.accuracy;
}

bool IsEq(const models::reposition::IndexEntry& l,
          const models::reposition::IndexEntry& r) {
  return l.exclude == r.exclude && l.override_busy == r.override_busy &&
         l.reposition_check_required == r.reposition_check_required;
}

bool IsEq(const models::driver::IndexedDriver& l,
          const models::driver::IndexedDriver& r) {
  return l.driver_id() == r.driver_id() && IsEq(l.profile(), r.profile()) &&
         IsEq(l.unique_driver(), r.unique_driver()) &&
         IsEq(l.score(), r.score()) && IsEq(l.car(), r.car()) &&
         l.finaly_classes() == r.finaly_classes() &&
         IsEq(l.status(), r.status()) && IsEq(l.point(), r.point()) &&
         IsEq(l.busy_info(), r.busy_info()) &&
         IsEq(l.pool_info(), r.pool_info()) &&
         l.desired_payment_type() == r.desired_payment_type() &&
         IsEq(l.airport_queue_position(), r.airport_queue_position()) &&
         l.experiments() == r.experiments() &&
         IsEq(l.reposition_index(), r.reposition_index()) &&
         l.IsVerybusy() == r.IsVerybusy();
}

bool IsEq(const clients::routing::RouteInfo& l,
          const clients::routing::RouteInfo& r) {
  return l.total_time == r.total_time && l.total_distance == r.total_distance;
}

bool IsEq(const models::driver::RoutedDriversBulk& l,
          const models::driver::RoutedDriversBulk& r) {
  const auto& l_bulk = l.routed_drivers_bulk;
  const auto& r_bulk = r.routed_drivers_bulk;
  if (l_bulk.size() != r_bulk.size()) return false;
  for (size_t i = 0; i < l_bulk.size(); ++i) {
    if (l_bulk[i].size() != r_bulk[i].size()) return false;
    for (size_t j = 0; j < l_bulk[i].size(); ++j) {
      if (!IsEq(l_bulk[i][j].driver, r_bulk[i][j].driver)) return false;
      if (l_bulk[i][j].allowed_order_classes_for_driver !=
          r_bulk[i][j].allowed_order_classes_for_driver)
        return false;
      if (!IsEq(l_bulk[i][j].route_info, r_bulk[i][j].route_info)) return false;
    }
  }
  return true;
}

template <typename T>
bool IsEq(const std::shared_ptr<T>& l, const std::shared_ptr<T>& r) {
  return l ? (r && IsEq(*l, *r)) : !r;
}

template <typename T>
bool IsEq(const boost::optional<T>& l, const boost::optional<T>& r) {
  return l ? (r && IsEq(*l, *r)) : !r;
}

models::driver::Car CreateCar() {
  const std::unordered_map<std::string, models::Classes> classes_orig = {
      {"*", models::Classes{"business", "econom"}},
      {"#", models::Classes{"UberX", "econom", "business"}}};

  models::driver::Car car;
  car.number = "1234";
  car.blacklisted = true;
  car.blacklisted_till = std::chrono::time_point_cast<std::chrono::seconds>(
      std::chrono::system_clock::now());
  car.manually_assigned_classes = classes_orig;
  return car;
}

models::reposition::IndexEntry CreateRepositionIndexEntry() {
  return models::reposition::IndexEntry();
}

models::driver::meta::Status CreateStatus() {
  models::driver::meta::Status status;
  status.timestamp = std::chrono::system_clock::from_time_t(time(nullptr));
  status.status = models::driver::meta::Status::DriverStatus::kVeryBusy;
  status.robot_status = models::driver::meta::Status::RobotStatus::kEnabled;
  status.tx_status = models::driver::meta::Status::TaximeterStatus::kOrder;
  status.order_provider = models::driver::meta::Status::OrderProvider::kUnknown;
  status.switched_on_classes =
      models::Classes{{models::Classes::Econom, models::Classes::UberX,
                       models::Classes::Ultimate}};
  status.disabled_Yandex = true;
  status.online_seconds = std::chrono::seconds{1234};
  status.dont_chain = true;
  status.only_card = true;
  return status;
}

models::driver::Profile CreateProfile() {
  models::driver::Profile profile;

  profile.driver_id.uuid = "uuid";
  profile.driver_id.clid = "clid";
  profile.license = "license";
  profile.driver_id.dbid = "db_id";
  profile.locale = "locale";
  profile.city = "city";
  profile.taximeter_version.Parse("1.2 (3)");

  time_t now_t = time(nullptr) - 300;
  profile.mqc_passed = std::chrono::system_clock::from_time_t(++now_t);

  profile.car = models::driver::ProfileCar{
      "number", "model", "mark_code", 1, "color", "color_code", 2, 3, 4, 6};

  {
    models::DriverRequirements dreq;
    std::unordered_set<std::string> booL_reqs = {"bool1", "bool2", "bool3"};
    std::unordered_map<std::string, short> int_reqs = {
        {"int1", 1}, {"int2", 2}, {"int3", 3}, {"int4", 4}};

    for (const auto& r : booL_reqs) dreq.Add(r, true);
    for (const auto& kv : int_reqs) dreq.Add(kv.first, kv.second);

    std::vector<models::ChildChairClassesSet> chairs{{1},    {2},    {3},
                                                     {1, 2}, {2, 3}, {1, 2, 3}};
    dreq.AddChildChairs(std::move(chairs));

    profile.requirements = std::move(dreq);
  }

  profile.allowed_classes = {models::Classes::Econom,
                             models::Classes::ComfortPlus,
                             models::Classes::UberBlack};
  profile.allowed_classes_orig = {models::Classes::Econom,
                                  models::Classes::ComfortPlus};

  profile.mqc_status = models::driver::MqcStatus::kCanTakeOrders;
  profile.supported_payment_methods =
      common::parks::ParsePaymentMethods({"card", "applepay", "cash"});
  profile.allowed_payment_methods =
      common::parks::ParsePaymentMethods({"card", "cash"});

  {
    profile.grades.by_class.Set(models::Classes::Econom, 1);
    profile.grades.by_class.Set(models::Classes::ComfortPlus, 2);
    profile.grades.by_class.Set(models::Classes::UberBlack, 3);
  }
  {
    profile.grades.by_class_air.Set(models::Classes::Econom, 4);
    profile.grades.by_class_air.Set(models::Classes::ComfortPlus, 5);
    profile.grades.by_class_air.Set(models::Classes::UberBlack, 6);
  }

  profile.park_deactivated = true;

  {
    models::driver::Workshift w1{
        "driver_id",
        std::chrono::system_clock::from_time_t(++now_t),
        std::chrono::system_clock::from_time_t(++now_t),
        "home_zone1",
        {"zone1", "zone2"}};
    models::driver::Workshift w2{
        "driver_id",
        std::chrono::system_clock::from_time_t(++now_t),
        std::chrono::system_clock::from_time_t(++now_t),
        "home_zone2",
        {"zone3", "zone4"}};
    models::driver::Workshifts w = {{"w1", w1}, {"w2", w2}};
    profile.workshifts =
        std::make_shared<models::driver::Workshifts>(std::move(w));
  }

  return profile;
}

models::driver::UniqueDriver CreateUniqueDriver() {
  models::driver::UniqueDriver driver;

  driver.id = "unique_driver_id";
  driver.licenses.emplace_back("license_1");

  models::driver_metrics::State driver_metrics_state;
  driver_metrics_state.blocked = true;
  driver_metrics_state.blocked_until =
      std::chrono::system_clock::from_time_t(time(nullptr) + 2100);
  driver_metrics_state.blocking_reason = "test_reason";
  driver_metrics_state.blocking_type = "test_type";

  driver.driver_metrics_state = driver_metrics_state;

  return driver;
}

models::driver::BusyInfo CreateBusyInfo() {
  models::driver::BusyInfo busy_info;

  busy_info.order_id = "order_id";
  busy_info.approximate = true;
  busy_info.destination = utils::geometry::Point{33.57, 55.76};
  busy_info.left_dist = 1025.8;
  busy_info.left_time = 645.7;

  return busy_info;
}

models::driver::pool::Info CreatePoolInfo() {
  models::driver::pool::Info pool_info;

  pool_info.umbrella_order_id = "umbrella_order_id";
  pool_info.orders.emplace_back(models::driver::pool::Order{
      "order_id_1", utils::geometry::Point{35.12, 55.34},
      utils::geometry::Point{36.56, 56.78}, 3, 5, true,
      std::chrono::system_clock::from_time_t(time(nullptr) - 300)});
  pool_info.orders.emplace_back(models::driver::pool::Order{
      "order_id_2", utils::geometry::Point{33.98, 53.76},
      utils::geometry::Point{34.54, 54.32}, 6, 7, true,
      std::chrono::system_clock::from_time_t(time(nullptr) - 200)

  });

  return pool_info;
}

models::driver::airport::QueuePosition CreateAirportQueuePosition() {
  models::driver::airport::QueuePosition queue_pos;

  queue_pos.id = "id";
  queue_pos.driver_id = "driver_id";
  queue_pos.zone_id = "zone_id";
  queue_pos.real_parking_id = "real_parking_id";
  queue_pos.recommended_parking_id = "recommended_parking_id";
  queue_pos.profile_db_id = "profile_db_id";

  auto tp = time(nullptr) - 100;
  queue_pos.created = std::chrono::system_clock::from_time_t(++tp);
  queue_pos.updated = std::chrono::system_clock::from_time_t(++tp);
  queue_pos.count_rejects = 12;
  queue_pos.time_activated = std::chrono::system_clock::from_time_t(++tp);
  queue_pos.time_deactivated = std::chrono::system_clock::from_time_t(++tp);
  queue_pos.time_exited = std::chrono::system_clock::from_time_t(++tp);
  queue_pos.time_online = std::chrono::system_clock::from_time_t(++tp);
  queue_pos.time_busy = std::chrono::system_clock::from_time_t(++tp);
  queue_pos.time_busy_reset = std::chrono::system_clock::from_time_t(++tp);
  queue_pos.busy_penalty = std::chrono::seconds{18};
  queue_pos.classes_info = {{models::Classes::Econom,
                             models::driver::airport::QueuePosition::ClassInfo{
                                 std::chrono::system_clock::from_time_t(++tp),
                                 34,
                                 {"first", "second", "third"}}},
                            {models::Classes::Business,
                             models::driver::airport::QueuePosition::ClassInfo{
                                 std::chrono::system_clock::from_time_t(++tp),
                                 boost::none,
                                 {"4th", "5th", "6th_tweak"}}}};
  queue_pos.active_classes_times = {
      {models::Classes::ChildTariff,
       std::chrono::system_clock::from_time_t(++tp)},
      {models::Classes::UberX, std::chrono::system_clock::from_time_t(++tp)}};
  queue_pos.active_classes = {models::Classes::ComfortPlus,
                              models::Classes::Express};
  queue_pos.available_classes = {models::Classes::Pool,
                                 models::Classes::PoputkaPromo};
  queue_pos.is_available_classes_only = true;
  queue_pos.virtual_updated = std::chrono::system_clock::from_time_t(++tp);
  queue_pos.frauder_list = {"frauder_1st", "frauder_2nd"};
  queue_pos.frauder_unbanned = std::chrono::system_clock::from_time_t(++tp);

  return queue_pos;
}

void CheckCarSerializations(const models::driver::Car& car) {
  const Json::Value json_car = pack::json::Car::Serialize(car);

  // Check number and blacklisted
  EXPECT_EQ(json_car["number"].asString(), car.number);
  EXPECT_EQ(json_car["blacklisted"].asBool(), car.blacklisted);

  // Check blacklisted_till
  EXPECT_EQ(json_car["blacklisted_till"].empty(), !car.blacklisted_till);

  if (!!car.blacklisted_till) {
    EXPECT_EQ(std::chrono::system_clock::from_time_t(
                  json_car["blacklisted_till"].asInt()),
              car.blacklisted_till.get());
  }

  // Check serialized manually_assigned_classes
  const auto& classes_json = json_car["manually_assigned_classes"];
  const auto& classes_orig = car.manually_assigned_classes;
  EXPECT_TRUE(classes_json.isObject());
  for (const auto& key : classes_json.getMemberNames()) {
    auto names_vector = classes_orig.at(key).GetNames();
    std::set<std::string> names_orig(names_vector.begin(), names_vector.end());
    std::set<std::string> names_json;

    for (Json::ArrayIndex i = 0; i < classes_json[key].size(); ++i) {
      EXPECT_TRUE(classes_json[key].isArray());
      EXPECT_TRUE(classes_json[key].size() == classes_orig.at(key).Count());
      names_json.insert(classes_json[key][i].asString());
    }
    EXPECT_EQ(names_json, names_orig);
  }

  // Check deserialized json car
  auto des_car = pack::json::Car::Deserialize(json_car);
  EXPECT_TRUE(IsEq(car, des_car));

  // Check flatbuffer serialazation
  const auto fbs_car = pack::fbs::Car::Serialize(car);
  const models::driver::Car unfbs_car = pack::fbs::Car::Deserialize(fbs_car);
  EXPECT_TRUE(IsEq(car, unfbs_car));
}

}  // namespace

TEST(Pack, ProfileCarTest) {
  models::driver::ProfileCar orig_car{
      "number", "model", "mark_code", 1, "color", "color_code", 2, 3, 4, 6};

  Json::Value json_car = pack::json::ProfileCar::Serialize(orig_car);
  EXPECT_EQ(json_car["number"].asString(), orig_car.number);
  EXPECT_EQ(json_car["model"].asString(), orig_car.model);
  EXPECT_EQ(json_car["mark_code"].asString(), orig_car.mark_code);
  EXPECT_EQ(json_car["age"].asInt(), orig_car.age);
  EXPECT_EQ(json_car["color"].asString(), orig_car.color);
  EXPECT_EQ(json_car["color_code"].asString(), orig_car.color_code);
  EXPECT_EQ(json_car["capacity"].asUInt64(), orig_car.capacity);
  EXPECT_EQ(json_car["capacity_luggage"].asUInt64(), orig_car.capacity_luggage);
  EXPECT_EQ(json_car["years"].asUInt(), orig_car.years);
  EXPECT_EQ(json_car["price"].asUInt(), orig_car.price);

  models::driver::ProfileCar decoded_json_car =
      pack::json::ProfileCar::Deserialize(json_car);
  EXPECT_TRUE(IsEq(decoded_json_car, orig_car));

  const auto fbs_car = pack::fbs::ProfileCar::Serialize(orig_car);
  models::driver::ProfileCar decoded_fbs_car =
      pack::fbs::ProfileCar::Deserialize(fbs_car);
  EXPECT_TRUE(IsEq(decoded_fbs_car, orig_car));
}

TEST(Pack, FullCarTest) {
  models::driver::Car car = CreateCar();

  CheckCarSerializations(car);
}

TEST(Pack, CarTestEmpty) {
  models::driver::Car car;
  car.number = "1234";
  CheckCarSerializations(car);
}

TEST(Pack, WorkshiftTest) {
  const time_t created_time = time(nullptr);
  const time_t date_finish = created_time + 68;

  models::driver::Workshift orig_workshift{
      "driver_id",
      std::chrono::system_clock::from_time_t(created_time),
      std::chrono::system_clock::from_time_t(date_finish),
      "home_zone",
      {"zone1", "zone2"}};

  Json::Value json_workshift = pack::json::Workshift::Serialize(orig_workshift);
  EXPECT_EQ(json_workshift["driver_id"].asString(), orig_workshift.driver_id);
  EXPECT_EQ(json_workshift["home_zone"].asString(), orig_workshift.home_zone);
  {
    decltype(orig_workshift.created) tp;
    utils::helpers::FetchMember(tp, json_workshift, "created");
    EXPECT_EQ(tp, orig_workshift.created);
  }
  {
    decltype(orig_workshift.date_finish) tp;
    utils::helpers::FetchMember(tp, json_workshift, "date_finish");
    EXPECT_EQ(tp, orig_workshift.date_finish);
  }
  {
    std::vector<std::string> zones;
    utils::helpers::FetchMember(zones, json_workshift, "zones");
    EXPECT_EQ(zones, orig_workshift.zones);
  }

  models::driver::Workshift decoded_json_workshift =
      pack::json::Workshift::Deserialize(json_workshift);
  EXPECT_TRUE(IsEq(decoded_json_workshift, orig_workshift));

  const auto fbs_workshift = pack::fbs::Workshift::Serialize(orig_workshift);
  models::driver::Workshift decoded_fbs_workshift =
      pack::fbs::Workshift::Deserialize(fbs_workshift);
  EXPECT_TRUE(IsEq(decoded_fbs_workshift, orig_workshift));

  models::driver::Workshift orig_workshift2{
      "driver_id_2",
      std::chrono::system_clock::from_time_t(created_time + 120),
      std::chrono::system_clock::from_time_t(date_finish + 120),
      "home_zone_2",
      {"zone3", "zone4", "zone5"}};

  models::driver::Workshifts orig_workshifts{{"key1", orig_workshift},
                                             {"key2", orig_workshift2}};
  Json::Value json_workshifts =
      pack::json::Workshifts::Serialize(orig_workshifts);
  models::driver::Workshifts decoded_json_workshifts =
      pack::json::Workshifts::Deserialize(json_workshifts);
  EXPECT_TRUE(IsEq(decoded_json_workshifts, orig_workshifts));

  const auto fbs_workshifts = pack::fbs::Workshifts::Serialize(orig_workshifts);
  models::driver::Workshifts decoded_fbs_workshifts =
      pack::fbs::Workshifts::Deserialize(fbs_workshifts);
  EXPECT_TRUE(IsEq(decoded_fbs_workshifts, orig_workshifts));
}

TEST(Pack, RequirementsTest) {
  models::Requirements req;
  {
    std::unordered_set<std::string> booL_reqs = {"bool1", "bool2", "bool3"};
    std::unordered_map<std::string, short> int_reqs = {
        {"int1", 1}, {"int2", 2}, {"int3", 3}, {"int4", 4}};

    for (const auto& r : booL_reqs) req.Add(r, true);
    for (const auto& kv : int_reqs) req.Add(kv.first, kv.second);
  }

  {
    const auto js_reqs = pack::json::Requirements::Serialize(req);
    const auto decoded_req = pack::json::Requirements::Deserialize(js_reqs);
    EXPECT_TRUE(IsEq(req, decoded_req));
  }
  {
    const auto fbs_reqs = pack::fbs::Requirements::Serialize(req);
    const auto decoded_req = pack::fbs::Requirements::Deserialize(fbs_reqs);
    EXPECT_TRUE(IsEq(req, decoded_req));
  }

  models::DriverRequirements dreq(std::cref(req));
  {
    std::vector<models::ChildChairClassesSet> chairs{{1},    {2},    {3},
                                                     {1, 2}, {2, 3}, {1, 2, 3}};
    dreq.AddChildChairs(std::move(chairs));

    EXPECT_TRUE(IsEq(req, static_cast<const models::Requirements&>(dreq)));
  }

  {
    const auto js_dreqs = pack::json::DriverRequirements::Serialize(dreq);
    const auto decoded_dreq =
        pack::json::DriverRequirements::Deserialize(js_dreqs);
    EXPECT_TRUE(IsEq(dreq, decoded_dreq));
  }
  {
    const auto fbs_dreqs = pack::fbs::DriverRequirements::Serialize(dreq);
    const auto decoded_dreq =
        pack::fbs::DriverRequirements::Deserialize(fbs_dreqs);
    EXPECT_TRUE(IsEq(dreq, decoded_dreq));
  }
}

TEST(Pack, ProfileTest) {
  models::driver::Profile profile = CreateProfile();

  {
    const auto js_profile = pack::json::Profile::Serialize(profile);
    const auto decoded_profile = pack::json::Profile::Deserialize(js_profile);
    EXPECT_TRUE(IsEq(profile, decoded_profile));
  }
  {
    const auto fbs_profile = pack::fbs::Profile::Serialize(profile);
    const auto decoded_profile = pack::fbs::Profile::Deserialize(fbs_profile);
    EXPECT_TRUE(IsEq(profile, decoded_profile));
  }
}

TEST(Pack, MetaStatusTest) {
  models::driver::meta::Status status;
  {
    status.timestamp = std::chrono::system_clock::from_time_t(time(nullptr));
    status.status = models::driver::meta::Status::DriverStatus::kVeryBusy;
    status.robot_status = models::driver::meta::Status::RobotStatus::kEnabled;
    status.tx_status = models::driver::meta::Status::TaximeterStatus::kOrder;
    status.order_provider =
        models::driver::meta::Status::OrderProvider::kUnknown;
    status.switched_on_classes =
        models::Classes{{models::Classes::Econom, models::Classes::UberX,
                         models::Classes::Ultimate}};
    status.disabled_Yandex = true;
    status.online_seconds = std::chrono::seconds{1234};
    status.dont_chain = true;
    status.only_card = true;
  }

  {
    const auto js_status = pack::json::MetaStatus::Serialize(status);
    const auto decoded_statis = pack::json::MetaStatus::Deserialize(js_status);
    EXPECT_TRUE(IsEq(status, decoded_statis));
  }
  {
    const auto fbs_status = pack::fbs::MetaStatus::Serialize(status);
    const auto decoded_status = pack::fbs::MetaStatus::Deserialize(fbs_status);
    EXPECT_TRUE(IsEq(status, decoded_status));
  }
}

TEST(Pack, BusyInfoTest) {
  models::driver::BusyInfo busy_info = CreateBusyInfo();

  {
    const auto js_busy_info = pack::json::BusyInfo::Serialize(busy_info);
    const auto decoded_busy_info =
        pack::json::BusyInfo::Deserialize(js_busy_info);
    EXPECT_TRUE(IsEq(busy_info, decoded_busy_info));
  }
  {
    const auto fbs_busy_info = pack::fbs::BusyInfo::Serialize(busy_info);
    const auto decoded_busy_info =
        pack::fbs::BusyInfo::Deserialize(fbs_busy_info);
    EXPECT_TRUE(IsEq(busy_info, decoded_busy_info));
  }
}

TEST(Pack, PoolOrderTest) {
  models::driver::pool::Order pool_order;
  {
    pool_order.order_id = "order_id";
    pool_order.source = utils::geometry::Point{35.12, 55.34};
    pool_order.destination = utils::geometry::Point{36.56, 56.78};
    pool_order.passengers_count = 3;
    pool_order.luggage_count = 5;
    pool_order.transporting = true;
    pool_order.start_time =
        std::chrono::system_clock::from_time_t(time(nullptr));
  }

  {
    const auto js_pool_order = pack::json::PoolOrder::Serialize(pool_order);
    const auto decoded_pool_order =
        pack::json::PoolOrder::Deserialize(js_pool_order);
    EXPECT_TRUE(IsEq(pool_order, decoded_pool_order));
  }
  {
    const auto fbs_pooL_order = pack::fbs::PoolOrder::Serialize(pool_order);
    const auto decoded_pool_order =
        pack::fbs::PoolOrder::Deserialize(fbs_pooL_order);
    EXPECT_TRUE(IsEq(pool_order, decoded_pool_order));
  }
}

TEST(Pack, PoolInfoTest) {
  models::driver::pool::Info pool_info = CreatePoolInfo();

  {
    const auto js_pool_info = pack::json::PoolInfo::Serialize(pool_info);
    const auto decoded_pool_info =
        pack::json::PoolInfo::Deserialize(js_pool_info);
    EXPECT_TRUE(IsEq(pool_info, decoded_pool_info));
  }
  {
    const auto fbs_pooL_info = pack::fbs::PoolInfo::Serialize(pool_info);
    const auto decoded_pool_info =
        pack::fbs::PoolInfo::Deserialize(fbs_pooL_info);
    EXPECT_TRUE(IsEq(pool_info, decoded_pool_info));
  }
}

TEST(Pack, AirportClassInfoTest) {
  models::driver::airport::QueuePosition::ClassInfo class_info;
  {
    class_info.time_virtual_enabled =
        std::chrono::system_clock::from_time_t(time(nullptr));
    class_info.virtual_positions_before = 3;
    class_info.drivers_before = {{"first", "second", "third"}};
  }

  {
    const auto js_class_info =
        pack::json::AirportClassInfo::Serialize(class_info);
    const auto decoded_class_info =
        pack::json::AirportClassInfo::Deserialize(js_class_info);
    EXPECT_TRUE(IsEq(class_info, decoded_class_info));
  }
  {
    const auto fbs_class_info =
        pack::fbs::AirportClassInfo::Serialize(class_info);
    const auto decoded_class_info =
        pack::fbs::AirportClassInfo::Deserialize(fbs_class_info);
    EXPECT_TRUE(IsEq(class_info, decoded_class_info));
  }
}

TEST(Pack, AirportQueuePositionTest) {
  models::driver::airport::QueuePosition queue_pos =
      CreateAirportQueuePosition();

  {
    const auto js_queue_pos =
        pack::json::AirportQueuePosition::Serialize(queue_pos);
    const auto decoded_queue_pos =
        pack::json::AirportQueuePosition::Deserialize(js_queue_pos);
    EXPECT_TRUE(IsEq(queue_pos, decoded_queue_pos));
  }
  {
    const auto fbs_queue_pos =
        pack::fbs::AirportQueuePosition::Serialize(queue_pos);
    const auto decoded_queue_pos =
        pack::fbs::AirportQueuePosition::Deserialize(fbs_queue_pos);
    EXPECT_TRUE(IsEq(queue_pos, decoded_queue_pos));
  }
}

TEST(Pack, IndexedDriverTest) {
  models::driver::IndexedDriver indexed_driver(
      "driver_id", std::make_shared<models::driver::Profile>(CreateProfile()),
      std::make_shared<models::driver::UniqueDriver>(CreateUniqueDriver()),
      std::make_shared<parks_activation::models::Park>(),
      models::driver::Score::FromInternalScore(0.0), CreateCar(),
      models::Classes{models::Classes::Econom, models::Classes::ComfortPlus,
                      models::Classes::UberBlack},
      CreateRepositionIndexEntry(), CreateStatus(),
      utils::geometry::TrackPoint{
          33.75, 55.67, 1.0, 123.8,
          std::chrono::system_clock::from_time_t(time(nullptr)),
          utils::geometry::PointSource::Adjuster},
      CreateBusyInfo(), CreatePoolInfo(),
      models::driver::payment_type::Type::ONLINE, CreateAirportQueuePosition(),
      std::set<std::string>({"exp_1", "experiment_2", "exprmnt3"}), {}, true);

  {
    const auto js_indexed_driver =
        pack::json::IndexedDriver::Serialize(indexed_driver);
    const auto decoded_indexed_driver =
        pack::json::IndexedDriver::Deserialize(js_indexed_driver);
    EXPECT_TRUE(IsEq(indexed_driver, decoded_indexed_driver));
  }
  {
    const auto fbs_indexed_driver =
        pack::fbs::IndexedDriver::Serialize(indexed_driver);
    const auto decoded_indexed_driver =
        pack::fbs::IndexedDriver::Deserialize(fbs_indexed_driver);
    EXPECT_TRUE(IsEq(indexed_driver, decoded_indexed_driver));
  }
}

TEST(Pack, RoutedDriversTest) {
  models::driver::RoutedDriversBulk orig_routed_drivers_bulk;
  {
    const models::driver::IndexedDriver indexed_driver(
        "driver_id1",
        std::make_shared<models::driver::Profile>(CreateProfile()),
        std::make_shared<models::driver::UniqueDriver>(),
        std::make_shared<parks_activation::models::Park>(),
        models::driver::Score::FromInternalScore(0.0), CreateCar(),
        models::Classes{models::Classes::Econom, models::Classes::ComfortPlus,
                        models::Classes::UberBlack},
        CreateRepositionIndexEntry(), CreateStatus(),
        utils::geometry::TrackPoint{
            33.75, 55.67, 1.0, 123.8,
            std::chrono::system_clock::from_time_t(time(nullptr)),
            utils::geometry::PointSource::Adjuster},
        CreateBusyInfo(), CreatePoolInfo(),
        models::driver::payment_type::Type::ONLINE,
        CreateAirportQueuePosition(),
        std::set<std::string>({"exp_1", "experiment_2", "exprmnt3"}));

    orig_routed_drivers_bulk.routed_drivers_bulk.push_back(
        {{indexed_driver, {1, 2}, clients::routing::RouteInfo{6.1, 2.4}}});
  }
  {
    const models::driver::IndexedDriver indexed_driver(
        "driver_id2",
        std::make_shared<models::driver::Profile>(CreateProfile()),
        std::make_shared<models::driver::UniqueDriver>(),
        std::make_shared<parks_activation::models::Park>(), boost::none,
        CreateCar(),
        models::Classes{models::Classes::Start, models::Classes::Business},
        CreateRepositionIndexEntry(), CreateStatus(),
        utils::geometry::TrackPoint{
            32.23, 54.89, 3.0, 320.8,
            std::chrono::system_clock::from_time_t(time(nullptr)),
            utils::geometry::PointSource::Adjuster},
        CreateBusyInfo(), CreatePoolInfo(),
        models::driver::payment_type::Type::CASH, CreateAirportQueuePosition(),
        std::set<std::string>({"exp_5", "experiment_8", "exprmnt0"}));

    orig_routed_drivers_bulk.routed_drivers_bulk.push_back(
        {{indexed_driver, {3, 5}, clients::routing::RouteInfo{7.8, 5.6}}});
  }

  {
    const auto& json_routed_drivers_bulk =
        pack::json::RoutedDriversBulk::Serialize(orig_routed_drivers_bulk);

    const auto& deserialized_routed_drivers_bulk =
        pack::json::RoutedDriversBulk::Deserialize(json_routed_drivers_bulk);
    EXPECT_TRUE(
        IsEq(orig_routed_drivers_bulk, deserialized_routed_drivers_bulk));
  }
  {
    const auto& fbs_routed_drivers_bulk =
        pack::fbs::RoutedDriversBulk::Serialize(orig_routed_drivers_bulk);
    const auto& deserialized_routed_drivers_bulk =
        pack::fbs::RoutedDriversBulk::Deserialize(fbs_routed_drivers_bulk);

    EXPECT_TRUE(
        IsEq(orig_routed_drivers_bulk, deserialized_routed_drivers_bulk));
  }
}
