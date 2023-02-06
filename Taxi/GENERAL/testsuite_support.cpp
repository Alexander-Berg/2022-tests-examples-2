#include <stq-dispatcher/handlers/testsuite_support.hpp>

#include <utility>

#include <userver/formats/bson.hpp>
#include <userver/formats/bson/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/logging/log.hpp>

#include <stq-dispatcher/components/stq_task_base.hpp>
#include <stq-dispatcher/models/task.hpp>

namespace stq_dispatcher::handlers {

namespace {

class ParseRequestError : public std::runtime_error {
  using runtime_error::runtime_error;
};

struct TaskInfo {
  std::string queue_name;
  stq_dispatcher::models::VariantTaskData task;
};

TaskInfo ParseRequest(const std::string& request_body) {
  namespace bson = formats::bson;
  bson::Document request_bson;
  try {
    request_bson = bson::FromJsonString(request_body);
  } catch (const bson::ConversionException& exc) {
    throw ParseRequestError(exc.what());
  }
  auto task_info = TaskInfo{};
  try {
    auto task_id = request_bson["task_id"].As<std::string>();
    auto task_tag = request_bson["tag"].As<std::optional<std::string>>();
    task_info.queue_name = request_bson["queue_name"].As<std::string>();
    task_info.task = {
        task_id,
        request_bson["exec_tries"].As<int>(0),
        request_bson["reschedule_counter"].As<int>(0),
        request_bson["eta"].As<std::chrono::system_clock::time_point>(
            std::chrono::system_clock::now()),
        request_bson["args"],
        request_bson["kwargs"],
        task_tag};
  } catch (const bson::BsonException& exc) {
    throw ParseRequestError(exc.what());
  }
  return task_info;
}

std::pair<formats::json::Value, formats::json::Value> ParseTaskArgumentsAsJson(
    const std::string& request_body) {
  namespace json = formats::json;
  json::Value request_json;
  try {
    request_json = json::FromString(request_body);
  } catch (const json::ConversionException& exc) {
    throw ParseRequestError(exc.what());
  }
  auto task_info = TaskInfo{};
  try {
    return std::make_pair(request_json["args"], request_json["kwargs"]);
  } catch (const json::Exception& exc) {
    throw ParseRequestError(exc.what());
  }
}

}  // namespace

void TestsuiteSupport::RegisterQueueHandler(std::string queue_name,
                                            const Task& task) {
  auto locked_queues = queues_.Lock();
  locked_queues->emplace(queue_name, task);
  LOG_INFO() << "Registered queue " << queue_name << " for testsuite";
}

void TestsuiteSupport::UnregisterQueueHandler(const std::string& queue_name) {
  auto locked_queues = queues_.Lock();
  locked_queues->erase(queue_name);
  LOG_INFO() << "Unregistered queue " << queue_name << " for testsuite";
}

std::string TestsuiteSupport::HandleRequestThrow(
    const server::http::HttpRequest& request,
    [[maybe_unused]] server::request::RequestContext& context) const {
  TaskInfo task_info;
  const auto& request_body = request.RequestBody();
  try {
    task_info = ParseRequest(request_body);
  } catch (const ParseRequestError& exc) {
    throw ClientError(InternalMessage{exc.what()}, ExternalBody{exc.what()});
  }
  auto locked_queues = queues_.SharedLock();
  auto handler_it = locked_queues->find(task_info.queue_name);
  if (handler_it == locked_queues->end()) {
    auto msg = "No handler registered for queue " + task_info.queue_name;
    throw server::handlers::ResourceNotFound(InternalMessage{msg},
                                             ExternalBody{msg});
  }
  if (handler_it->second.ParseArgsAsJson()) {
    try {
      auto task_arguments = ParseTaskArgumentsAsJson(request_body);
      task_info.task.args = task_arguments.first;
      task_info.task.kwargs = task_arguments.second;
    } catch (const ParseRequestError& exc) {
      throw ClientError(InternalMessage{exc.what()}, ExternalBody{exc.what()});
    }
  }
  bool failed = false;
  try {
    handler_it->second.Perform(std::move(task_info.task));
  } catch (const std::exception& exc) {
    LOG_WARNING() << "Stq task failed: " << exc;
    failed = true;
  }
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  builder["failed"] = failed;
  return formats::json::ToString(builder.ExtractValue());
}

}  // namespace stq_dispatcher::handlers
