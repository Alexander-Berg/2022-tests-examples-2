
#include "stq/components/test.hpp"

#include <bitset>
#include <userver/components/component.hpp>
#include <userver/logging/log.hpp>
#include <userver/tracing/span.hpp>

#include <boost/algorithm/string/join.hpp>

#include <handlers/dependencies.hpp>
#include <stq-dispatcher/components/stq_dispatcher.hpp>

#include <stq/tasks/test.hpp>

namespace stq_tasks::test {
Test::Test(const components::ComponentConfig& config,
           const components::ComponentContext& context)
    : stq_dispatcher::components::StqTaskBase::StqTaskBase(config, context),
      deps_factory_(
          std::make_unique<handlers::DependenciesFactory>(config, context))
{
  auto queue_name = config["queue_name"].As<std::string>();
  auto& dispatcher =
      context.FindComponent<stq_dispatcher::components::StqDispatcher>();
  dispatcher.RegisterQueueHandler(std::move(queue_name), *this);
}

Test::~Test() = default;

void Test::Perform(const stq_dispatcher::models::VariantTaskData& task) const {
  handlers::Dependencies dependencies = deps_factory_->GetDependencies();
  auto args_struct = ParseArgs(std::get<formats::json::Value>(task.args),
                               std::get<formats::json::Value>(task.kwargs));

  auto task_parsed =
      TaskDataParsed{task.id,  task.exec_tries,        task.reschedule_counter,
                     task.eta, std::move(args_struct), task.tag};
  stq_tasks::test::Performer::Perform(std::move(task_parsed),
                                      std::move(dependencies));
}

bool Test::ParseArgsAsJson() const { return true; }

namespace args {
const std::vector<std::string> kArgsList = {"simple_string", "array",
                                            "optional_number", "object_field",
                                            "datetime_field"};
}  // namespace args

Args Test::ParseArgs(const formats::json::Value& args,
                     const formats::json::Value& kwargs) const {
  if (!args.IsArray()) {
    throw InvalidArgumentsError{"Args must be an array"};
  }
  if (!kwargs.IsObject()) {
    throw InvalidArgumentsError{"Kwargs must be an object"};
  }
  auto scope =
      tracing::Span::CurrentSpan().CreateScopeTime("stq_task_parse_args");
  formats::json::ValueBuilder new_kwargs(kwargs);
  const auto known_args_number = args::kArgsList.size();
  if (args.GetSize() > known_args_number) {
    throw InvalidArgumentsError{
        "Not all args were used during parsing, found " +
        std::to_string(args.GetSize() - known_args_number) + " extra arg(s)"};
  }
  for (size_t args_used = 0; args_used < args.GetSize(); args_used++) {
    const auto& arg_name = args::kArgsList[args_used];
    if (kwargs.HasMember(arg_name)) {
      throw InvalidArgumentsError{"Kwargs seem to be duplicating args: " +
                                  arg_name};
    }
    new_kwargs[arg_name] = args[args_used];
  }
  auto value = new_kwargs.ExtractValue();
  return value.As<Args>();
}

}  // namespace stq_tasks::test
