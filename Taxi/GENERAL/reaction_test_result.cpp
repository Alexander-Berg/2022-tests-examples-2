#include "reaction_test_result.hpp"

#include <fastcgi2/request.h>
#include <limits>

#include <cache/caches_component.hpp>
#include <handlers/helpers_driver_protocol.hpp>
#include <mongo/mongo_component.hpp>
#include <utils/helpers/driver.hpp>
#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>

#include "views/reaction_test_result.hpp"

namespace handlers {
namespace driver {
namespace {

void ValidateTime(const std::string& name,
                  const std::chrono::milliseconds& time) {
  const auto& count = time.count();
  if (count < 0 || count > std::numeric_limits<int>::max()) {
    throw BadRequest("Invalid " + name);
  }
}

views::reaction_tests::Request ParseRequest(
    const std::string& request_body,
    const AuthorizedDriverBase::Context& context) {
  views::reaction_tests::Request request;
  try {
    utils::helpers::Params params(request_body);
    std::string test_id;
    params.Fetch(test_id, "id");
    try {
      request.test_id = mongo::OID(test_id);
    } catch (const std::exception& e) {
      LOG_WARNING() << "Failed to parse test id: " << e.what()
                    << context.log_extra;
      throw BadRequest("Invalid test_id");
    }
    std::string type;
    params.Fetch(type, "type");
    try {
      request.test_type = models::ReactionTestTypeFromString(type);
    } catch (const std::exception& e) {
      LOG_WARNING() << "Failed to parse test type: " << e.what()
                    << context.log_extra;
      throw BadRequest("Invalid type");
    }
    const auto& results_obj = params.FetchArray<Json::Value>("results");
    request.results.reserve(results_obj.size());
    for (const auto& result_obj : results_obj) {
      utils::helpers::Params result_params(result_obj);
      models::ReactionTestResult result;
      result_params.Fetch(result.total_time_ms, "total_time_ms");
      ValidateTime("total_time_ms", result.total_time_ms);
      std::string status;
      result_params.Fetch(status, "status");
      try {
        result.status = models::ReactionTestStatusFromString(status);
      } catch (const std::exception& e) {
        LOG_WARNING() << "Failed to parse test status: " << e.what()
                      << context.log_extra;
        throw BadRequest("Invalid status");
      }
      const auto& clicks_obj = result_params.FetchArray<Json::Value>("clicks");
      result.clicks.reserve(clicks_obj.size());
      for (const auto& click_obj : clicks_obj) {
        models::ReactionTestClick click;
        utils::helpers::Params click_params(click_obj);
        click_params.Fetch(click.is_hit, "is_hit");
        click_params.Fetch(click.delay_ms, "delay_ms");
        ValidateTime("delay_ms", click.delay_ms);
        result.clicks.emplace_back(std::move(click));
      }
      request.results.emplace_back(std::move(result));
    }
  } catch (const utils::helpers::JsonParseError& e) {
    LOG_WARNING() << "Failed to parse Json: " << request_body
                  << " error: " << e.what() << context.log_extra;
    throw BadRequest("Invalid json");
  }
  return request;
}
}  // namespace

void ReactionTestResult::onLoad() {
  AuthorizedDriverBase::onLoad();
  const caches::Component::CPtr caches(context());
  unique_drivers_ = &caches->GetProvider<models::UniqueDrivers>();
  status_history_ = ::components::GetComponentRefByName<MongoComponent>(
                        *context(), "mongo-status-history")
                        .GetPool();
}

void ReactionTestResult::onUnload() {
  status_history_.reset();
  unique_drivers_ = nullptr;
  AuthorizedDriverBase::onUnload();
}

std::string ReactionTestResult::HandleRequestThrow(
    fastcgi::Request& /*request*/, const std::string& request_body,
    Context& context, TimeStorage& ts) const {
  const auto& unique_drivers = unique_drivers_->Get();
  const auto& drivers_info_ptr = drivers_info_->Get();

  auto driver_data = drivers_info_ptr->GetDriver(
      context.park_db_id, context.driver_id, context.log_extra);

  boost::optional<models::UniqueDriver> unique_driver =
      unique_drivers->GetByLicensePdId(driver_data.license_pd_id);
  if (!unique_driver) {
    LOG_WARNING() << models::UniqueDrivers::GetLicenseNotFoundLogMessage(
                         driver_data.license_pd_id)
                  << context.log_extra;
    throw BadRequest("Invalid driver");
  }

  const auto& input = ParseRequest(request_body, context);

  const auto& verification_info = views::reaction_tests::ProcessResult(
      input, unique_driver->id, status_history_, context.config,
      context.log_extra, ts);

  Json::Value resp_json;
  resp_json["passed"] = verification_info.passed;

  return utils::helpers::WriteJson(resp_json);
}

}  // namespace driver
}  // namespace handlers
