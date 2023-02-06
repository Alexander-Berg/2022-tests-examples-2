#include "view.hpp"

#include <userver/formats/bson/value_builder.hpp>

#include <stq/client/queues.hpp>

namespace handlers::stq_create_task::post {
Response View::Handle(Request&& request, Dependencies&& deps) {
  Response200 response;

  if (!request.queue || request.queue.value() == Queue::kSampleQueueWithArgs) {
    stq_clients::sample_queue_with_args::Args args{};
    args.task_id = request.body;
    args.optional_arg = 42;
    deps.stq->sample_queue_with_args.Call("internal id", args);
  } else if (request.queue.value() == Queue::kSampleQueue) {
    formats::bson::ValueBuilder builder;
    builder.PushBack(request.body);
    const auto& args = builder.ExtractValue();
    deps.stq->sample_queue.Call("internal id", args);
  } else {
    throw std::runtime_error("Invalid queue name");
  }

  return response;
}
}  // namespace handlers::stq_create_task::post
