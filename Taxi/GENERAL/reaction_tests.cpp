#include "reaction_tests.hpp"

#include <logging/logger.hpp>
#include <mongo/mongo.hpp>
#include <mongo/mongo_component.hpp>
#include <mongo/names/reaction_tests.hpp>
#include <mongo/wrappers.hpp>
#include <threads/async.hpp>
#include <utils/constants.hpp>
#include <utils/helpers/params.hpp>

namespace caches {

constexpr std::chrono::minutes ReactionTests::kUpdateInterval;
constexpr std::chrono::minutes ReactionTests::kCleanUpdateInterval;
constexpr std::chrono::seconds ReactionTests::kLastUpdateCorrection;

namespace names = utils::mongo::db::StatusHistory::ReactionTests;

ReactionTests::ReactionTests(const utils::mongo::PoolPtr& connection_pool)
    : PartiallyBase(kName, kUpdateInterval, kLastUpdateCorrection,
                    kCleanUpdateInterval),
      connection_pool_(connection_pool) {}

ReactionTests::DataPtr ReactionTests::UpdatePartially(
    TimePoint /*now*/, TimePoint from, const utils::AsyncStatus& status,
    TimeStorage& ts, LogExtra& log_extra) const {
  LOG_INFO() << "Reaction tests update started" << log_extra;
  const bool clean = IsClean(from);
  mongo::BSONObjBuilder query_builder;
  if (!clean) {
    query_builder.append(names::kUpdated,
                         mongo::BSONObjBuilder()
                             .appendDate("$gte", utils::mongo::Date(from))
                             .obj());
  }

  mongo::Query query(query_builder.obj());
  query.readPref(mongo::ReadPreference_SecondaryPreferred,
                 utils::mongo::empty_arr);

  utils::mongo::CollectionWrapper collection(connection_pool_,
                                             names::kCollection);
  auto cursor = collection.find(query);

  if (!clean && !cursor.more()) return nullptr;

  const auto& data = CreateData(clean, ts);
  size_t new_count = 0;
  try {
    while (cursor.more()) {
      const mongo::BSONObj& doc = cursor.nextSafe();

      if (status.interrupted()) return nullptr;

      try {
        models::ReactionTestInfo info(doc);
        auto it = data->find(info.uniq_driver_id);
        if (it != data->end() && info.created < it->second.created) {
          // old test found
          continue;
        }
        (*data)[info.uniq_driver_id] = std::move(info);
        ++new_count;
      } catch (const utils::helpers::JsonParseError& exc) {
        LOG_ERROR() << "Failed to parse reaction test: " << exc.what()
                    << log_extra;
      }
    }
  } catch (const std::exception& exc) {
    LOG_ERROR() << "Failed to update reaction tests: " << exc.what()
                << log_extra;
    throw;
  }

  LOG_INFO() << "Reaction tests updated"
             << LogExtra({{"total", data->size()}, {"new", new_count}})
             << log_extra;
  return data;
}

}  // namespace caches
