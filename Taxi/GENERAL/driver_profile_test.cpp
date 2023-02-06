#include <boost/range/adaptor/map.hpp>
#include <boost/range/iterator_range.hpp>

#include <gtest/gtest.h>

#include <mongo/mongo.hpp>
#include <mongo/names/dbdrivers.hpp>

#include "driver_profile.hpp"

using models::DriverProfile;
using models::DriverProfiles;
using models::ParkDriverProfiles;
using models::UpsertDriverProfile;

namespace names = utils::mongo::db::drivers;

void DPWithWorkRuleIdAndStatusHelper(mongo::BSONObjBuilder& builder,
                                     const std::string& id,
                                     const std::string& park_id,
                                     const std::string& work_status,
                                     const std::string& work_rule_id) {
  builder.append(names::kDriverId, id);
  builder.append(names::kParkId, park_id);

  if (!work_rule_id.empty()) {
    builder.append(names::kRuleId, work_rule_id);
  }

  if (!work_status.empty()) {
    builder.append(names::kWorkStatus, work_status);
  }
}

DriverProfile DPWithWorkRuleIdAndStatus(const std::string& id,
                                        const std::string& park_id,
                                        const std::string& work_status,
                                        const std::string& work_rule_id = "") {
  mongo::BSONObjBuilder builder;
  DPWithWorkRuleIdAndStatusHelper(builder, id, park_id, work_status,
                                  work_rule_id);
  return DriverProfile{builder.obj()};
}

DriverProfile DPWithWorkRuleIdAndStatusDeleted(
    const std::string& id, const std::string& park_id,
    const std::string& work_status, const std::string& work_rule_id = "") {
  mongo::BSONObjBuilder builder;
  DPWithWorkRuleIdAndStatusHelper(builder, id, park_id, work_status,
                                  work_rule_id);
  builder.append(names::kIsRemovedByRequest, true);
  return DriverProfile{builder.obj()};
}

DriverProfile DPWithPassword(const std::string& id, const std::string& park_id,
                             const std::string& password) {
  mongo::BSONObjBuilder builder;
  builder.append(names::kDriverId, id);
  builder.append(names::kParkId, park_id);

  if (!password.empty()) {
    builder.append(names::kPassword, password);
  }

  return DriverProfile{builder.obj()};
}

void DPWithLastTransactionDateHelper(
    mongo::BSONObjBuilder& builder, const std::string& id,
    const std::string& park_id,
    const boost::optional<std::chrono::system_clock::time_point>&
        last_transaction_date) {
  builder.append(names::kDriverId, id);
  builder.append(names::kParkId, park_id);

  if (last_transaction_date) {
    builder.append(names::kLastTransactionDate,
                   utils::mongo::Date(*last_transaction_date));
  }
}

DriverProfile DPWithLastTransactionDate(
    const std::string& id, const std::string& park_id,
    const boost::optional<std::chrono::system_clock::time_point>&
        last_transaction_date) {
  mongo::BSONObjBuilder builder;
  DPWithLastTransactionDateHelper(builder, id, park_id, last_transaction_date);
  return DriverProfile{builder.obj()};
}

DriverProfile DPWithLastTransactionDateDeleted(
    const std::string& id, const std::string& park_id,
    const boost::optional<std::chrono::system_clock::time_point>&
        last_transaction_date) {
  mongo::BSONObjBuilder builder;
  DPWithLastTransactionDateHelper(builder, id, park_id, last_transaction_date);
  builder.append(names::kIsRemovedByRequest, true);
  return DriverProfile{builder.obj()};
}

void CheckValueIndex(
    const std::unordered_map<std::string, std::set<std::size_t>>& value_map,
    const std::string& value, std::size_t index) {
  for (const auto& pair : value_map) {
    if (pair.first == value) {
      ASSERT_TRUE(pair.second.find(index) != pair.second.end());
    } else {
      ASSERT_TRUE(pair.second.find(index) == pair.second.end());
    }
  }
}

void CheckValueIndexRemoved(
    const std::unordered_map<std::string, std::set<std::size_t>>& value_map,
    std::size_t index) {
  for (const auto& pair : value_map) {
    ASSERT_TRUE(pair.second.find(index) == pair.second.end());
  }
}

void CheckDriverProfileInPark(const ParkDriverProfiles& profiles,
                              const DriverProfile& profile) {
  const auto& it = profiles.id_map.find(profile.GetId());
  ASSERT_TRUE(it != profiles.id_map.end());
  const auto index = it->second;
  const auto& data_profile = profiles.data.at(index);
  ASSERT_EQ(profile.GetId(), data_profile.GetId());
  ASSERT_EQ(profile.GetParkId(), data_profile.GetParkId());
  ASSERT_EQ(profile.GetWorkRuleId(), data_profile.GetWorkRuleId());
  ASSERT_EQ(profile.GetWorkStatus(), data_profile.GetWorkStatus());
  if (!profile.IsRemovedByRequest()) {
    CheckValueIndex(profiles.work_rule_id_map, profile.GetWorkRuleId(), index);
    CheckValueIndex(profiles.work_status_map, profile.GetWorkStatus(), index);
  } else {
    CheckValueIndexRemoved(profiles.work_rule_id_map, index);
    CheckValueIndexRemoved(profiles.work_status_map, index);
  }
}

TEST(TestUpsertDriverProfile, UpdateDriverProfile) {
  ParkDriverProfiles cache;

  const std::string kId = "anton";
  const std::string kParkId = "mospark";
  const std::string kWorking = "working";
  const std::string kFired = "fired";
  const std::string kYandex = "yandex";

  const auto& profile_v1 = DPWithWorkRuleIdAndStatus(kId, kParkId, kWorking);

  UpsertDriverProfile(cache, DriverProfile{profile_v1});
  ASSERT_EQ(1u, cache.data.size());
  CheckDriverProfileInPark(cache, profile_v1);

  UpsertDriverProfile(cache, DriverProfile(profile_v1));
  ASSERT_EQ(1u, cache.data.size());
  CheckDriverProfileInPark(cache, profile_v1);

  const auto& profile_v2 = DPWithWorkRuleIdAndStatus(kId, kParkId, kFired);

  UpsertDriverProfile(cache, DriverProfile(profile_v2));
  ASSERT_EQ(1u, cache.data.size());
  CheckDriverProfileInPark(cache, profile_v2);

  const auto& profile_v3 =
      DPWithWorkRuleIdAndStatus(kId, kParkId, kFired, kYandex);

  UpsertDriverProfile(cache, DriverProfile(profile_v3));
  ASSERT_EQ(1u, cache.data.size());
  CheckDriverProfileInPark(cache, profile_v3);

  const auto& profile_v4 = DPWithWorkRuleIdAndStatus(kId, kParkId, "", kYandex);

  UpsertDriverProfile(cache, DriverProfile(profile_v4));
  ASSERT_EQ(1u, cache.data.size());
  CheckDriverProfileInPark(cache, profile_v4);
}

TEST(TestUpsertDriverProfile, UpdateDriverProfileDeleted) {
  ParkDriverProfiles cache;

  const std::string kId = "anton";
  const std::string kParkId = "mospark";
  const std::string kFired = "fired";
  const std::string kYandex = "yandex";

  const auto& profile =
      DPWithWorkRuleIdAndStatus(kId, kParkId, kFired, kYandex);
  const auto& profile_deleted =
      DPWithWorkRuleIdAndStatusDeleted(kId, kParkId, kFired, kYandex);

  UpsertDriverProfile(cache, DriverProfile(profile_deleted));
  ASSERT_EQ(1u, cache.data.size());
  CheckDriverProfileInPark(cache, profile_deleted);

  UpsertDriverProfile(cache, DriverProfile(profile));
  ASSERT_EQ(1u, cache.data.size());
  CheckDriverProfileInPark(cache, profile);

  UpsertDriverProfile(cache, DriverProfile(profile_deleted));
  ASSERT_EQ(1u, cache.data.size());
  CheckDriverProfileInPark(cache, profile_deleted);
}

TEST(TestUpsertDriverProfile, Password) {
  ParkDriverProfiles cache;

  const std::string kParkId = "mospark";

  UpsertDriverProfile(cache, DPWithPassword("1", kParkId, "123"));
  ASSERT_EQ(1u, cache.data.size());
  ASSERT_EQ(1u, cache.payment_service_ids.size());
  ASSERT_EQ(1u, cache.payment_service_ids.count("123"));

  UpsertDriverProfile(cache, DPWithPassword("1", kParkId, "123"));
  ASSERT_EQ(1u, cache.data.size());
  ASSERT_EQ(1u, cache.payment_service_ids.size());
  ASSERT_EQ(1u, cache.payment_service_ids.count("123"));

  UpsertDriverProfile(cache, DPWithPassword("2", kParkId, "234"));
  ASSERT_EQ(2u, cache.data.size());
  ASSERT_EQ(2u, cache.payment_service_ids.size());
  ASSERT_EQ(1u, cache.payment_service_ids.count("234"));

  UpsertDriverProfile(cache, DPWithPassword("1", kParkId, "234"));
  ASSERT_EQ(2u, cache.data.size());
  ASSERT_EQ(2u, cache.payment_service_ids.size());
  ASSERT_EQ(2u, cache.payment_service_ids.count("234"));

  UpsertDriverProfile(cache, DPWithPassword("1", kParkId, {}));
  ASSERT_EQ(2u, cache.data.size());
  ASSERT_EQ(1u, cache.payment_service_ids.size());
  ASSERT_EQ(1u, cache.payment_service_ids.count("234"));

  UpsertDriverProfile(cache, DPWithPassword("2", kParkId, {}));
  ASSERT_EQ(2u, cache.data.size());
  ASSERT_EQ(0u, cache.payment_service_ids.size());

  UpsertDriverProfile(cache, DPWithPassword("2", kParkId, {}));
  ASSERT_EQ(2u, cache.data.size());
  ASSERT_EQ(0u, cache.payment_service_ids.size());
}

using Uset = std::set<size_t>;

Uset GetValsSet(const utils::SortedIndex& index,
                const std::chrono::system_clock::time_point t) {
  const auto [beg, end] = index.equal_range(t);
  const auto vals =
      boost::make_iterator_range(beg, end) | boost::adaptors::map_values;
  return Uset(boost::begin(vals), boost::end(vals));
}

TEST(TestUpsertDriverProfile, LastTransactionDate) {
  ParkDriverProfiles cache;

  const std::string kParkId = "mospark";
  std::chrono::system_clock::time_point some_time{std::chrono::seconds{100}};

  {
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("1", kParkId, some_time));
    ASSERT_EQ(1u, cache.data.size());
    ASSERT_EQ(1u, cache.last_transaction_date_index.size());
    ASSERT_EQ((Uset{0u}),
              GetValsSet(cache.last_transaction_date_index, some_time));
  }

  {
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("1", kParkId, some_time));
    ASSERT_EQ(1u, cache.data.size());
    ASSERT_EQ(1u, cache.last_transaction_date_index.size());
    ASSERT_EQ((Uset{0u}),
              GetValsSet(cache.last_transaction_date_index, some_time));
  }

  {
    // it is impossible that last_transaction_date disappears, but let`s check
    // this case anyway
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("1", kParkId, boost::none));
    ASSERT_EQ(1u, cache.data.size());
    ASSERT_EQ(0u, cache.last_transaction_date_index.size());
  }

  {
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("1", kParkId, boost::none));
    ASSERT_EQ(1u, cache.data.size());
    ASSERT_EQ(0u, cache.last_transaction_date_index.size());
  }

  {
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("2", kParkId, some_time));
    ASSERT_EQ(2u, cache.data.size());
    ASSERT_EQ(1u, cache.last_transaction_date_index.size());
    ASSERT_EQ(1u, cache.last_transaction_date_index.count(some_time));
    ASSERT_EQ((Uset{1u}),
              GetValsSet(cache.last_transaction_date_index, some_time));
  }

  {
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("1", kParkId, some_time));
    ASSERT_EQ(2u, cache.data.size());
    ASSERT_EQ(2u, cache.last_transaction_date_index.size());
    ASSERT_EQ(2u, cache.last_transaction_date_index.count(some_time));
    ASSERT_EQ((Uset{0u, 1u}),
              GetValsSet(cache.last_transaction_date_index, some_time));
  }

  auto other_time = some_time + std::chrono::seconds{1};
  {
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("3", kParkId, other_time));
    ASSERT_EQ(3u, cache.data.size());
    ASSERT_EQ(3u, cache.last_transaction_date_index.size());
    ASSERT_EQ((Uset{0u, 1u}),
              GetValsSet(cache.last_transaction_date_index, some_time));
    ASSERT_EQ((Uset{2u}),
              GetValsSet(cache.last_transaction_date_index, other_time));
  }

  {
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("1", kParkId, other_time));
    ASSERT_EQ(3u, cache.data.size());
    ASSERT_EQ(3u, cache.last_transaction_date_index.size());
    ASSERT_EQ((Uset{1u}),
              GetValsSet(cache.last_transaction_date_index, some_time));
    ASSERT_EQ((Uset{0u, 2u}),
              GetValsSet(cache.last_transaction_date_index, other_time));
  }

  auto otro_tiempo = some_time + std::chrono::seconds{2};
  {
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("1", kParkId, otro_tiempo));
    ASSERT_EQ(3u, cache.data.size());
    ASSERT_EQ(3u, cache.last_transaction_date_index.size());
    ASSERT_EQ((Uset{1u}),
              GetValsSet(cache.last_transaction_date_index, some_time));
    ASSERT_EQ((Uset{2u}),
              GetValsSet(cache.last_transaction_date_index, other_time));
    ASSERT_EQ((Uset{0u}),
              GetValsSet(cache.last_transaction_date_index, otro_tiempo));
  }
}

TEST(TestUpsertDriverProfile, LastTransactionDateDeleted) {
  ParkDriverProfiles cache;

  const std::string kParkId = "mospark";
  std::chrono::system_clock::time_point some_time{std::chrono::seconds{100}};

  {
    UpsertDriverProfile(
        cache, DPWithLastTransactionDateDeleted("1", kParkId, some_time));
    ASSERT_EQ(1u, cache.data.size());
    ASSERT_EQ(0u, cache.last_transaction_date_index.size());
  }

  {
    UpsertDriverProfile(cache,
                        DPWithLastTransactionDate("1", kParkId, some_time));
    ASSERT_EQ(1u, cache.data.size());
    ASSERT_EQ(1u, cache.last_transaction_date_index.size());
    ASSERT_EQ((Uset{0u}),
              GetValsSet(cache.last_transaction_date_index, some_time));
  }

  {
    UpsertDriverProfile(
        cache, DPWithLastTransactionDateDeleted("1", kParkId, some_time));
    ASSERT_EQ(1u, cache.data.size());
    ASSERT_EQ(0u, cache.last_transaction_date_index.size());
  }
}
