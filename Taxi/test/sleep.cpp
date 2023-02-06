#include <candidates/filters/test/sleep.hpp>

#include <candidates/filters/test/sleep_info.hpp>
#include <candidates/filters/test/sleep_params.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

namespace candidates::filters::test {

const FilterData<Sleep, Sleep::TaskPtr> Sleep::task_data_("task");

Sleep::Sleep(const FilterInfo& info, const std::chrono::milliseconds duration)
    : Filter(info), duration_(duration) {}

Result Sleep::Process(const GeoMember&, Context& context) const {
  // Use shared_ptr to store move-only TaskWithResult in std::any, because
  // it supports only CopyConstructible types
  auto task = task_data_.Get(context, {});
  if (!task) {
    task = std::make_shared<Task>(utils::Async(
        name(), [d = duration_] { engine::InterruptibleSleepFor(d); }));
    task_data_.Set(context, task);
  }
  return task->IsFinished() ? Result::kAllow : Result::kRepeat;
}

bool Sleep::IsFinished(const Context& context) {
  const auto task = task_data_.Get(context, {});
  return task && task->IsFinished();
}

SleepFactory::SleepFactory() : Factory(info::kSleep) {}

std::unique_ptr<Filter> SleepFactory::Create(
    const formats::json::Value& params,
    [[maybe_unused]] const FactoryEnvironment& env) const {
  const auto& fparams = params.As<sleep::Params>();
  if (!fparams.sleep_ms) return {};

  if (*fparams.sleep_ms > std::chrono::milliseconds::zero())
    return std::make_unique<Sleep>(info(), *fparams.sleep_ms);

  return {};
}

}  // namespace candidates::filters::test
