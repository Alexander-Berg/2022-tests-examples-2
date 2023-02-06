#pragma once

#include <libplatform/libplatform.h>

#include <userver/utest/utest.hpp>

#include <userver/utils/scope_guard.hpp>

#include <js/component.hpp>
#include <js/execution/component.hpp>

#include <js-pipeline/execution/object_wrapper.hpp>

#include "../../common.hpp"

namespace js_pipeline::testing {

using namespace js::execution;
using JsComponent = js::Component;
using JsExecutionComponent = js::execution::Component;

constexpr const auto kWorkerThreadsCount = 4;
constexpr const std::chrono::milliseconds kTimeout{100000};

struct JSTest : public ::testing::Test {
  struct GlobalTestingContext {
    std::shared_ptr<::v8::Platform> platform;

    GlobalTestingContext() : platform(JsComponent::Initialize()) {}
    ~GlobalTestingContext() {
      JsComponent::Shutdown();
      platform.reset();
    }
  };

  struct TestingContext {
    engine::SingleThreadedTaskProcessorsPool pool;
    js::execution::TaskQueue::ProducerPtr task_queue_producer;
    js::execution::TaskQueue::ConsumerPtr task_queue_consumer;

    TestingContext(int worker_threads_count = kWorkerThreadsCount)
        : pool(engine::SingleThreadedTaskProcessorsPool::MakeForTests(
              worker_threads_count)),
          task_queue_producer(nullptr),
          task_queue_consumer(nullptr) {
      auto queue = js::execution::TaskQueue::Create(worker_threads_count);

      task_queue_producer = queue->GetProducer();
      task_queue_consumer = queue->GetConsumer();
    }
  };

  JSTest() {
    // disposing from V8 is permanent and process has to be restarted to use V8
    // again, so we manage its lifetime in static object
    static GlobalTestingContext global_testing_context;
  }

  // forward private members
  using WorkerTasks = JsExecutionComponent::WorkerTasks;

  static JsExecutionComponent::WorkerTasks Start(TestingContext& context) {
    return JsExecutionComponent::Start(
        context.pool, std::move(context.task_queue_consumer), nullptr, nullptr);
  }

  template <typename Result>
  static auto Execute(TestingContext& context, TaskPtr task) {
    return JsExecutionComponent::Execute<Result>(*context.task_queue_producer,
                                                 std::move(task), {});
  }

  static void WaitForCompletion(
      JsExecutionComponent::WorkerTasks& worker_tasks) {
    return JsExecutionComponent::WaitForCompletion(worker_tasks);
  }

  template <typename Fn>
  static void RunInV8(Fn&& fn, int worker_threads_count = kWorkerThreadsCount) {
    RunInCoro([fn = std::forward<Fn>(fn), worker_threads_count] {
      TestingContext context(worker_threads_count);
      WorkerTasks worker_tasks = Start(context);

      utils::ScopeGuard guard([&worker_tasks, &context] {
        context.task_queue_producer.reset();
        WaitForCompletion(worker_tasks);
      });

      fn(context);
    });
  }
};

struct TestingTask : public Task {
  static inline const std::string kName = "testing_task";

  std::string script;

  TestingTask(const std::string& script)
      : script(ReadResource("common.js") + script) {}

  const std::string* GetScript() const override { return &script; }
  const std::string& GetName() const override { return kName; }
};

}  // namespace js_pipeline::testing
