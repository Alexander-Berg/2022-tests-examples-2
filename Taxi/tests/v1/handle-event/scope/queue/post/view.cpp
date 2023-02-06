#include "view.hpp"

namespace handlers::tests_v1_handle_event_scope_queue::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const processing::models::ItemLocator item_locator{
      request.scope, request.queue, request.item_id};
  formats::json::Value current_state, prev_state;
  if (request.body.current_state) {
    current_state = request.body.current_state->extra;
  }
  if (request.body.prev_state) {
    prev_state = request.body.prev_state->extra;
  }
  auto queue_locator = processing::models::QueueLocator(item_locator);
  const auto& data =
      dependencies.extra.processing_ng.LocateQueue(queue_locator);
  std::optional<std::string> stage_id;
  std::optional<formats::json::Value> initial_state;
  if (auto stage = request.body.stage) {
    stage_id = stage->id;
    initial_state = std::move(stage->shared_state.extra);
  }
  auto final_state = data.queue.processor_.HandleSingleEvent(
      item_locator, request.body.event.extra, current_state, prev_state,
      request.body.pipeline, stage_id, initial_state, data.DynamicConfig(),
      data.DynamicQosConfig(), data.Config(), data.queue.stats_counters_);
  handlers::SharedState response;
  response.extra = std::move(final_state);
  return Response200{response};
}

}  // namespace handlers::tests_v1_handle_event_scope_queue::post
