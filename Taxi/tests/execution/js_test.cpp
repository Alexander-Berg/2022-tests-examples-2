#include <tests/common.hpp>

namespace js::testing {

struct JsTest : public Fixture {};

struct AddingTask : public TestingTask {
  int a, b;
  AddingTask(int a, int b)
      : TestingTask(R"(
            function add(a, b) {
              // just check that it doesn't fail
              log.info("called with a:" + a + ", b: " + b);
              return a + b;
            }
          )"),
        a(a),
        b(b) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    return scope.Escape(js::CallGlobal(js::FromContext<v8::Function>("add"),
                                       js::New(a), js::New(b)));
  }
};

TEST_F(JsTest, AsyncAwait) {
  static const auto kScript =
      "async function test(a) {"
      "  if (await async_undefined_fn(a) !== undefined) {"
      "    throw 'Supposed to be undefined!';"
      "  }"
      "  return a + await async_fn(7);"
      "}";

  const auto kTest = [](TestingContext& context) {
    engine::SingleConsumerEvent ev1, ev2;

    auto a1 = std::make_shared<const int>(1);
    auto a2 = std::make_shared<const int>(2);
    int c1 = 0, c2 = 0;

    auto ch1 = Execute<int>(context, std::make_unique<TestingCachableAsyncTask>(
                                         [&](int) {
                                           EXPECT_TRUE(ev1.WaitForEvent());
                                           return c1;
                                         },
                                         a1, kScript));

    auto ch2 = Execute<int>(context, std::make_unique<TestingCachableAsyncTask>(
                                         [&](int) {
                                           EXPECT_TRUE(ev2.WaitForEvent());
                                           return c2;
                                         },
                                         a2, kScript));

    // async tasks are sleeping...
    CheckIsSleeping(ch1);
    CheckIsSleeping(ch2);

    // ...while not interfering with another tasks
    ASSERT_EQ(
        5, Execute<int>(context, std::make_unique<AddingTask>(2, 3)).Get({}));

    // async tasks are still sleeping...
    CheckIsSleeping(ch1);
    CheckIsSleeping(ch2);

    c2 = 5;
    // ...until we complete awaited async function
    ev2.Send();

    ASSERT_EQ(/*5 + 7 + 2=*/14, ch2.Get({}));

    // first async task is still sleeping...
    ASSERT_EQ(engine::CvStatus::kTimeout, ch1.Wait(kTotal50MsTimeout));

    c1 = 10;
    // ...until we complete its awaited async function
    ev1.Send();

    ASSERT_EQ(/*10 + 7 + 1=*/18, ch1.Get({}));
  };

  RunInV8(kTest);
  RunInV8(kTest, /*worker_threads_count=*/1);
}

TEST_F(JsTest, AsyncAwaitCaching) {
  static const auto kScript =
      "async function test(a) {return a + await async_fn(7);}";

  const auto kTest = [](TestingContext& context) {
    int n = 2;
    TestingCachableAsyncTask::init_count = 0;

    auto a1 = std::make_shared<const int>(1);

    while (n--) {
      engine::SingleConsumerEvent ev1;

      int c1 = 0;

      auto ch1 =
          Execute<int>(context, std::make_unique<TestingCachableAsyncTask>(
                                    [&](int) {
                                      EXPECT_TRUE(ev1.WaitForEvent());
                                      return c1;
                                    },
                                    a1, kScript));

      c1 = 10;
      // ...until we complete its awaited async function
      ev1.Send();

      ASSERT_EQ(/*10 + 7 + 1=*/18, ch1.Get({}));
    }

    ASSERT_EQ(1, TestingCachableAsyncTask::init_count);
  };

  RunInV8(kTest, /*worker_threads_count=*/1);
}

TEST_F(JsTest, AsyncAwaitStableCaching) {
  using Task = TestingStableCachableAsyncTask;

  static const auto kScript =
      "async function test(a) {return a + await async_fn(7);}";

  const auto kTest = [](TestingContext& context) {
    int n = 2;
    Task::init_count = 0;
    Task::CacheParameters cache_params{
        /*slot_id=*/"slot_0",
        /*instance_id=*/"instance_0",
        /*cache_max_unused_time=*/kMaxSeconds,
    };

    auto a1 = std::make_shared<const int>(1);

    while (n--) {
      engine::SingleConsumerEvent ev1;

      int c1 = 0;

      auto ch1 = Execute<int>(context, std::make_unique<Task>(
                                           [&](int) {
                                             EXPECT_TRUE(ev1.WaitForEvent());
                                             return c1;
                                           },
                                           a1, cache_params, kScript));

      c1 = 10;
      // ...until we complete its awaited async function
      ev1.Send();

      ASSERT_EQ(/*10 + 7 + 1=*/18, ch1.Get({}));
    }

    ASSERT_EQ(1, Task::init_count);
  };

  RunInV8(kTest, /*worker_threads_count=*/1);
}

TEST_F(JsTest, AsyncAwaitBadArgument) {
  RunInV8([](TestingContext& context) {
    static const auto kScript =
        "async function test(a) {"
        "  return a + await async_fn(/*error: float instead of an int*/ 7.1);"
        "}";

    auto a1 = std::make_shared<const int>(1);

    auto ch1 = Execute<int>(context, std::make_unique<TestingCachableAsyncTask>(
                                         [](int) {
                                           EXPECT_TRUE(false);
                                           return 0;
                                         },
                                         a1, kScript));

    // async task will not be issued because call is invalid,
    // so whole execution becomes synchronous and no signaling is required
    ASSERT_EQ(engine::CvStatus::kNoTimeout, ch1.Wait({}));
    ASSERT_THROW_MSG_CONTAINS(ch1.Get({}), std::runtime_error,
                              "got: 'number' when a 'int32_t' was expected");
  });
}

TEST_F(JsTest, AsyncAwaitExceptions) {
  RunInV8([](TestingContext& context) {
    static const auto kScript =
        "async function test(a) {"
        "  return a + await async_fn(7);"
        "}";

    engine::SingleConsumerEvent ev1;

    auto a1 = std::make_shared<const int>(1);
    int c1 = 0;

    auto ch1 = Execute<int>(context, std::make_unique<TestingCachableAsyncTask>(
                                         [&](int) {
                                           EXPECT_TRUE(ev1.WaitForEvent());
                                           return c1;
                                         },
                                         a1, kScript));

    c1 = -1;  // trigger exception in async function
    ev1.Send();

    ASSERT_THROW_MSG_CONTAINS(ch1.Get({}), std::runtime_error,
                              "c is negative!");
  });
}

TEST_F(JsTest, AsyncAwaitCancellation) {
  RunInV8([](TestingContext& context) {
    static const auto kScript =
        "async function test(a) {"
        "  return a + await async_fn(7);"
        "}";

    engine::SingleConsumerEvent ev1;

    auto a1 = std::make_shared<const int>(1);

    auto ch1 = Execute<int>(context, std::make_unique<TestingCachableAsyncTask>(
                                         [&](int) {
                                           EXPECT_FALSE(ev1.WaitForEvent());
                                           return 0;
                                         },
                                         a1, kScript));

    ASSERT_THROW_MSG_CONTAINS(ch1.Get(kTotal50MsTimeout), std::runtime_error,
                              "timed out during async await");
  });
}

TEST_F(JsTest, AsyncAwaitAbandon) {
  RunInV8([](TestingContext& context) {
    static const auto kScript =
        "async function test(a) {"
        "  let abandoned = async_fn(0);"
        "  return a + await async_fn(1);"
        "}";

    engine::SingleConsumerEvent ev[2];
    boost::tribool ev_states[2]{boost::indeterminate, boost::indeterminate};

    auto a1 = std::make_shared<const int>(1);

    auto ch1 = Execute<int>(context, std::make_unique<TestingCachableAsyncTask>(
                                         [&](int b) {
                                           ev_states[b] = ev[b].WaitForEvent();
                                           return 10;
                                         },
                                         a1, kScript));

    // async task is sleeping...
    CheckIsSleeping(ch1);

    ev[1].Send();

    ASSERT_EQ(/*1(a1) + 1(b) + 10(c)=*/12, ch1.Get({}));

    // check that all async functions completed as expected
    ASSERT_EQ(false, ev_states[0]);
    ASSERT_EQ(true, ev_states[1]);
  });
}

TEST_F(JsTest, AsyncAwaitThen) {
  RunInV8([](TestingContext& context) {
    static const auto kScript =
        "async function test(a) {"
        "  let p0 = async_fn(0);"
        "  let p1 = p0.then(async (value) => { return value + await "
        "async_fn(1); });"
        "  let v2 = await async_fn(2);"
        "  return a + v2 + await p1;"
        "}";

    engine::SingleConsumerEvent ev[3], evr[3];

    auto a1 = std::make_shared<const int>(1);

    auto ch1 = Execute<int>(context, std::make_unique<TestingCachableAsyncTask>(
                                         [&](int b) {
                                           evr[b].Send();
                                           EXPECT_TRUE(ev[b].WaitForEvent());
                                           return 10;
                                         },
                                         a1, kScript));

    // async task is sleeping...
    CheckIsSleeping(ch1);

    ASSERT_TRUE(evr[0].WaitForEvent());
    ASSERT_FALSE(evr[1].WaitForEventFor(50ms));
    ASSERT_TRUE(evr[2].WaitForEvent());

    ev[0].Send();  // resolve p0 and trigger its .then

    ASSERT_TRUE(evr[1].WaitForEvent());

    ev[1].Send();
    ev[2].Send();

    ASSERT_EQ(/*1(a1) + 0(b) + 10(c) + 1(b) + 10(c) + 2(b) + 10(c)=*/34,
              ch1.Get({}));
  });
}

TEST_F(JsTest, AsyncAwaitMultipleDeferredAwaits) {
  RunInV8([](TestingContext& context) {
    static const auto kScript =
        "async function test(a) {"
        "  let promise1 = async_fn(7);"
        "  let promise2 = async_fn(5);"
        "  return a + await promise1 + await promise2;"
        "}";

    engine::SingleConsumerEvent ev[2];

    auto a1 = std::make_shared<const int>(1);
    int cs[2]{4, 2};

    auto ch1 = Execute<int>(context, std::make_unique<TestingCachableAsyncTask>(
                                         [&](int b) {
                                           int i = b == 7 ? 0 : 1;
                                           EXPECT_TRUE(ev[i].WaitForEvent());
                                           return cs[i];
                                         },
                                         a1, kScript));

    // async task is sleeping...
    CheckIsSleeping(ch1);

    ev[1].Send();

    // async task is sleeping...
    CheckIsSleeping(ch1);

    ev[0].Send();

    ASSERT_EQ(/*1(a1) + 5(b) + 2(cs[1]) + 7(b) + 4(cs[0])=*/19, ch1.Get({}));
  });
}

struct GeneratingTask : public TestingWrappedGeneratorTask {
  int n, throw_at;
  bool is_done = false;

  GeneratingTask(int n, int throw_at = -1)
      : TestingWrappedGeneratorTask(R"(
          function* range(n, throw_at){
            let i = 0;
            let threw = false;
            while (i < n) {
              if (threw) {
                throw "another exception";
              }

              if (i === throw_at) {
                threw = true;
                throw "exception from JS";
              }

              yield i++;
            }
            return i; // simplifies test
          }
        )"),
        n(n),
        throw_at(throw_at) {}

  v8::Local<v8::Object> GetGenerator(const AsyncPublicContext&) const override {
    UASSERT(!IsDone());

    return js::As<v8::Object>(js::CallGlobal(
        js::FromContext<v8::Function>("range"), js::New(n), js::New(throw_at)));
  }
};

struct TaskWithTimeout : public TestingTask {
  std::chrono::milliseconds sleep_for_;
  std::chrono::milliseconds timeout_;
  engine::TaskProcessor& task_processor_;

  TaskWithTimeout(engine::TaskProcessor& task_processor,
                  std::chrono::milliseconds sleep_for,
                  std::chrono::milliseconds timeout)
      : TestingTask(R"(
          function wait_for(sleep_duration) {
              var now = new Date().getTime();
              while(new Date().getTime() < now + sleep_duration){ /* do nothing */ }

              return 0xDEAD;
          }
      )"),
        sleep_for_(sleep_for),
        timeout_(timeout),
        task_processor_(task_processor) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    return js::CallWithTimeout(task_processor_, timeout_,
                               js::FromContext<v8::Function>("wait_for"),
                               js::New(sleep_for_.count()));
  }
};

struct SeveralCallsWithTimeoutTask : public TestingTask {
  engine::TaskProcessor& task_processor_;

  SeveralCallsWithTimeoutTask(engine::TaskProcessor& task_processor)
      : TestingTask(R"(
          function func_1(sleep_duration) {
              var now = new Date().getTime();
              while(new Date().getTime() < now + sleep_duration){ /* do nothing */ }

              return 0xDEAD;
          }

          function func_2() {
              return 0xBEEF;
          }
      )"),
        task_processor_(task_processor) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    auto work_time = 200ms;
    auto timeout = 100ms;

    try {
      return js::CallWithTimeout(task_processor_, timeout,
                                 js::FromContext<v8::Function>("func_1"),
                                 js::New(work_time.count()));
    } catch (const js::TerminateError&) {
    }

    return js::CallGlobal(js::FromContext<v8::Function>("func_2"));
  }
};

struct OptTask : public TestingTask {
  OptTask() : TestingTask("") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    return {};
  }
};

struct EternalRunTask : public TestingTask {
  EternalRunTask() : TestingTask(R"(while(true);)") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    return {};
  }
};

struct EternalCallTask : public TestingTask {
  EternalCallTask()
      : TestingTask(R"(
            function eternal() {
              while(true);
            })") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    return CallGlobal(FromContext<v8::Function>("eternal"));
  }
};

struct ErrorTask : public TestingTask {
  ErrorTask()
      : TestingTask(R"(
            function make_throw() {
              throw "!testing exception!";
            }
          )") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    return scope.Escape(
        js::CallGlobal(js::FromContext<v8::Function>("make_throw")));
  }
};

struct CachableWrapperTask : public TestingTask {
  struct Wrapper : public CachableJsWrapper {
    struct CacheEntry : public NativeResourceCacheEntry {
      static inline int value_gc_count = 0;

      NativeResourceCacheEntry::Key GetId() const final { return nullptr; }
      bool IsExpired() const final {
        ++value_gc_count;
        return false;
      }
    };

   private:
    struct NativeData final : public NativeDataInterface {
      mutable int build_count = 0;

      NativeResourceCacheEntryPtr GetResourceCacheEntry() const override {
        return std::make_unique<CacheEntry>();
      }

      v8::Local<v8::Value> BuildJsValue(Handle& wrapper_handle) const final {
        ++build_count;

        auto v8_context = GetCurrentContext();

        auto res = js::NewObject();
        auto o1 = js::NewObject();
        auto ok = o1->Set(v8_context, js::New("v1"), js::New(8));
        UASSERT(FromMaybe(ok));

        ok = res->Set(v8_context, js::New("o1"), o1);
        UASSERT(FromMaybe(ok));

        ok = res->Set(v8_context, js::New("get_build_count"),
                      js::New<JSGetBuildCount>(wrapper_handle));
        UASSERT(FromMaybe(ok));

        return res;
      }
    };

    static void JSGetBuildCount(const v8::FunctionCallbackInfo<v8::Value>& info,
                                Handle& wrapper_handle) {
      info.GetReturnValue().Set(wrapper_handle.As<NativeData>().build_count);
    }

   public:
    Wrapper() : CachableJsWrapper(std::make_shared<NativeData>()) {}
    const NativeData& GetData() const {
      auto casted =
          std::dynamic_pointer_cast<const NativeData>(GetNativeData());
      UASSERT(casted);
      return *casted;
    }
  };

  Wrapper& wrapper;

  explicit CachableWrapperTask(Wrapper& wrapper)
      : TestingTask(R"(
            function main(data) {
              check(8, data.o1.v1);

              return data.get_build_count();
            }
          )"),
        wrapper(wrapper) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    auto data = wrapper.AsJsValue();
    data = wrapper.AsJsValue();  // provoke excessive value cache GC
    return scope.Escape(
        js::CallGlobal(js::FromContext<v8::Function>("main"), data));
  }
};

struct AddingCachableTask : public TestingCachableTask {
  int b;
  AddingCachableTask(std::shared_ptr<const int> a, int b)
      : TestingCachableTask(a, R"(
            function add(b) {
              return a + b;   // a is global cached
            }
          )"),
        b(b) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    return scope.Escape(
        js::CallGlobal(js::FromContext<v8::Function>("add"), js::New(b)));
  }

  void InitializeState() const override {
    TestingCachableTask::InitializeState();

    v8::Local v8_context = js::GetCurrentContext();
    v8::Local global = v8_context->Global();

    js::SetWithContext set{&v8_context};

    set(global, "a", *a);
  }
};

struct AddingStableCachableTask : public TestingStableCachableTask {
  int a;  // cached
  int b;
  AddingStableCachableTask(CacheParameters cache_params, int a, int b)
      : TestingStableCachableTask(nullptr, std::move(cache_params), R"(
            function add(b) {
              return a + b;   // a is global cached
            }
          )"),
        a(a),
        b(b) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    return scope.Escape(
        js::CallGlobal(js::FromContext<v8::Function>("add"), js::New(b)));
  }

  void InitializeState() const override {
    TestingStableCachableTask::InitializeState();

    v8::Local v8_context = js::GetCurrentContext();
    v8::Local global = v8_context->Global();

    js::SetWithContext set{&v8_context};

    set(global, "a", a);
  }
};

struct MakeGlobalVarTask : public TestingTask {
  MakeGlobalVarTask()
      : TestingTask(R"(
            function main() {
              global_var = 21;
              return global_var;
            }
          )") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    return scope.Escape(js::CallGlobal(js::FromContext<v8::Function>("main")));
  }
};

struct MakeGlobalVarCachableTask : public TestingCachableTask {
  MakeGlobalVarCachableTask()
      : TestingCachableTask(std::make_shared<int>(0), R"(
            function main() {
              global_var = 1;
            }
          )") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    return scope.Escape(js::CallGlobal(js::FromContext<v8::Function>("main")));
  }
};

struct MakeOkGlobalVarCachableTask : public TestingCachableTask {
  MakeOkGlobalVarCachableTask()
      : TestingCachableTask(std::make_shared<int>(0), R"(
            function init() {
              global_var = 42;
            }

            function main() {
              return global_var;
            }
          )") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    return scope.Escape(js::CallGlobal(js::FromContext<v8::Function>("main")));
  }

  void InitializeState() const override {
    TestingCachableTask::InitializeState();

    js::CallGlobal(js::FromContext<v8::Function>("init"));
  }
};

struct ConstDataTask : public TestingTask {
  ConstDataTask()
      : TestingTask(R"(
            function main(obj) {
              let a = obj.a;
              check(0, obj.a_empty.length);
              check(1, a.length);
              check(1, a.length);

              check(10, a[0]);
              check(undefined, a[3]);

              check(1, a.length);

              try {
                obj.lol = 12;
                check(true, false);
              } catch (e) {
                check('object is const', e.message);
              }

              try {
                a[1] = 12;
                check(true, false);
              } catch (e) {
                check('object is const', e.message);
              }
              check(undefined, a[1]);

              return a;
            }
          )") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());

    formats::json::ValueBuilder json = formats::common::Type::kObject;
    json["a"].PushBack(10);
    json["a_empty"] = formats::common::Type::kArray;

    return scope.Escape(
        js::CallGlobal(js::FromContext<v8::Function>("main"),
                       New(json.ExtractValue(), Mutability::kConst)));
  }
};

struct FrozenObjectsTask : public TestingTask {
  FrozenObjectsTask()
      : TestingTask(R"(
            function main(obj) {
              check(2, obj.frozen_array.length);
              check(10, obj.frozen_array[0]);
              check(20, obj.frozen_array[1]);
              check(undefined, obj.frozen_array[2]);
              check(2, obj.frozen_array.length);
              try {
                obj.frozen_array[2] = 20;
              } catch (e) {
                // Do not throw error when try to mutate frozen array
                check(true, false);
              }
              check(undefined, obj.frozen_array[2]);
              check(2, obj.frozen_array.length);
              // Array.prototype.join() - works for frozen arrays
              check(obj.frozen_array.join(), '10,20');

              check(10, obj.frozen_object.a);
              try {
                obj.frozen_object.a = 20;
                obj.frozen_object.b = 20;
              } catch (e) {
                // Do not throw error when try to mutate frozen object
                check(true, false);
              }
              check(10, obj.frozen_object.a);
              check(undefined, obj.frozen_object.b);

              return obj;
            }
          )") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    formats::json::ValueBuilder json = formats::common::Type::kObject;
    formats::json::ValueBuilder array = formats::common::Type::kArray;
    array.PushBack(10);
    array.PushBack(20);
    formats::json::ValueBuilder object = formats::common::Type::kObject;
    object["a"] = 10;
    json["frozen_object"] = object.ExtractValue();
    json["frozen_array"] = array.ExtractValue();

    return scope.Escape(
        js::CallGlobal(js::FromContext<v8::Function>("main"),
                       New(json.ExtractValue(),
                           /*array_mutability=*/::js::Mutability::kFrozen,
                           /*object_mutability=*/::js::Mutability::kFrozen)));
  }
};

TEST_F(JsTest, CallWithoutTimeout) {
  RunInV8([](TestingContext& context) {
    auto& task_processor = engine::current_task::GetTaskProcessor();
    auto work_time = 100ms;
    auto timeout = 1000ms;

    std::optional<uint32_t> result;
    ASSERT_NO_THROW(result =
                        Execute<std::optional<uint32_t>>(
                            context, std::make_unique<TaskWithTimeout>(
                                         task_processor, work_time, timeout))
                            .Get({}));

    ASSERT_NE(result, std::nullopt);
    ASSERT_EQ(*result, 0xDEAD);
  });
}

TEST_F(JsTest, CallWithTimeout) {
  RunInV8([](TestingContext& context) {
    auto& task_processor = engine::current_task::GetTaskProcessor();
    auto timeout = 20ms;
    auto js_sleep_time = 10000ms;

    ASSERT_THROW(Execute<std::optional<uint32_t>>(
                     context, std::make_unique<TaskWithTimeout>(
                                  task_processor, js_sleep_time, timeout))
                     .Get({}),
                 js::TerminateError);
  });
}

TEST_F(JsTest, CallWithTimeoutValidState) {
  RunInV8([](TestingContext& context) {
    auto& task_processor = engine::current_task::GetTaskProcessor();

    uint32_t result = 0xDEAD;

    ASSERT_NO_THROW(
        result = Execute<uint32_t>(
                     context, std::make_unique<SeveralCallsWithTimeoutTask>(
                                  task_processor))
                     .Get({}));

    ASSERT_EQ(result, 0xBEEF);
  });
}

TEST_F(JsTest, Basic) {
  RunInV8([](TestingContext& context) {
    ASSERT_EQ(
        5, Execute<int>(context, std::make_unique<AddingTask>(2, 3)).Get({}));
  });
}

TEST_F(JsTest, OptResult) {
  RunInV8([](TestingContext& context) {
    ASSERT_EQ(std::nullopt,
              Execute<std::optional<int>>(context, std::make_unique<OptTask>())
                  .Get({}));
  });
}

TEST_F(JsTest, TimeoutInRun) {
  RunInV8(
      [](TestingContext& context) {
        ASSERT_THROW(Execute<int>(context, std::make_unique<EternalRunTask>())
                         .Get(kShortTimeout),
                     TerminationError);
        ASSERT_EQ(
            5,
            Execute<int>(context, std::make_unique<AddingTask>(2, 3)).Get({}));
      },
      /*worker_threads_count=*/1);  // ensure that previously blocked by JS
                                    // thread is reused
}

TEST_F(JsTest, TimeoutInCall) {
  RunInV8(
      [](TestingContext& context) {
        ASSERT_THROW(Execute<int>(context, std::make_unique<EternalCallTask>())
                         .Get(kShortTimeout),
                     TerminationError);
        ASSERT_EQ(
            5,
            Execute<int>(context, std::make_unique<AddingTask>(2, 3)).Get({}));
      },
      /*worker_threads_count=*/1);  // ensure that previously blocked by JS
                                    // thread is reused
}

TEST_F(JsTest, Error) {
  RunInV8([](TestingContext& context) {
    ASSERT_THROW_MSG(
        Execute<int>(context, std::make_unique<ErrorTask>()).Get({}),
        js::ExecuteError, "JS runtime error: at 12:14 !testing exception!");
  });
}

TEST_F(JsTest, MemoryCaching) {
  RunInV8(
      [](TestingContext& context) {
        {
          auto a = std::make_shared<const int>(2);
          ASSERT_EQ(5, Execute<int>(context,
                                    std::make_unique<AddingCachableTask>(a, 3))
                           .Get({}));
          ASSERT_EQ(1, AddingCachableTask::init_count);
          ASSERT_EQ(4, Execute<int>(context,
                                    std::make_unique<AddingCachableTask>(a, 2))
                           .Get({}));
          ASSERT_EQ(1, AddingCachableTask::init_count);  // no init is done
        }                                                // resource "a" dies

        {
          auto a = std::make_shared<const int>(3);
          ASSERT_EQ(6, Execute<int>(context,
                                    std::make_unique<AddingCachableTask>(a, 3))
                           .Get({}));
          ASSERT_EQ(2, AddingCachableTask::init_count);  // init required
          ASSERT_EQ(5, Execute<int>(context,
                                    std::make_unique<AddingCachableTask>(a, 2))
                           .Get({}));
          ASSERT_EQ(2, AddingCachableTask::init_count);  // no init is done
        }
      },
      /*worker_threads_count=*/1);  // guarantee that cache miss will not occur
                                    // because of different thread without cache
}

TEST_F(JsTest, StableCaching) {
  using Task = AddingStableCachableTask;

  RunInV8(
      [](TestingContext& context) {
        {
          Task::CacheParameters cache_params{
              /*slot_id=*/"slot_0",
              /*instance_id=*/"instance_0",
              /*cache_max_unused_time=*/kMaxSeconds,
          };
          const int a = 2;
          ASSERT_EQ(5, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, a, 3))
                           .Get({}));
          ASSERT_EQ(1, Task::init_count);
          ASSERT_EQ(4, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, a, 2))
                           .Get({}));
          ASSERT_EQ(1, Task::init_count);  // no init is done

          Task::init_count = 0;
        }

        {  // different slot
          Task::CacheParameters cache_params{
              /*slot_id=*/"slot_1",
              /*instance_id=*/"instance_0",
              /*cache_max_unused_time=*/kMaxSeconds,
          };
          const int a = 1;
          ASSERT_EQ(4, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, a, 3))
                           .Get({}));
          ASSERT_EQ(1, Task::init_count);
          ASSERT_EQ(3, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, a, 2))
                           .Get({}));
          ASSERT_EQ(1, Task::init_count);  // no init is done

          Task::init_count = 0;
        }

        {  // back to cached slot with same instance
          Task::CacheParameters cache_params{
              /*slot_id=*/"slot_0",
              /*instance_id=*/"instance_0",
              /*cache_max_unused_time=*/kMaxSeconds,
          };
          const int a = 10;  // should have no effect - cached value is 2
          ASSERT_EQ(5, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, a, 3))
                           .Get({}));
          ASSERT_EQ(0, Task::init_count);  // no init is done
          ASSERT_EQ(4, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, a, 2))
                           .Get({}));
          ASSERT_EQ(0, Task::init_count);  // no init is done

          Task::init_count = 0;
        }

        {  // new instance
          Task::CacheParameters cache_params{
              /*slot_id=*/"slot_0",
              /*instance_id=*/"instance_1",
              /*cache_max_unused_time=*/kMaxSeconds,
          };
          const int a = 3;
          ASSERT_EQ(6, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, a, 3))
                           .Get({}));
          ASSERT_EQ(1, Task::init_count);  // init required
          ASSERT_EQ(5, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, a, 2))
                           .Get({}));
          ASSERT_EQ(1, Task::init_count);  // no init is done

          Task::init_count = 0;
        }

        {  // check GC by setting cache_max_unused_time to 0
          Task::CacheParameters cache_params{
              /*slot_id=*/"slot_0",
              /*instance_id=*/"instance_2",
              /*cache_max_unused_time=*/0s,
          };
          const int a = 4;
          ASSERT_EQ(7, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, a, 3))
                           .Get({}));
          ASSERT_EQ(1, Task::init_count);  // init required
          ASSERT_EQ(8, Execute<int>(context,
                                    std::make_unique<Task>(cache_params, 6, 2))
                           .Get({}));
          ASSERT_EQ(2, Task::init_count);  // GC: init required

          Task::init_count = 0;
        }
      },
      /*worker_threads_count=*/1);  // guarantee that cache miss will not occur
                                    // because of different thread without cache
}

TEST_F(JsTest, MakeGlobalVar) {
  RunInV8([](TestingContext& context) {
    ASSERT_EQ(
        21,
        Execute<int>(context, std::make_unique<MakeGlobalVarTask>()).Get({}));

    ASSERT_THROW(
        Execute<int>(context, std::make_unique<MakeGlobalVarCachableTask>())
            .Get({}),
        js::ExecuteError);

    ASSERT_EQ(42, Execute<int>(context,
                               std::make_unique<MakeOkGlobalVarCachableTask>())
                      .Get({}));
  });
}

TEST_F(JsTest, ConstData) {
  RunInV8([](TestingContext& context) {
    auto json = Execute<formats::json::Value>(context,
                                              std::make_unique<ConstDataTask>())
                    .Get({});

    ASSERT_TRUE(json.IsArray());
    ASSERT_EQ(1, json.GetSize());
    ASSERT_EQ(10, json[0].As<int>());
  });
}

TEST_F(JsTest, CachableWrapper) {
  using Task = CachableWrapperTask;
  using Wrapper = Task::Wrapper;
  using CacheEntry = Wrapper::CacheEntry;

  RunInV8(
      [](TestingContext& context) {
        {
          Wrapper wrapper;
          auto& data = wrapper.GetData();

          EXPECT_EQ(0, data.build_count);  // no build is done

          EXPECT_EQ(
              1,
              Execute<int>(context, std::make_unique<Task>(wrapper)).Get({}));

          EXPECT_EQ(1, data.build_count);            // build is done
          EXPECT_EQ(0, CacheEntry::value_gc_count);  // cold cache - no GC

          EXPECT_EQ(
              1,
              Execute<int>(context, std::make_unique<Task>(wrapper)).Get({}));

          EXPECT_EQ(1, data.build_count);            // no build - cached
          EXPECT_EQ(1, CacheEntry::value_gc_count);  // one GC per task

          CacheEntry::value_gc_count = 0;
        }
        {
          // no V8 state rebuild even after wrapper recreation
          Wrapper wrapper;
          // data will not be reused - previous wrapper is dead
          // so this reference will not expire
          auto& data = wrapper.GetData();

          EXPECT_EQ(0, data.build_count);  // no build is done

          EXPECT_EQ(
              0,
              Execute<int>(context, std::make_unique<Task>(wrapper)).Get({}));

          EXPECT_EQ(0, data.build_count);            // no build - cached
          EXPECT_EQ(1, CacheEntry::value_gc_count);  // one GC per task

          CacheEntry::value_gc_count = 0;

          EXPECT_EQ(
              0,
              Execute<int>(context, std::make_unique<Task>(wrapper)).Get({}));

          EXPECT_EQ(0, data.build_count);            // no build - cached
          EXPECT_EQ(1, CacheEntry::value_gc_count);  // one GC per task
        }
      },
      /*worker_threads_count=*/1);  // guarantee that cache miss will not occur
                                    // because of different thread without cache
}

TEST_F(JsTest, FrozenObjects) {
  RunInV8([](TestingContext& context) {
    auto json = Execute<formats::json::Value>(
                    context, std::make_unique<FrozenObjectsTask>())
                    .Get({});
    const auto array = json["frozen_array"];
    ASSERT_TRUE(array.IsArray());
    ASSERT_EQ(2, array.GetSize());
    ASSERT_EQ(10, array[0].As<int>());
    ASSERT_EQ(20, array[1].As<int>());
    const auto object = json["frozen_object"];
    ASSERT_TRUE(object.IsObject());
    ASSERT_EQ(1, object.GetSize());
    ASSERT_EQ(10, object["a"].As<int>());
  });
}

TEST_F(JsTest, GeneratorTask_ReuseContext) {
  struct ContextCheckingGeneratingTask : public TestingGeneratorTask {
    int n, i = 0;

    ContextCheckingGeneratingTask(int n) : TestingGeneratorTask(""), n(n) {}

    bool IsDone() const { return i > n; }
    v8::Local<v8::Value> Execute(const AsyncPublicContext&) {
      auto current_context = GetCurrentContext();
      if (i == 0) {
        current_context->SetAlignedPointerInEmbedderData(5, this);
      }
      UINVARIANT(current_context->GetAlignedPointerFromEmbedderData(5) == this,
                 "V8 context changed");
      return js::New(i++);
    }
  };

  RunInV8([](TestingContext& context) {
    bool was_done = false;
    const int kN = 10;

    std::vector<int> results, expected = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    auto channel = Execute<int>(
        context, std::make_unique<ContextCheckingGeneratingTask>(kN));
    for (auto i : channel.Iterate({})) {
      EXPECT_FALSE(was_done);
      results.push_back(i);
      was_done |= channel.IsDone();
    }
    EXPECT_TRUE(channel.IsDone());
    ASSERT_EQ(expected, results);
  });
}

TEST_F(JsTest, GeneratorTask_Iterate) {
  RunInV8([](TestingContext& context) {
    bool was_done = false;
    const int kN = 10;

    std::vector<int> results, expected = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    auto channel = Execute<int>(context, std::make_unique<GeneratingTask>(kN));
    for (auto i : channel.Iterate({})) {
      EXPECT_FALSE(was_done);
      results.push_back(i);
      was_done |= channel.IsDone();
    }
    EXPECT_TRUE(channel.IsDone());
    ASSERT_EQ(expected, results);
  });
}

TEST_F(JsTest, GeneratorTask_Exception) {
  RunInV8([](TestingContext& context) {
    bool was_done = false;
    const int kN = 10;
    const int kThrowAt = 5;

    std::vector<int> results, expected = {0, 1, 2, 3, 4};

    auto perform = [&] {
      auto channel =
          Execute<int>(context, std::make_unique<GeneratingTask>(kN, kThrowAt));
      for (auto i : channel.Iterate({})) {
        EXPECT_FALSE(was_done);
        results.push_back(i);
        was_done |= channel.IsDone();
      }
    };

    EXPECT_THROW_MSG_CONTAINS(perform(), js::ExecuteError, "exception from JS");
    ASSERT_EQ(expected, results);
  });
}

struct CachableHandleWrapper : public CachableJsWrapper {
  using StatePtr = std::shared_ptr<void*>;
  static inline std::set<const NativeDataInterface*> freed;
  static inline std::map<const NativeDataInterface*, int> handle_access_counts;
  static inline int access_count{0};
  static inline int build_count{0};

  struct NativeData final : public NativeDataInterface {
    StatePtr state_ptr;

    explicit NativeData(StatePtr state_ptr) : state_ptr(state_ptr) {}
    ~NativeData() { freed.insert(this); }

    static void TestCb(const v8::FunctionCallbackInfo<v8::Value>& info,
                       Handle& handle) {
      auto* data_ptr = &handle.As<NativeData>();
      // honestly this check is outdated since handle now uses weak_ptr instead
      // of raw pointer and has its own check for expiration inside As,
      // but let's keep this check just in case
      EXPECT_FALSE(freed.count(data_ptr)) << "handle points to a deleted data";
      handle_access_counts[data_ptr]++;
      info.GetReturnValue().Set(access_count++);
    }

    NativeResourceCacheEntryPtr GetResourceCacheEntry() const override {
      struct CacheEntry : public NativeResourceCacheEntry {
        void* id;
        StatePtr::weak_type w_ptr;
        CacheEntry(StatePtr ptr) : id(*ptr), w_ptr(ptr) {}

        Key GetId() const override { return id; }
        bool IsExpired() const override { return w_ptr.expired(); }
      };
      UASSERT(state_ptr);
      return std::make_unique<CacheEntry>(state_ptr);
    }

    v8::Local<v8::Value> BuildJsValue(Handle& handle) const override {
      ++build_count;
      return New<TestCb>(handle);
    }
  };

  explicit CachableHandleWrapper(StatePtr state_ptr)
      : CachableJsWrapper(std::make_shared<NativeData>(state_ptr)) {}
};

TEST_F(JsTest, GeneratorTask_CachableWrapperHandle) {
  using StatePtr = CachableHandleWrapper::StatePtr;
  CachableHandleWrapper::access_count = 0;
  CachableHandleWrapper::build_count = 0;
  CachableHandleWrapper::freed.clear();
  CachableHandleWrapper::handle_access_counts.clear();

  struct Task : public TestingWrappedGeneratorTask {
    CachableHandleWrapper wrapper;

    Task(StatePtr state)
        : TestingWrappedGeneratorTask(R"(
          function* test(wrapped){
            yield wrapped();
            return wrapped();
          }
        )"),
          wrapper(state) {}

    v8::Local<v8::Object> GetGenerator(
        const AsyncPublicContext&) const override {
      UASSERT(!IsDone());

      return js::As<v8::Object>(js::CallGlobal(
          js::FromContext<v8::Function>("test"), wrapper.AsJsValue()));
    }
  };

  RunInV8(
      [](TestingContext& context) {
        StatePtr state = std::make_shared<void*>();
        *state = state.get();

        auto ch1 = Execute<int>(context, std::make_unique<Task>(state));
        auto ch2 = Execute<int>(context, std::make_unique<Task>(state));

        ch1.Get({});  // cache miss, wrapper from task 1 ref
        ch2.Get({});  // cache hit, wrapper from task 2 ref

        {  // destroy task 2 and wrapper, stored in it
          ch2.Resume();
          ch2.Get({});
          ASSERT_TRUE(ch2.IsDone());
        }

        {  // access handle (provoke UB)
          ch1.Resume();
          ch1.Get({});
          ASSERT_TRUE(ch1.IsDone());
        }

        ASSERT_EQ(4, CachableHandleWrapper::access_count)
            << "total_count: " << CachableHandleWrapper::access_count;

        ASSERT_EQ(2, CachableHandleWrapper::freed.size());
        ASSERT_EQ(1, CachableHandleWrapper::build_count);

        // check that existing data was prolongated instead of update
        ASSERT_EQ(1, CachableHandleWrapper::handle_access_counts.size());
        ASSERT_EQ(CachableHandleWrapper::access_count,
                  CachableHandleWrapper::handle_access_counts.begin()->second);
      },
      1);
}

struct StackOverflowCallTask : public TestingTask {
  StackOverflowCallTask()
      : TestingTask(R"(
            function test() {
              return test();
            }
          )") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    CallGlobal(js::FromContext<v8::Function>("test"));
    return {};
  }
};

struct StackOverflowRunTask : public TestingTask {
  StackOverflowRunTask()
      : TestingTask(R"(
            function test() {
              return test();
            }
            test();
          )") {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    UINVARIANT(false, "Execute isn't supposed to be called here");
    return {};
  }
};

TEST_F(JsTest, StackOverflow) {
  RunInV8([](TestingContext& context) {
    ASSERT_THROW_MSG_CONTAINS(
        Execute<std::optional<int>>(context,
                                    std::make_unique<StackOverflowCallTask>())
            .Get({}),
        js::ExecuteError, "RangeError: Maximum call stack size exceeded");

    ASSERT_THROW_MSG_CONTAINS(
        Execute<std::optional<int>>(context,
                                    std::make_unique<StackOverflowRunTask>())
            .Get({}),
        js::ExecuteError, "RangeError: Maximum call stack size exceeded");
  });
}

TEST_F(JsTest, CastVariant) {
  ExecuteInV8([] {
    auto number = js::New(10);
    auto variant = js::TypeCast<std::variant<std::string, int>>(number);
    EXPECT_TRUE(std::holds_alternative<int>(variant));
    EXPECT_EQ(10, std::get<int>(variant));
    EXPECT_THROW_MSG(
        (js::TypeCast<std::variant<std::string, std::vector<int>>>(number)),
        js::Error,
        "type mismatch, no matched variant for 'number': type mismatch, got "
        "'number' when a 'string' was expected; type mismatch, got 'number' "
        "when an array was expected");
  });
}

TEST_F(JsTest, Int64) {
  ExecuteInV8([] {
    constexpr auto kHumanPopulation = 7929552222;
    EXPECT_EQ(kHumanPopulation,
              js::TypeCast<int64_t>(js::New(kHumanPopulation)));
    EXPECT_EQ(
        kHumanPopulation,
        js::TypeCast<formats::json::Value>(
            js::New(
                formats::json::ValueBuilder{kHumanPopulation}.ExtractValue()))
            .As<int64_t>());
  });
}

}  // namespace js::testing
