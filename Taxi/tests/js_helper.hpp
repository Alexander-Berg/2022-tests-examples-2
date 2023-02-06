#pragma once

#include <libplatform/libplatform.h>

#include <fmt/format.h>
#include <boost/logic/tribool.hpp>

#include <atomic>
#include <functional>
#include <set>

#include <userver/engine/run_in_coro.hpp>
#include <userver/engine/single_consumer_event.hpp>
#include <userver/engine/task/single_threaded_task_processors_pool.hpp>
#include <userver/utils/assert.hpp>
#include <userver/utils/scope_guard.hpp>

#include <js/component.hpp>
#include <js/errors.hpp>
#include <js/execution/component.hpp>
#include <js/execution/internal/statistics.hpp>

namespace js::testing {

using namespace js::execution;
using JsComponent = js::Component;
using JsExecutionComponent = js::execution::Component;

constexpr const uint16_t kWorkerThreadsCount = 4;

template <typename... Mixins>
struct TestingTaskBase : public TaskInterface<Mixins...> {
  static inline const std::string kName = "testing_task";

  std::string script;

  TestingTaskBase(std::string code)
      : script(R"(
    let check_number = 1;

    function check(exp, act) {
      let num = check_number++;
      if (exp !== act) {
        throw 'check #' + num + ' failed; expected: ' + exp + '; got: ' + act;
      }
    }
    )") {
    script += code;
  }

  const std::string* GetScript() const override { return &script; }
  const std::string& GetName() const override { return kName; }
};

using TestingTask = TestingTaskBase<RegularExecution>;
using TestingGeneratorTask = TestingTaskBase<GeneratorExecution>;
using TestingWrappedGeneratorTask = TestingTaskBase<WrappedGeneratorExecution>;

struct Helper {
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
    TaskQueue::ProducerPtr task_queue_producer;
    TaskQueue::ConsumerPtr task_queue_consumer;
    StatisticsByTaskPtr stats_by_task_name;

    TestingContext(uint16_t worker_threads_count = kWorkerThreadsCount)
        : pool(engine::SingleThreadedTaskProcessorsPool::MakeForTests(
              worker_threads_count)),
          task_queue_producer(nullptr),
          task_queue_consumer(nullptr),
          stats_by_task_name(std::make_shared<StatisticsByTask>()) {
      // NOTE: Has to be created before any v8::Isolate
      // disposing from V8 is permanent and process has to be restarted to use
      // V8 again, so we manage its lifetime in static object
      static GlobalTestingContext global_testing_context;

      auto queue = TaskQueue::Create(worker_threads_count,
                                     TaskQueue::PushMode::kBlocking);

      task_queue_producer = queue->GetProducer();
      task_queue_consumer = queue->GetConsumer();
    }
  };

  // forward private members
  using WorkerTasks = JsExecutionComponent::WorkerTasks;

  static WorkerTasks Start(TestingContext& context) {
    return JsExecutionComponent::Start(context.pool,
                                       std::move(context.task_queue_consumer),
                                       context.stats_by_task_name, nullptr);
  }

  template <typename Result>
  static ChannelOut<Result> Execute(TestingContext& context, TaskPtr task,
                                    channel::Settings channel_settings = {}) {
    return JsExecutionComponent::Execute<Result>(
        *context.task_queue_producer, std::move(task), channel_settings);
  }

  static void WaitForCompletion(WorkerTasks& worker_tasks) {
    return JsExecutionComponent::WaitForCompletion(worker_tasks);
  }

  template <typename Fn>
  static void RunInV8(Fn&& fn, int worker_threads_count = kWorkerThreadsCount) {
    RunInCoro([fn = std::forward<Fn>(fn), worker_threads_count]() mutable {
      TestingContext context(worker_threads_count);
      WorkerTasks worker_tasks = Start(context);

      utils::ScopeGuard guard([&worker_tasks, &context] {
        context.task_queue_producer.reset();
        WaitForCompletion(worker_tasks);
      });

      fn(context);
    });
  }

  struct Task : public TestingTask {
    using Base = TestingTask;
    using ExecuteImpl = std::function<void()>;

    ExecuteImpl execute_impl;

    Task(ExecuteImpl execute_impl)
        : Base(""), execute_impl(std::move(execute_impl)) {}

    v8::Local<v8::Value> Execute(
        const ::js::execution::AsyncPublicContext&) const override {
      execute_impl();
      return js::New(true);
    }
  };

  template <typename Fn>
  static void ExecuteInV8(Fn&& execute_impl, uint16_t worker_count = 1) {
    RunInV8(
        [execute_impl =
             std::forward<Fn>(execute_impl)](TestingContext& context) mutable {
          UASSERT(Execute<bool>(context, std::make_unique<Task>(
                                             std::forward<Fn>(execute_impl)))
                      .Get({}));
        },
        worker_count);
  }
};

struct CommonTaskData {
  std::shared_ptr<const int> a;  // persistent external resource
};

template <typename Execution>
struct TestingCachableTaskBase : public TaskInterface<Execution, MemoryCaching>,
                                 public CommonTaskData {
  static inline const std::string kName = "testing_cachable_task";

  std::string script;
  logging::LogExtra log_extra;

  static inline std::atomic_size_t init_count = 0;

  TestingCachableTaskBase(std::shared_ptr<const int> a, std::string script)
      : CommonTaskData{a}, script(std::move(script)) {}

  const std::string* GetScript() const override { return &script; }
  const std::string& GetName() const override { return kName; }
  NativeResourceCacheEntryPtr GetResourceCacheEntry() const override {
    struct TestingCacheEntry : public NativeResourceCacheEntry {
      std::weak_ptr<const int> resource_w_ptr;

      TestingCacheEntry(std::shared_ptr<const int> resource)
          : resource_w_ptr(resource) {}

      Key GetId() const override {
        auto locked = resource_w_ptr.lock();
        UASSERT(locked);
        return locked.get();
      }

      bool IsExpired() const override { return resource_w_ptr.expired(); }
    };

    return std::make_unique<const TestingCacheEntry>(a);
  }

  void InitializeState() const override { ++init_count; }
};

using TestingCachableTask = TestingCachableTaskBase<RegularExecution>;

template <typename Execution>
struct TestingStableCachableTaskBase
    : public TaskInterface<Execution, StableCaching>,
      public CommonTaskData {
  static inline const std::string kName = "testing_cachable_task";

  struct CacheParameters {
    std::optional<std::string> slot_id;
    std::string instance_id;
    std::chrono::seconds cache_max_unused_time;
  };

  CacheParameters cache_params;
  std::string script;
  logging::LogExtra log_extra;

  static inline std::atomic_size_t init_count = 0;

  TestingStableCachableTaskBase(std::shared_ptr<const int> a,
                                CacheParameters cache_params,
                                std::string script)
      : CommonTaskData{a},
        cache_params(std::move(cache_params)),
        script(std::move(script)) {}

  const std::string* GetScript() const override { return &script; }
  const std::string& GetName() const override { return kName; }
  StableNativeResourceCacheEntryPtr GetResourceCacheEntry() const override {
    struct TestingCacheEntry : public StableNativeResourceCacheEntry {
      CacheParameters cache_params;

      TestingCacheEntry(CacheParameters cache_params)
          : cache_params(std::move(cache_params)) {}

      std::optional<std::string> GetSlotId() const override {
        return cache_params.slot_id;
      }
      const std::string& GetInstanceId() const override {
        return cache_params.instance_id;
      }
      std::chrono::seconds GetMaxUnusedTime() const override {
        return cache_params.cache_max_unused_time;
      }
    };

    return std::make_unique<const TestingCacheEntry>(cache_params);
  }

  void InitializeState() const override { ++init_count; }
};

using TestingStableCachableTask =
    TestingStableCachableTaskBase<RegularExecution>;

template <template <typename> class _Base>
struct TestingCachableAsyncTaskBase : public _Base<WrappedAsyncAwaitExecution> {
  using Base = _Base<WrappedAsyncAwaitExecution>;
  using GetC = std::function<int(int)>;

  engine::TaskProcessor& async_task_processor;
  GetC get_c;

  template <typename... BaseArgs>
  TestingCachableAsyncTaskBase(GetC get_c, BaseArgs&&... base_args)
      : Base(std::forward<BaseArgs>(base_args)...),
        async_task_processor(engine::current_task::GetTaskProcessor()),
        get_c(get_c) {}

  engine::TaskProcessor& GetAsyncTaskProcessor() const override {
    return async_task_processor;
  }

  /**
   * @brief Will be called once to get root promise
   */
  v8::Local<v8::Promise> GetPromise(const AsyncPublicContext&) const override {
    return js::As<v8::Promise>(js::CallGlobal(
        js::FromContext<v8::Function>("test"), js::New(*CommonTaskData::a)));
  }

  void InitializeState() const override {
    Base::InitializeState();

    auto v8_context = js::GetCurrentContext();
    auto global = v8_context->Global();

    js::SetWithContext set{&v8_context};

    set(global, "async_fn",
        WrappedAsyncAwaitExecution::NewAsyncFunction([get_c = get_c](int b) {
          auto c = get_c(b);

          if (c < 0) {
            throw std::runtime_error("c is negative!");
          }

          return b + c;
        }));

    set(global, "async_undefined_fn",
        WrappedAsyncAwaitExecution::NewAsyncFunction(
            []([[maybe_unused]] int b) { return; }));
  }
};

using TestingCachableAsyncTask =
    TestingCachableAsyncTaskBase<TestingCachableTaskBase>;
using TestingStableCachableAsyncTask =
    TestingCachableAsyncTaskBase<TestingStableCachableTaskBase>;

}  // namespace js::testing
