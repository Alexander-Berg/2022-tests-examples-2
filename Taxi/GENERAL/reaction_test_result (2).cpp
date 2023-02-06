#include "reaction_test_result.hpp"

#include <models/reaction_tests.hpp>
#include <mongo/mongo.hpp>
#include <mongo/names/reaction_tests.hpp>
#include <mongo/wrappers.hpp>

#include "config/config.hpp"
#include "config/reaction_tests_config.hpp"

namespace views {
namespace reaction_tests {
namespace {
namespace names = utils::mongo::db::StatusHistory::ReactionTests;

ValidationInfo ValidateSchulteSimple(const Request& request,
                                     const config::Config& config,
                                     const LogExtra& log_extra) {
  const config::ReactionTests& tests_config =
      config.Get<config::ReactionTests>();
  std::chrono::milliseconds total_time_ms(0);
  int count = 0;
  for (const auto& r : request.results) {
    if (r.status == models::ReactionTestStatus::Success) {
      total_time_ms += r.total_time_ms;
      count++;
    }
  }
  ValidationInfo result;
  result.passed = false;
  if (count == 0 ||
      count < tests_config.schulte_result_table_count_limit.Get()) {
    LOG_INFO() << "Not enough successful tables in result, test failed"
               << log_extra;
    return result;
  }
  std::chrono::milliseconds average = total_time_ms / count;
  if (average <= tests_config.schulte_result_average_limit_ms.Get()) {
    result.passed = true;
  } else {
    LOG_INFO() << "Average time is too big, test failed" << log_extra;
  }
  return result;
}

ValidationInfo ValidateResult(
    const Request& request,
    const std::vector<models::ReactionTestInfo>& /*tests*/,
    const config::Config& config, const LogExtra& log_extra) {
  if (request.test_type == models::ReactionTestType::Schulte) {
    return ValidateSchulteSimple(request, config, log_extra);
  }
  LOG_WARNING() << "Unhandled test type, assume test failed" << log_extra;
  ValidationInfo result;
  result.passed = false;
  return result;
}

void WriteToDb(const Request& request, const std::string& unique_driver_id,
               const ValidationInfo& info,
               const utils::mongo::CollectionWrapper& collection,
               const LogExtra& log_extra) {
  mongo::BSONObjBuilder query_builder;
  query_builder.append(names::kId, request.test_id);
  query_builder.append(names::kUniqueDriverId, unique_driver_id);
  query_builder.append(names::kType,
                       models::ReactionTestTypeToString(request.test_type));
  query_builder.append(names::kResults, BSON("$exists" << false));

  mongo::BSONObjBuilder update_builder;
  mongo::BSONObjBuilder set_builder(update_builder.subobjStart("$set"));
  set_builder.append(names::kPassed, info.passed);
  if (info.blocked_till) {
    set_builder.append(names::kBlockedTill,
                       utils::mongo::Date(info.blocked_till.get()));
  }
  mongo::BSONArrayBuilder results_obj(
      set_builder.subarrayStart(names::kResults));
  for (const auto& result : request.results) {
    mongo::BSONObjBuilder result_builder;
    int total_time = result.total_time_ms.count();
    result_builder.append(names::kTotalTimeMs, total_time);
    result_builder.append(names::kStatus,
                          models::ReactionTestStatusToString(result.status));
    mongo::BSONArrayBuilder clicks_obj(
        result_builder.subarrayStart(names::kClicks));
    for (const auto& click : result.clicks) {
      mongo::BSONObjBuilder click_builder;
      click_builder.append(names::kIsHit, click.is_hit);
      int delay = click.delay_ms.count();
      click_builder.append(names::kDelayMs, delay);
      clicks_obj.append(click_builder.obj());
    }
    clicks_obj.done();
    results_obj.append(result_builder.obj());
  }
  results_obj.done();
  set_builder.done();
  mongo::BSONObjBuilder date_builder(
      update_builder.subobjStart("$currentDate"));
  date_builder.append(names::kUpdated, true);
  date_builder.done();
  const auto& query = query_builder.obj();
  const auto& update = update_builder.obj();

  const auto& result = collection.findAndModify(query, update, false, true);
  if (result.isEmpty()) {
    LOG_WARNING() << "Failed to update test in db" << log_extra
                  << LogExtra({{"query", query.toString()},
                               {"update", update.toString()}});
  }
}

std::vector<models::ReactionTestInfo> FetchDriverTests(
    const utils::mongo::CollectionWrapper& /*collection*/,
    const std::string /*unique_driver_id*/) {
  return {};
}

}  // namespace
ValidationInfo ProcessResult(const Request& request,
                             const std::string& unique_driver_id,
                             const utils::mongo::PoolPtr& status_history,
                             const config::Config& config,
                             const LogExtra& log_extra, TimeStorage& ts) {
  utils::mongo::CollectionWrapper collection(status_history,
                                             names::kCollection);
  const auto& tests = (ScopeTime(ts, "fetch_tests"),
                       FetchDriverTests(collection, unique_driver_id));
  const auto& ret = (ScopeTime(ts, "validate_result"),
                     ValidateResult(request, tests, config, log_extra));
  (ScopeTime(ts, "write_to_db"),
   WriteToDb(request, unique_driver_id, ret, collection, log_extra));
  return ret;
}
}  // namespace reaction_tests
}  // namespace views
