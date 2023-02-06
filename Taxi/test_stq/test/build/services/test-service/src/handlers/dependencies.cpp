/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

#include <stq/component.hpp>

#include <handlers/dependencies.hpp>
#include <userver/components/component.hpp>
#include <userver/components/statistics_storage.hpp>
#include <userver/concurrent/background_task_storage.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/storage/component.hpp>

namespace handlers {

DependenciesFactory::DependenciesFactory(
    [[maybe_unused]] const components::ComponentConfig& config,
    const components::ComponentContext& context)
    : config_source_(
          context.FindComponent<components::DynamicConfig>().GetSource()),
      metrics_storage_(context.FindComponent<components::StatisticsStorage>()
                           .GetMetricsStorage()),
      bts_(),
      custom_dependencies_(config, context),
      stq_(context.FindComponent<stq::Component>().GetQueues())

{}

DependenciesFactory::~DependenciesFactory() { bts_->CancelAndWait(); }

Dependencies DependenciesFactory::GetDependencies() const {
  return Dependencies{
      config_source_.GetSnapshot(),
      metrics_storage_,
      *bts_,
      custom_dependencies_.GetExtra(),
      stq_,
  };
}

}  // namespace handlers