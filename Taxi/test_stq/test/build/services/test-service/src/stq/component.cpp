#include <stq/component.hpp>

#include <userver/components/component.hpp>

#include <clients/stq-agent/component.hpp>
#include <components/stq_agent.hpp>

#include <stq/client.hpp>

#include <stq/client/queues.hpp>

namespace stq {
namespace {
std::shared_ptr<StqQueues> MakeQueues(
    const ::components::ComponentContext& context) {
  return std::make_shared<StqQueues>(
      context.FindComponent<clients::stq_agent::deprecated::Component>()
          .GetClient(),
      context.FindComponent<clients::stq_agent::Component>().GetClient());
}
}  // namespace

Component::Component(const ::components::ComponentConfig& config,
                     const ::components::ComponentContext& context)
    : LoggableComponentBase(config, context),
      stq_queues_(MakeQueues(context))
{}

std::shared_ptr<StqQueues> Component::GetQueues() const { return stq_queues_; }

}  // namespace stq
