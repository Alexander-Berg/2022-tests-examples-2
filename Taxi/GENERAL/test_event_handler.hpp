#pragma once

#include <testsuite-tasks/component.hpp>
#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/components/loggable_component_base.hpp>

#include <grocery-event-bus/components/producers.hpp>
#include <grocery-event-bus/models/topics/test-bulk-event.hpp>
#include <grocery-event-bus/models/topics/test-event.hpp>
#include <grocery-event-bus/models/topics/test-protobuf-event.hpp>

#include <grocery-event-bus/components/logbroker_event_handler_with_config.hpp>

namespace grocery_dispatch_tracking::components {

class TestEventHandler
    : public grocery_event_bus::components::LogbrokerEventHandlerWithConfig<
          TestEventHandler> {
 public:
  constexpr static const char* kName = "test-event-handler";

  TestEventHandler(const ::components::ComponentConfig&,
                   const ::components::ComponentContext&);

  /// Test event handler
  void HandleEvent(grocery_event_bus::models::topics::test_event::Event event);
  /// Test bulk event handler
  void HandleBulkEvent(
      std::vector<grocery_event_bus::models::topics::test_bulk_event::Event>);

  void HandleBulkEvent(
      std::vector<
          grocery_event_bus::models::topics::test_protobuf_event::Event>);

 private:
  grocery_event_bus::components::Producers& producer_;
  testsuite_tasks::TestsuiteTasksComponent& testsuite_tasks_;
};
}  // namespace grocery_dispatch_tracking::components
