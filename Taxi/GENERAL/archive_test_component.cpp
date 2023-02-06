#include <trackstory/components/archive_test_component.hpp>

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/formats/json/serialize_container.hpp>
#include <userver/logging/log.hpp>
#include <userver/testsuite/testpoint.hpp>

namespace trackstory::components {

namespace {

const std::string kCreateTasks = "create_tasks";
const std::string kExecuteTasks = "execute_tasks";

}  // namespace

TestArchiveComponent::TestArchiveComponent(
    const ::components::ComponentConfig& config,
    const ::components::ComponentContext& component_context)
    : server::handlers::HttpHandlerJsonBase(config, component_context),
      archive_task_creator_(
          component_context.FindComponent<ArchiveTaskCreator>()),
      archive_task_executor_(
          component_context.FindComponent<ArchiveTaskExecutor>()),
      archive_consumer_component_(
          component_context.FindComponent<ArchiveConsumerComponent>()) {}

const std::string& TestArchiveComponent::HandlerName() const {
  static const std::string kHandlerName = kName;
  return kHandlerName;
}

formats::json::Value TestArchiveComponent::HandleRequestJsonThrow(
    const server::http::HttpRequest& /*request*/,
    const formats::json::Value& request_body,
    server::request::RequestContext& /*context*/) const {
  auto action = request_body["action"].As<std::string>();

  if (action == kCreateTasks) {
    archive_task_creator_.RunOnce();

    formats::json::ValueBuilder builder;
    builder["test"] = "test";
    TESTPOINT("logbroker_commit", builder.ExtractValue());
  } else if (action == kExecuteTasks) {
    /// TODO(melon-aerial): get this data from handler if we will decide to
    /// write this tests.
    {
      std::string topic = "some_topic";
      std::string data = "some_data";

      logbroker_consumer::Offset offset;
      logbroker_consumer::Message::TimePoint create_time, write_time;
      auto partition = 0;
      std::string source_id = "";
      uint64_t seq_no = 0;

      auto message = std::make_unique<logbroker_consumer::Message>(
          std::move(data), std::move(topic), create_time, write_time, offset,
          partition, source_id, seq_no, [] {
            TESTPOINT("logbroker_commit",
                      formats::json::ValueBuilder("test").ExtractValue());
          });
      archive_consumer_component_.PushMessageDebug(std::move(message));
    }

    archive_task_executor_.RunOnce();
  } else {
    LOG_ERROR() << "Unknown action for tests : " << action;
    throw std::runtime_error("Unknown action");
  }

  return {};
}

}  // namespace trackstory::components
