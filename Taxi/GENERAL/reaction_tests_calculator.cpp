#include "reaction_tests_calculator.hpp"

#include <boost/algorithm/string.hpp>
#include <boost/range/algorithm/replace_if.hpp>
#include <config/config.hpp>
#include <config/reaction_tests_config.hpp>
#include <models/taxi_drivers.hpp>
#include <mongo/mongo.hpp>
#include <mongo/names/reaction_tests.hpp>
#include <utils/datetime.hpp>
#include <utils/driver_weariness/work_calc.hpp>
#include <utils/driver_weariness/work_interval_merger.hpp>
#include <utils/helpers/params.hpp>
#include <utils/l10n.hpp>
#include <utils/prof.hpp>
#include <utils/time.hpp>
#include "components/caches.hpp"
#include "helpers/driver_weariness.hpp"

namespace workers {

namespace {

namespace names = utils::mongo::db::StatusHistory::ReactionTests;

static const std::string kReactionTestSchulte = "reaction_test_schulte";
static const std::string kReactionTestGopher = "reaction_test_gopher";

const int kBulkSize = 10000;

struct DriverTestInfo {
  models::ReactionTestType test_type{};
  bool test_required = false;

  std::string city;
  std::string last_driver_id;
  std::chrono::seconds working_time_no_rest{0};
  utils::TimePoint last_work_timepoint;
  utils::TimePoint start_work_norest_timepoint;
  utils::TimePoint end_work_norest_timepoint;
};

struct ReactionTestsInfo {
  std::unordered_map<std::string, DriverTestInfo> driver_test_map;
};

DriverTestInfo GetOrCreateTestInfo(ReactionTestsInfo& result,
                                   const std::string& uniq_driver_id,
                                   const std::string& driver_id,
                                   const boost::optional<std::string>& city,
                                   handlers::Context& context) {
  auto it = result.driver_test_map.find(uniq_driver_id);
  if (it != result.driver_test_map.end()) {
    LOG_DEBUG() << "Found statuses from another profile. Uniq driver: "
                << uniq_driver_id << " driver_id: " << driver_id
                << " prev_driver_id: " << it->second.last_driver_id
                << context.log_extra;
    return it->second;
  }

  DriverTestInfo ret{};

  if (city) {
    try {
      ret.city = utils::driver_weariness::NormalizeCityNameForGraphite(
          l10n::Transliterate(*city));
    } catch (const std::exception& exp) {
      LOG_WARNING() << "Failed to transliterate city: " << *city
                    << context.log_extra;
    }
  }

  return ret;
}

void UpdateNoRestWorkTime(
    DriverTestInfo& driver_test_info,
    const helpers::driver_weariness::WorkNoRestInfo& work_info,
    const std::chrono::minutes& long_rest_time) {
  if (driver_test_info.start_work_norest_timepoint.time_since_epoch().count() ==
      0) {
    // First time just set data.
    driver_test_info.start_work_norest_timepoint =
        work_info.start_work_timepoint;
    driver_test_info.end_work_norest_timepoint = work_info.end_work_timepoint;
  } else {
    // Merge intervals
    if (driver_test_info.end_work_norest_timepoint <=
        work_info.start_work_timepoint) {
      // new interval after previous
      auto time_diff = work_info.start_work_timepoint -
                       driver_test_info.end_work_norest_timepoint;
      if (time_diff > long_rest_time) {
        // new interval is after long rest, so take it.
        driver_test_info.start_work_norest_timepoint =
            work_info.start_work_timepoint;
        driver_test_info.end_work_norest_timepoint =
            work_info.end_work_timepoint;
      } else {
        // merge, because distance less than long rest.
        driver_test_info.end_work_norest_timepoint =
            work_info.end_work_timepoint;
      }
    } else if (driver_test_info.start_work_norest_timepoint >=
               work_info.end_work_timepoint) {
      // new interval before previous
      auto time_diff = driver_test_info.start_work_norest_timepoint -
                       work_info.end_work_timepoint;
      if (time_diff <= long_rest_time) {
        // if distance less long rest, then merge.
        driver_test_info.start_work_norest_timepoint =
            work_info.start_work_timepoint;
      }
    } else {
      // interval intersects
      driver_test_info.start_work_norest_timepoint =
          std::min(driver_test_info.start_work_norest_timepoint,
                   work_info.start_work_timepoint);
      driver_test_info.end_work_norest_timepoint =
          std::max(driver_test_info.end_work_norest_timepoint,
                   work_info.end_work_timepoint);
    }
  }

  driver_test_info.working_time_no_rest =
      std::chrono::duration_cast<std::chrono::seconds>(
          driver_test_info.end_work_norest_timepoint -
          driver_test_info.start_work_norest_timepoint);
  driver_test_info.last_work_timepoint = std::max(
      work_info.end_work_timepoint, driver_test_info.last_work_timepoint);
}

models::ReactionTestType GetTestType(const std::set<std::string>& experiments,
                                     const LogExtra& log_extra) {
  if (experiments.count(kReactionTestSchulte)) {
    return models::ReactionTestType::Schulte;
  } else if (experiments.count(kReactionTestGopher)) {
    return models::ReactionTestType::Gopher;
  } else {
    LOG_ERROR() << "Cannot determine reaction test type for driver"
                << log_extra;
    throw std::runtime_error("no experiment to generate test");
  }
}

bool IsLastStatusOffline(const models::DriverStatuses& statuses,
                         const LogExtra& log_extra) {
  if (statuses.empty()) {
    LOG_WARNING() << "No statuses for driver" << log_extra;
    return true;
  }
  return !helpers::driver_weariness::IsOnlineStatus(statuses.back());
}

void UpdateDriverTestInfo(
    DriverTestInfo& driver_test_info, const models::DriverStatuses& statuses,
    const utils::TimePoint& now, const boost::optional<std::string>& city,
    const std::string& driver_id, const std::string& uniq_driver_id,
    const boost::optional<utils::TimePoint>& last_test_time,
    const boost::optional<utils::TimePoint>& blocked_till,
    const config::ReactionTests& config,
    const std::set<std::string>& experiments, const LogExtra& log_extra) {
  const auto& long_rest_time = config.reaction_tests_rest_minutes.Get(city);
  const auto& last_status_age_limit =
      config.reaction_tests_offline_status_threshold_minutes.Get();
  const auto& max_interval_time =
      config.reaction_tests_max_calc_interval_minutes.Get();
  const auto& max_work_after_long_rest =
      config.reaction_tests_max_work_after_long_rest_minutes.Get(city);
  const auto& max_work_after_test =
      config.reaction_tests_max_work_after_test_minutes.Get(city);

  auto relevant_statuses_interval =
      std::max(max_work_after_long_rest, max_work_after_test);
  relevant_statuses_interval += long_rest_time;

  const auto& work_no_rest_info =
      helpers::driver_weariness::CalcDriverWorkNoRestInfo(
          statuses, now, relevant_statuses_interval, max_interval_time,
          long_rest_time);

  LOG_DEBUG()
      << "calculated work no rest: "
      << utils::datetime::Timestring(work_no_rest_info.end_work_timepoint)
      << " "
      << utils::datetime::Timestring(work_no_rest_info.start_work_timepoint)
      << " " << log_extra << LogExtra({{"uniq_driver_id", uniq_driver_id}});

  if (work_no_rest_info.end_work_timepoint.time_since_epoch().count() != 0) {
    UpdateNoRestWorkTime(driver_test_info, work_no_rest_info, long_rest_time);
  }

  driver_test_info.last_driver_id = driver_id;

  // if  now - last work timepoint  > offline driver treshold dont add test
  if (IsLastStatusOffline(statuses, log_extra) ||
      now - driver_test_info.last_work_timepoint > last_status_age_limit) {
    LOG_DEBUG() << "Driver is offline, do not add reaction test"
                << LogExtra({{"uniq_driver_id", uniq_driver_id}}) << log_extra;
    return;
  }

  if (!last_test_time) {
    LOG_DEBUG() << "Driver does not have previous test"
                << LogExtra({{"uniq_driver_id", uniq_driver_id}}) << log_extra;
    if (driver_test_info.working_time_no_rest >= max_work_after_long_rest) {
      driver_test_info.test_type = GetTestType(experiments, log_extra);
      driver_test_info.test_required = true;
    }
    return;
  }

  if (blocked_till) {
    LOG_DEBUG() << "Driver was or is blocked"
                << LogExtra({{"uniq_driver_id", uniq_driver_id}}) << log_extra;
    utils::TimePoint unblocked = std::max(
        blocked_till.get(), driver_test_info.start_work_norest_timepoint);
    if (now - unblocked >= max_work_after_long_rest) {
      driver_test_info.test_type = GetTestType(experiments, log_extra);
      driver_test_info.test_required = true;
    }
    return;
  }

  if (driver_test_info.start_work_norest_timepoint > last_test_time.get()) {
    LOG_DEBUG() << "Driver had a long rest after last test"
                << LogExtra({{"uniq_driver_id", uniq_driver_id}}) << log_extra;
    if (driver_test_info.working_time_no_rest >= max_work_after_long_rest) {
      driver_test_info.test_type = GetTestType(experiments, log_extra);
      driver_test_info.test_required = true;
    }
    return;
  }

  if (now - last_test_time.get() >= max_work_after_test) {
    LOG_DEBUG() << "Driver worked long time after last test"
                << LogExtra({{"uniq_driver_id", uniq_driver_id}}) << log_extra;
    driver_test_info.test_type = GetTestType(experiments, log_extra);
    driver_test_info.test_required = true;
  }
  return;
}

models::ReactionTestsIndex ReadReactionTestsFromDb(
    const mongo::dbstatus_histrory::Collections& collections,
    const LogExtra& log_extra) {
  LOG_INFO() << "Read started" << log_extra;

  mongo::BSONObj query_obj;
  mongo::Query query(query_obj);
  query.readPref(mongo::ReadPreference_SecondaryPreferred,
                 utils::mongo::empty_arr);

  auto cursor = collections.reaction_tests.find(query);

  models::ReactionTestsIndex result;
  try {
    while (cursor.more()) {
      const mongo::BSONObj& doc = cursor.nextSafe();
      try {
        models::ReactionTestInfo info(doc);
        auto it = result.find(info.uniq_driver_id);
        if (it != result.end() && info.created < it->second.created) {
          continue;
        }
        result[info.uniq_driver_id] = std::move(info);
      } catch (const utils::helpers::JsonParseError& exc) {
        LOG_ERROR() << "Failed to parse reaction test: " << exc.what()
                    << log_extra;
      }
    }
  } catch (const std::exception& exc) {
    LOG_ERROR() << "Failed to read reaction tests: " << exc.what() << log_extra;
    throw;
  }

  LOG_INFO() << "Reaction tests read finished"
             << LogExtra({{"total", result.size()}}) << log_extra;
  return result;
}

ReactionTestsInfo CalculateReactionTests(
    const models::StatusHistoryIndex& status_history_idx,
    const models::ReactionTestsIndex& reaction_tests_map,
    const models::UniqueDrivers& unique_drivers,
    const models::Drivers& drivers_cache, const models::Parks& parks,
    const experiments::DriverExperiments& driver_experiments,
    const config::ReactionTests& reaction_tests_config,
    const models::ApiOverDataDeps& api_over_data_deps,
    handlers::Context& context) {
  ReactionTestsInfo ret;
  std::size_t failed_get_uniq_driver_count = 0;
  std::size_t failed_get_taxi_driver_count = 0;
  std::size_t failed_get_driver_count = 0;
  std::size_t failed_get_park_count = 0;
  std::size_t test_unfinished = 0;
  std::size_t disabled_in_city = 0;
  std::size_t disabled_by_experiments = 0;

  const auto& now = utils::datetime::Now();
  const auto& status_history_map = status_history_idx.Get();
  for (const auto& item : status_history_map) {
    const auto& driver_id = item.first;
    const auto& statuses = item.second;

    const auto& drivers = drivers_cache.GetDriversByClidUuid(driver_id);
    if (drivers.empty()) {
      LOG_WARNING() << "Failed get driver for driver id " << driver_id
                    << context.log_extra;
      failed_get_driver_count++;
      continue;
    }

    const auto& taxi_driver =
        models::GetTaxiDriver(drivers_cache, api_over_data_deps, driver_id);
    if (!taxi_driver) {
      LOG_DEBUG() << "Failed to find taxi driver for driver id"
                  << context.log_extra << LogExtra({{"driver_id", driver_id}});
      failed_get_taxi_driver_count++;
      continue;
    }

    const auto& experiments = driver_experiments.Get(
        driver_id, drivers.at(0).park_id, taxi_driver->taximeter_version);
    if (!experiments.count(kReactionTestSchulte) &&
        !experiments.count(kReactionTestGopher)) {
      LOG_DEBUG() << "Reaction tests disabled by experiments for driver"
                  << context.log_extra << LogExtra({{"driver_id", driver_id}});
      disabled_by_experiments++;
      continue;
    }

    const auto& park = models::GetTaxiPark(parks, taxi_driver->clid);
    boost::optional<std::string> city;
    if (!park) {
      LOG_WARNING() << "Failed to get taxi park for clid" << context.log_extra
                    << LogExtra({{"clid", taxi_driver->clid}});
      failed_get_park_count++;
    } else {
      city = park->city;
    }

    bool enabled_for_city =
        reaction_tests_config.reaction_tests_enabled_by_city.Get(city);
    if (!enabled_for_city) {
      LogExtra extra;
      if (city) {
        extra = LogExtra({{"city", city.get()}});
      }
      LOG_DEBUG() << "Reaction tests disabled in city" << extra
                  << context.log_extra;
      disabled_in_city++;
      continue;
    }

    const auto& uniq_driver =
        unique_drivers.GetByLicense(taxi_driver->driver_license);
    if (!uniq_driver) {
      LOG_WARNING() << "Failed to find uniq driver id for license "
                    << context.log_extra
                    << LogExtra(
                           {{"driver_license", taxi_driver->driver_license}});
      failed_get_uniq_driver_count++;
      continue;
    }

    DriverTestInfo driver_test_info =
        GetOrCreateTestInfo(ret, uniq_driver->id, driver_id, city, context);

    if (driver_test_info.test_required) {
      LOG_INFO() << "Test already scheduled for driver" << context.log_extra
                 << LogExtra({{"uniq_driver_id", uniq_driver->id}});
      continue;
    }

    boost::optional<utils::TimePoint> last_test_time = boost::none;
    boost::optional<utils::TimePoint> blocked_till = boost::none;

    auto it = reaction_tests_map.find(uniq_driver->id);
    if (it != reaction_tests_map.end()) {
      if (!it->second.passed) {
        LOG_DEBUG() << "Driver already have unfinished test"
                    << context.log_extra
                    << LogExtra({{"uniq_driver_id", uniq_driver->id}});
        test_unfinished++;
        continue;
      }
      last_test_time = it->second.updated;
      if (it->second.blocked_till) {
        blocked_till = it->second.blocked_till.get();
      }
    }
    try {
      UpdateDriverTestInfo(driver_test_info, statuses, now, city, driver_id,
                           uniq_driver->id, last_test_time, blocked_till,
                           reaction_tests_config, experiments,
                           context.log_extra);
      ret.driver_test_map[uniq_driver->id] = std::move(driver_test_info);
    } catch (const std::exception& e) {
      LOG_ERROR() << "Error on updating driver test info: " << e.what()
                  << LogExtra({{"uniq_driver_id", uniq_driver->id}})
                  << context.log_extra;
    }
  }

  context.log_extra.Extend(
      {{"failed_to_get_uniq_driver", failed_get_uniq_driver_count}});
  context.log_extra.Extend(
      {{"failed_to_get_taxi_driver", failed_get_taxi_driver_count}});
  context.log_extra.Extend({{"failed_to_get_driver", failed_get_driver_count}});
  context.log_extra.Extend({{"failed_to_get_park", failed_get_park_count}});
  context.log_extra.Extend({{"test_unfinished", test_unfinished}});
  context.log_extra.Extend({{"disabled_in_city", disabled_in_city}});
  context.log_extra.Extend(
      {{"disabled_by_experiments", disabled_by_experiments}});

  return ret;
}

mongo::BSONObj CreateReactionTestObj(const utils::TimePoint& now,
                                     const std::string& driver_id,
                                     const DriverTestInfo& driver_test_info) {
  mongo::BSONObjBuilder builder;

  builder.append(names::kCreated, utils::mongo::Date(now));
  builder.append(names::kUpdated, utils::mongo::Date(now));
  builder.append(names::kType,
                 models::ReactionTestTypeToString(driver_test_info.test_type));
  builder.append(names::kUniqueDriverId, driver_id);

  return builder.obj();
}

void StoreDataToDb(const ReactionTestsInfo& driver_result,
                   const mongo::dbstatus_histrory::Collections& collections,
                   const config::ReactionTests& config,
                   handlers::Context& context) {
  std::size_t upserted_count = 0;
  std::size_t inserted_count = 0;
  std::size_t modified_count = 0;
  std::size_t skipped_count = 0;
  std::size_t write_err_count = 0;
  std::size_t write_err_concern_count = 0;
  const auto& driver_test_map = driver_result.driver_test_map;
  auto& log_extra = context.log_extra;

  for (auto driver_it = driver_test_map.begin();
       driver_it != driver_test_map.end();) {
    auto bulk = collections.reaction_tests.UnorderedBulk();
    auto now = utils::datetime::Now();
    int size = 0;
    for (size = 0; size < kBulkSize && driver_it != driver_test_map.end();
         ++driver_it) {
      const auto& driver_test_info = driver_it->second;
      const auto& driver_id_str = driver_it->first;

      // TODO add stats like in driver_weariness

      if (!driver_test_info.test_required) {
        LOG_DEBUG() << "Do not need to create test for driver"
                    << LogExtra({{"uniq_driver_id", driver_id_str}})
                    << log_extra;
        ++skipped_count;
        continue;
      }

      const auto& obj =
          CreateReactionTestObj(now, driver_id_str, driver_test_info);
      LOG_DEBUG() << "Adding new reaction test obj" << obj;
      bulk.insert(obj);
      ++size;
    }

    // Execute operations
    mongo::WriteResult result;
    try {
      if (config.reaction_tests_write_to_db_enabled.Get() && size != 0) {
        bulk.execute(&mongo::WriteConcern::acknowledged, &result);
      }
    } catch (const mongo::DBException& exc) {
      LOG_ERROR() << "Error during bulk insert to the "
                  << "status_history.reaction_tests"  // names::kCollection
                  << " collection. DBException: " << exc.toString()
                  << log_extra;
    }
    if (result.hasErrors()) {
      for (const auto& err : result.writeErrors()) {
        LOG_ERROR() << "status_history.reaction_tests"  // names::kCollection
                    << " write error " << err << log_extra;
        ++write_err_count;
      }
      for (const auto& err : result.writeConcernErrors()) {
        LOG_ERROR() << "status_history.reaction_tests"  // names::kCollection
                    << " write concern error" << err << log_extra;
        ++write_err_concern_count;
      }
    }
    LOG_DEBUG() << "status_history.reaction_tests"  // names::kCollection
                << " upserted=" << result.nUpserted()
                << ", inserted=" << result.nInserted() << log_extra;
    inserted_count += result.nInserted();
    upserted_count += result.nUpserted();
    modified_count += result.nModified();
  }

  log_extra.Extend({{"all", driver_test_map.size()},
                    {"inserted", inserted_count},
                    {"upserted", upserted_count},
                    {"skipped", skipped_count},
                    {"modified", modified_count},
                    {"write_err", write_err_count},
                    {"write_concern_err", write_err_concern_count}});
}

}  //  namespace

const uint32_t ReactionTestsCalculator::kPeriodMs;
const uint32_t ReactionTestsCalculator::kLockTimeoutMs;
const uint32_t ReactionTestsCalculator::kLockProlongMs;

void ReactionTestsCalculator::onLoad() {
  Configure({name, std::chrono::milliseconds(kPeriodMs),
             std::chrono::milliseconds(kLockTimeoutMs),
             std::chrono::milliseconds(kLockProlongMs)});

  fastcgi::ComponentContext* const ctx = context();

  const caches::Component::CPtr caches(ctx);
  collections_.Accept(ctx);
  driver_experiments_ = &caches->GetProvider<experiments::DriverExperiments>();
  parks_cache_ = &caches->GetProvider<models::Parks>();
  drivers_cache_ = &caches->GetProvider<models::Drivers>();
  unique_drivers_cache_ = &caches->GetProvider<models::UniqueDrivers>();
  status_history_cache_ = &caches->GetProvider<models::StatusHistoryIndex>();
  driver_info_ =
      &caches->GetProvider<api_over_data::models::labor::DriverInfo>();

  BaseUnique::onLoad();
}

void ReactionTestsCalculator::onUnload() {
  BaseUnique::onUnload();

  collections_.Release();
  status_history_cache_ = nullptr;
  unique_drivers_cache_ = nullptr;
  parks_cache_ = nullptr;
  driver_experiments_ = nullptr;
  drivers_cache_ = nullptr;
  driver_info_ = nullptr;
}

void ReactionTestsCalculator::Run(const utils::AsyncStatus& status,
                                  handlers::Context& context,
                                  TimeStorage& ts) const {
  const auto& status_history = status_history_cache_->Get();
  const auto& unique_drivers = unique_drivers_cache_->Get();
  const auto& drivers = drivers_cache_->Get();
  const auto& parks = parks_cache_->Get();
  const auto& driver_experiments = driver_experiments_->Get();
  const auto& driver_info = driver_info_->Get();

  models::ApiOverDataDeps api_over_data_deps{*driver_info, ts};

  const auto& reaction_tests_config =
      context.config.Get<config::ReactionTests>();
  if (!reaction_tests_config.reaction_tests_enabled.Get()) {
    LOG_INFO() << "reaction tests disabled by config" << context.log_extra;
    return;
  }

  if (status.interrupted()) {
    return;
  }

  ScopeTime perf_st(ts);
  perf_st.Reset("read_reaction_tests_from_db");
  const auto& reaction_tests = ReadReactionTestsFromDb(
      collections_->status_history(), context.log_extra);

  perf_st.Reset("calculate_reaction_tests");
  const auto& calc_result = CalculateReactionTests(
      *status_history, reaction_tests, *unique_drivers, *drivers, *parks,
      *driver_experiments, reaction_tests_config, api_over_data_deps, context);

  if (status.interrupted()) {
    return;
  }

  perf_st.Reset("store_reaction_tests");
  StoreDataToDb(calc_result, collections_->status_history(),
                reaction_tests_config, context);
  LOG_INFO() << "Successfully finish updating reaction tests"
             << context.log_extra;
}

}  // namespace workers
