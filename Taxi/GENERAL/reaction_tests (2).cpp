#include "reaction_tests.hpp"

#include <mongo/names/reaction_tests.hpp>
#include <utils/helpers/params.hpp>

namespace models {
namespace names = utils::mongo::db::StatusHistory::ReactionTests;

namespace {

static const std::map<std::string, ReactionTestStatus> string_to_status{
    {"timed_out", ReactionTestStatus::TimedOut},
    {"finished_on_errors", ReactionTestStatus::FinishedOnErrors},
    {"finished_on_restart", ReactionTestStatus::FinishedOnRestart},
    {"success", ReactionTestStatus::Success},
};

static const std::map<ReactionTestStatus, std::string> status_to_string{
    {ReactionTestStatus::TimedOut, "timed_out"},
    {ReactionTestStatus::FinishedOnErrors, "finished_on_errors"},
    {ReactionTestStatus::FinishedOnRestart, "finished_on_restart"},
    {ReactionTestStatus::Success, "success"},
};

static const std::map<std::string, ReactionTestType> string_to_type{
    {"schulte", ReactionTestType::Schulte},
    {"gopher", ReactionTestType::Gopher},
};

static const std::map<ReactionTestType, std::string> type_to_string{
    {ReactionTestType::Schulte, "schulte"},
    {ReactionTestType::Gopher, "gopher"},
};

}  // namespace

ReactionTestStatus ReactionTestStatusFromString(const std::string& status) {
  auto it = string_to_status.find(status);
  if (it == string_to_status.end()) {
    throw std::runtime_error("unknown_status_string");
  }
  return it->second;
}

std::string ReactionTestStatusToString(const ReactionTestStatus& status) {
  auto it = status_to_string.find(status);
  if (it == status_to_string.end()) {
    throw std::runtime_error("unknown_status");
  }
  return it->second;
}

ReactionTestType ReactionTestTypeFromString(const std::string& type) {
  auto it = string_to_type.find(type);
  if (it == string_to_type.end()) {
    throw std::runtime_error("unknown_type_string");
  }
  return it->second;
}

std::string ReactionTestTypeToString(const ReactionTestType& type) {
  auto it = type_to_string.find(type);
  if (it == type_to_string.end()) {
    throw std::runtime_error("unknown_type");
  }
  return it->second;
}

ReactionTestClick::ReactionTestClick() {}

ReactionTestClick::ReactionTestClick(const mongo::BSONObj& doc) {
  utils::helpers::FetchMember(is_hit, doc, names::kIsHit);
  utils::helpers::FetchMember(delay_ms, doc, names::kDelayMs);
}

ReactionTestResult::ReactionTestResult() {}

ReactionTestResult::ReactionTestResult(const mongo::BSONObj& doc) {
  utils::helpers::FetchMember(total_time_ms, doc, names::kTotalTimeMs);
  std::string status_str;
  utils::helpers::FetchMember(status_str, doc, names::kStatus);
  status = ReactionTestStatusFromString(status_str);

  const auto& click_objs = utils::helpers::FetchArray(doc, names::kClicks);
  for (const auto& click_obj : click_objs) {
    clicks.emplace_back(ReactionTestClick(click_obj.Obj()));
  }
}

ReactionTestInfo::ReactionTestInfo() {}

ReactionTestInfo::ReactionTestInfo(const mongo::BSONObj& doc) {
  utils::helpers::FetchMember(id, doc, names::kId);
  utils::helpers::FetchMember(type, doc, names::kType);
  utils::helpers::FetchMember(uniq_driver_id, doc, names::kUniqueDriverId);
  utils::helpers::FetchMember(passed, doc, names::kPassed);
  utils::helpers::FetchMember(blocked_till, doc, names::kBlockedTill);
  utils::helpers::FetchMember(created, doc, names::kCreated);
  utils::helpers::FetchMember(updated, doc, names::kUpdated);

  const auto& results_objs =
      utils::helpers::FetchArrayOptional(doc, names::kResults);
  for (const auto& result_obj : results_objs) {
    results.emplace_back(ReactionTestResult(result_obj.Obj()));
  }
}

}  // namespace models
