#pragma once

#include <boost/optional.hpp>
#include <config/configfwd.hpp>
#include <logging/log_extra.hpp>
#include <models/reaction_tests.hpp>
#include <mongo/mongo.hpp>
#include <mongo/pool.hpp>
#include <string>
#include <utils/prof.hpp>
#include <utils/types.hpp>
#include <vector>

namespace views {
namespace reaction_tests {

struct Request {
  mongo::OID test_id;
  models::ReactionTestType test_type;
  std::vector<models::ReactionTestResult> results;
};

struct ValidationInfo {
  bool passed;
  boost::optional<utils::TimePoint> blocked_till;
};

ValidationInfo ProcessResult(const Request& request,
                             const std::string& unique_driver_id,
                             const utils::mongo::PoolPtr& status_history,
                             const config::Config& config,
                             const LogExtra& log_extra, TimeStorage& ts);
}  // namespace reaction_tests
}  // namespace views
