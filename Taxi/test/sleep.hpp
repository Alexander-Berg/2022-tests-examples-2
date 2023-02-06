#pragma once

#include <chrono>

#include <userver/engine/task/task_with_result.hpp>
#include <userver/utils/async.hpp>

#include <candidates/filters/context_data.hpp>
#include <candidates/filters/filter.hpp>

namespace candidates::filters::test {

class Sleep : public Filter {
 public:
  Sleep(const FilterInfo& info, const std::chrono::milliseconds duration);

  Result Process(const GeoMember&, Context& context) const override;

  // just for test
  static bool IsFinished(const Context& context);

 private:
  const std::chrono::milliseconds duration_;

  using Task = engine::TaskWithResult<void>;
  using TaskPtr = std::shared_ptr<Task>;

  static const FilterData<Sleep, TaskPtr> task_data_;
};

class SleepFactory : public Factory {
 public:
  SleepFactory();

  std::unique_ptr<Filter> Create(const formats::json::Value& params,
                                 const FactoryEnvironment&) const override;
};

}  // namespace candidates::filters::test
