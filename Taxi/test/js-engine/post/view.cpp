#include "view.hpp"

#include <fmt/format.h>

#include <userver/tracing/scope_time.hpp>

#include <components/js_engine.hpp>
#include <models/js_engine/script.hpp>

#include <handlers/dependencies.hpp>

using grocery_pro_bdu::models::js_engine::Script;

namespace handlers::driver_v1_grocery_pro_bdu_v1_test_js_engine::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  tracing::ScopeTime scope_time{
      fmt::format("test_js_engine_handler_bench-{}", request.body.task_name)};
  Response200 response;
  response.result.extra = dependencies.js_engine.Execute(
      request.body.task_name, Script::Create(std::move(request.body.code)),
      Script::Create(std::move(request.body.json_template)),
      std::move(request.body.user_data.extra), request.body.init,
      request.body.main);
  response.duration = scope_time.DurationTotal();
  return response;
}

}  // namespace handlers::driver_v1_grocery_pro_bdu_v1_test_js_engine::post
