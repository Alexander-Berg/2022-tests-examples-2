#pragma once

#include <trackstory/components/archive_consumer_component.hpp>
#include <trackstory/components/archive_task_creator.hpp>
#include <trackstory/components/archive_task_executor.hpp>

#include <userver/components/loggable_component_base.hpp>
#include <userver/server/handlers/http_handler_json_base.hpp>

namespace trackstory::components {

/// Component with test handlers to test ArchiveTaskExecutor and
/// ArchiveTaskCreator components.
class TestArchiveComponent final
    : public server::handlers::HttpHandlerJsonBase {
 public:
  TestArchiveComponent(const ::components::ComponentConfig& config,
                       const ::components::ComponentContext& component_context);

  static constexpr const char* kName = "test-archive-component";

  const std::string& HandlerName() const override;

  formats::json::Value HandleRequestJsonThrow(
      const server::http::HttpRequest& request,
      const formats::json::Value& request_body,
      server::request::RequestContext& context) const override;

 private:
  ArchiveTaskCreator& archive_task_creator_;
  ArchiveTaskExecutor& archive_task_executor_;
  ArchiveConsumerComponent& archive_consumer_component_;
};

}  // namespace trackstory::components
