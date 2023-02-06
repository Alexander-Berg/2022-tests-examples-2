#include "test.hpp"

#include <cstdint>
#include <string>

#include <clients/stq_clients.hpp>
#include <configs/experiments3.hpp>
#include <experiments3_common/models/kwargs.hpp>
#include <handler_util/errors.hpp>
#include <models/experiments3.hpp>
#include <mongo/wrappers.hpp>
#include <secdist/secdist_component.hpp>
#include <utils/application.hpp>
#include <utils/experiments3/ping.hpp>
#include <utils/helpers/args.hpp>
#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>
#include <utils/http.hpp>
#include <utils/optional.hpp>
#include <utils/prof.hpp>
#include <utils/request.hpp>
#include "components/caches.hpp"
#include "components/clients.hpp"

namespace handlers {

void TestHandler::onLoad() {
  handlers::BaseExp3Handler::onLoad();

  const components::Caches::CPtr caches(context());

  experiments3_cache_ =
      &caches->GetProvider<experiments3::models::CacheManager>();
}

void TestHandler::onUnload() {
  experiments3_cache_ = nullptr;
  handlers::BaseExp3Handler::onUnload();
}

void TestHandler::Handle(fastcgi::Request& /* request*/,
                         ::handlers::BaseContext& base_context) {
  const std::string& request_body = base_context.request_body;
  const auto& request_json =
      utils::helpers::ParseJsonRequest(request_body, base_context.log_extra);
  std::string task_id;
  utils::helpers::FetchMember(task_id, request_json, "task_id");
  const auto& config_ptr = config_->Get();
  const auto& tvm2_ptr = tvm2_component_->Get();
  const auto& exp3_cfg = config_ptr->Get<config::Experiments3>();
  const auto& cache_manager = experiments3_cache_->Get();

  handlers::Context context2(*config_ptr, *graphite_, tvm2_ptr,
                             base_context.log_extra);
  experiments3::utils::CheckMandatoryConfigsLoad(
      exp3_cfg.mandatory_configs_switch.Get(), exp3_cfg.max_config_time.Get(),
      *cache_manager, base_context.log_extra);
  Json::Value response_json(Json::objectValue);
  response_json["status"] = "ok";
  base_context.response = utils::helpers::WriteStyledJson(response_json);

  const auto& stq = clients_->Get<clients::StqClients>()->GetStq();
  const auto& stq_client = stq.experiments3_test;

  stq_client.Call(task_id, context2);
}

}  // namespace handlers
