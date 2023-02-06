#include "tests_control.hpp"
#include <handler_util/errors.hpp>
#include <logging/logger.hpp>
#include <tests_control/tests_control_handler.hpp>
#include <utils/helpers/params.hpp>

namespace handlers {
namespace service {

void TestsControlHandler::onLoad() {
  ContextBase::onLoad();
  cron_.Accept(context());
  psql_.Accept(context());
}

void TestsControlHandler::onUnload() {
  psql_.Release();
  cron_.Release();
  ContextBase::onUnload();
}

std::string TestsControlHandler::HandleRequestThrow(
    fastcgi::Request&, const std::string& request_body,
    handlers::Context& context) const {
  utils::helpers::Params params(request_body);
  std::string task_name;
  params.Fetch(task_name, "task_name");
  try {
    cron_->Run(task_name, context.log_extra);
    return std::string();
  } catch (const std::exception& exp) {
    LOG_ERROR() << "exc_info: " << exp.what() << context.log_extra;
    throw;
  }
}

}  // namespace service
}  // namespace handlers
