#pragma once

#include <mongo/bson/bson.h>
#include <mongo/mongo.hpp>
#include <string>
#include <unordered_map>
#include <utils/types.hpp>

namespace models {

enum class ReactionTestStatus {
  TimedOut,
  FinishedOnErrors,
  FinishedOnRestart,
  Success
};

enum class ReactionTestType { Schulte, Gopher };

ReactionTestStatus ReactionTestStatusFromString(const std::string& status);
std::string ReactionTestStatusToString(const ReactionTestStatus& status);

ReactionTestType ReactionTestTypeFromString(const std::string& type);
std::string ReactionTestTypeToString(const ReactionTestType& type);

struct ReactionTestClick {
  ReactionTestClick(const mongo::BSONObj& doc);
  ReactionTestClick();

  bool is_hit = false;
  std::chrono::milliseconds delay_ms;
};

struct ReactionTestResult {
  ReactionTestResult(const mongo::BSONObj& doc);
  ReactionTestResult();

  std::chrono::milliseconds total_time_ms;
  ReactionTestStatus status{};
  std::vector<ReactionTestClick> clicks;
};

struct ReactionTestInfo {
  ReactionTestInfo(const mongo::BSONObj& doc);
  ReactionTestInfo();

  mongo::OID id;
  std::string type;
  std::string uniq_driver_id;
  std::vector<ReactionTestResult> results;
  boost::optional<bool> passed;
  boost::optional<utils::TimePoint> blocked_till;
  utils::TimePoint created;
  utils::TimePoint updated;
};

using ReactionTestsIndex = std::unordered_map<std::string, ReactionTestInfo>;

}  // namespace  models
