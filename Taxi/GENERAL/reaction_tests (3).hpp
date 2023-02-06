#pragma once

#include <string>

namespace utils {
namespace mongo {
namespace db {
namespace StatusHistory {
namespace ReactionTests {

static const std::string kCollection = "dbstatus_history.reaction_tests";

static const std::string kId = "_id";
static const std::string kCreated = "created";
static const std::string kUpdated = "updated";
static const std::string kUniqueDriverId = "unique_driver_id";
static const std::string kType = "type";

static const std::string kResults = "results";
static const std::string kPassed = "passed";
static const std::string kBlockedTill = "blocked_till";

static const std::string kStatus = "status";
static const std::string kTotalTimeMs = "total_time_ms";
static const std::string kClicks = "clicks";

static const std::string kIsHit = "is_hit";
static const std::string kDelayMs = "delay_ms";

}  // namespace ReactionTests
}  // namespace StatusHistory
}  // namespace db
}  // namespace mongo
}  // namespace utils
