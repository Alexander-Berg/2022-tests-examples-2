#pragma once

#include <string>
#include <unordered_map>

#include <userver/components/component_config.hpp>
#include <userver/components/component_context.hpp>
#include <userver/concurrent/variable.hpp>
#include <userver/engine/shared_mutex.hpp>
#include <userver/formats/bson/document.hpp>
#include <userver/server/handlers/http_handler_base.hpp>

namespace stq_dispatcher::components {
class StqTaskInterface;
}  // namespace stq_dispatcher::components

namespace stq_dispatcher::handlers {

class TestsuiteSupport : public server::handlers::HttpHandlerBase {
 public:
  using Task = stq_dispatcher::components::StqTaskInterface;

  using server::handlers::HttpHandlerBase::HttpHandlerBase;

  static constexpr const char* kName = "handler-testsuite-stq";

  std::string HandleRequestThrow(
      const server::http::HttpRequest&,
      server::request::RequestContext&) const override;

  void RegisterQueueHandler(std::string queue_name, const Task& task);

  void UnregisterQueueHandler(const std::string& queue_name);

 private:
  using QueuesMap = std::unordered_map<std::string, const Task&>;
  concurrent::Variable<QueuesMap, engine::SharedMutex> queues_;
};

}  // namespace stq_dispatcher::handlers
