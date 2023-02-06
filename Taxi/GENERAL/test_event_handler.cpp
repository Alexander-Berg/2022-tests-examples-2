#include "test_event_handler.hpp"

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/storages/postgres/exceptions.hpp>
#include <userver/testsuite/testpoint.hpp>

namespace events = ::grocery_event_bus::models::topics;

namespace grocery_dispatch_tracking::components {
TestEventHandler::TestEventHandler(const ::components::ComponentConfig& cfg,
                                   const ::components::ComponentContext& ctx)
    : LogbrokerEventHandlerWithConfig<TestEventHandler>{cfg, ctx},
      producer_{ctx.FindComponent<grocery_event_bus::components::Producers>()},
      testsuite_tasks_(
          ctx.FindComponent<testsuite_tasks::TestsuiteTasksComponent>()) {
  StartBulkConsuming<events::test_bulk_event::Event>();
  StartBulkConsuming<events::test_protobuf_event::Event>();
  StartConsuming<events::test_event::Event>();
}

void TestEventHandler::HandleEvent(events::test_event::Event event) {
  auto builder = formats::json::ValueBuilder{};
  builder["event"] = event;
  TESTPOINT("test_event", builder.ExtractValue());

  producer_.PublishAndForget(event);

  TESTPOINT_CALLBACK(
      "retry_inject_error_event", formats::json::Value{},
      [](const formats::json::Value& obj) {
        if (obj.IsObject() && obj["is_inject_error"].As<bool>()) {
          throw grocery_event_bus::errors::RetryableError{"Injected error"};
        }
      });
}

void TestEventHandler::HandleBulkEvent(
    std::vector<grocery_event_bus::models::topics::test_bulk_event::Event>
        event_bulk) {
  formats::json::ValueBuilder builder(formats::json::Type::kArray);
  for (const auto& event : event_bulk) builder.PushBack(event);
  TESTPOINT("test_bulk_event", builder.ExtractValue());

  TESTPOINT_CALLBACK(
      "retry_inject_error_bulk_event", formats::json::Value{},
      [](const formats::json::Value& obj) {
        if (obj.IsObject() && obj["is_inject_error"].As<bool>()) {
          throw grocery_event_bus::errors::RetryableError{"Injected error"};
        }
      });
}

void TestEventHandler::HandleBulkEvent(
    std::vector<grocery_event_bus::models::topics::test_protobuf_event::Event>
        event_bulk) {
  formats::json::ValueBuilder builder(formats::json::Type::kArray);
  for (const auto& event : event_bulk) {
    builder.PushBack(event.Utf8DebugString().ConstRef());
    producer_.PublishAndForget(event);
  }
  TESTPOINT("test_protobuf_event", builder.ExtractValue());
}

}  // namespace grocery_dispatch_tracking::components
