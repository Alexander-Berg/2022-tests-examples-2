#include <js-pipeline/execution/json_value/array_view.hpp>
#include <js-pipeline/execution/json_value/object_view.hpp>
#include <js-pipeline/execution/json_value/value_base.hpp>
#include <js-pipeline/execution/json_value/view.hpp>
#include <js-pipeline/models/serialization/json/schema.hpp>

#include "common.hpp"

#include <userver/utils/assert.hpp>

namespace js_pipeline::testing {

namespace {

struct ObjectWrapperTest : public JSTest {
  using JSTest::JSTest;
};

using js_pipeline::execution::ObjectWrapper;
using js_pipeline::execution::json_value::ValueBase;
using js_pipeline::execution::json_value::ValuePtr;

struct BasicTestingTask : public TestingTask {
  ValuePtr obj;
  BasicTestingTask()
      : TestingTask(ReadResource("basic.js")),
        obj(ValueBase::New(ReadJsonResource("basic.json"), "basic_json")) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    js_pipeline::execution::ObjectWrapper wrapped(obj->AsTransactional());
    auto js_obj = wrapped.AsJsValue();
    UASSERT(ObjectWrapper::IdentifyInstanceType(js_obj) ==
            ObjectWrapper::InstanceType::kObject);
    UASSERT(ObjectWrapper::IdentifyInstanceType(
                js::FromMaybe(js_obj.As<v8::Object>()->Get(
                    js::GetCurrentContext(), js::New("a1")))) ==
            ObjectWrapper::InstanceType::kArray);
    return scope.Escape(
        js::CallGlobal(js::FromContext<v8::Function>("test"), js_obj));
  }
};

struct InterceptorsTestingTask : public TestingTask {
  ValuePtr obj;
  InterceptorsTestingTask()
      : TestingTask(ReadResource("interceptors.js")),
        obj(ValueBase::New(ReadJsonResource("interceptors.json"),
                           "interceptors_json")) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::Local v8_context = js::GetCurrentContext();

    v8::Local global = v8_context->Global();

    js::SetWithContext set{&v8_context};

    set(global, js_pipeline::execution::ObjectWrapper::kObjectJsClassName,
        js_pipeline::execution::ObjectWrapper::GetObjectFunctionTemplate()
            ->GetFunction(v8_context));

    set(global, js_pipeline::execution::ObjectWrapper::kArrayJsClassName,
        js_pipeline::execution::ObjectWrapper::GetArrayFunctionTemplate()
            ->GetFunction(v8_context));

    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    js_pipeline::execution::ObjectWrapper wrapped(obj->AsTransactional());
    auto res = js::CallGlobal(js::FromContext<v8::Function>("test"),
                              wrapped.AsJsValue());
    return scope.Escape(res);
  }
};

struct MutabilityTestingTask : public TestingTask {
  ValueBase& obj;
  MutabilityTestingTask(ValueBase& obj)
      : TestingTask(ReadResource("mutability.js")), obj(obj) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    js_pipeline::execution::ObjectWrapper wrapped(obj.AsTransactional());
    return scope.Escape(js::CallGlobal(js::FromContext<v8::Function>("test"),
                                       wrapped.AsJsValue()));
  }
};

struct AutoInitializationTestingTask : public TestingTask {
  ValueBase& obj;
  AutoInitializationTestingTask(ValueBase& obj)
      : TestingTask(ReadResource("auto_initialization.js")), obj(obj) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    js_pipeline::execution::ObjectWrapper wrapped(obj.AsTransactional());
    auto res = js::CallGlobal(js::FromContext<v8::Function>("test"),
                              wrapped.AsJsValue());
    return scope.Escape(res);
  }
};

struct ValidationTestingTask : public TestingTask {
  ValueBase& obj;
  ValidationTestingTask(ValueBase& obj)
      : TestingTask(ReadResource("validation.js")), obj(obj) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    js_pipeline::execution::ObjectWrapper wrapped(obj.AsTransactional());
    auto res = js::CallGlobal(js::FromContext<v8::Function>("test"),
                              wrapped.AsJsValue());
    return scope.Escape(res);
  }
};

struct ComplexInitTestingTask : public TestingTask {
  ValueBase& obj;
  ComplexInitTestingTask(ValueBase& obj)
      : TestingTask(ReadResource("complex_init.js")), obj(obj) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    js_pipeline::execution::ObjectWrapper wrapped(obj.AsTransactional());
    auto res = js::CallGlobal(js::FromContext<v8::Function>("test"),
                              wrapped.AsJsValue());
    return scope.Escape(res);
  }
};

}  // namespace

TEST_F(ObjectWrapperTest, Basic) {
  RunInV8([](TestingContext& context) {
    ASSERT_EQ("str9", Execute<std::string>(context,
                                           std::make_unique<BasicTestingTask>())
                          .Get(kTimeout));
  });
}

TEST_F(ObjectWrapperTest, Interceptors) {
  RunInV8([](TestingContext& context) {
    ASSERT_TRUE(
        Execute<bool>(context, std::make_unique<InterceptorsTestingTask>())
            .Get(kTimeout));
  });
}

TEST_F(ObjectWrapperTest, Mutability) {
  RunInV8([](TestingContext& context) {
    auto obj =
        ValueBase::New(ReadJsonResource("mutability.json"), "mutability_json");
    Execute<std::optional<int>>(context,
                                std::make_unique<MutabilityTestingTask>(*obj))
        .Get(kTimeout);

    ASSERT_EQ(20, obj->AsJson().Get("a1")->AsArray().GetSize());

    EXPECT_EQ(21, obj->AsJson()["o1"]["o2"].Get("p1")->As<int>());
    EXPECT_EQ(55, obj->AsJson()["a1"].Get(19u)->As<int>());

    EXPECT_EQ(12, obj->AsJson().Get("f1")->As<int>());
    EXPECT_EQ("0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19",
              obj->AsJson().Get("s1")->As<std::string>());
  });
}

TEST_F(ObjectWrapperTest, AutoInitialization) {
  RunInV8([](TestingContext& context) {
    ValueBase obj(
        /*json=*/formats::json::FromString("{}"),
        /*id=*/"<test>", /*parent=*/nullptr,
        /*schema=*/
        ReadJsonResource("auto_initialization.schema.json")
            .As<models::SchemaCPtr>());

    EXPECT_EQ(42,
              Execute<int>(context,
                           std::make_unique<AutoInitializationTestingTask>(obj))
                  .Get(kTimeout));

    EXPECT_EQ(ReadJsonResource("auto_initialization.expected.json"),
              obj.ToJson());
  });
}

TEST_F(ObjectWrapperTest, Validation) {
  RunInV8([](TestingContext& context) {
    ValueBase obj(
        /*json=*/formats::json::FromString("{}"),
        /*id=*/"<test>",
        /*parent=*/nullptr,
        /*schema=*/
        ReadJsonResource("validation.schema.json").As<models::SchemaCPtr>());

    auto result = Execute<std::string>(
                      context, std::make_unique<ValidationTestingTask>(obj))
                      .Get(kTimeout);

    EXPECT_EQ(result, "ok");

    EXPECT_EQ(ReadJsonResource("validation.expected.json"), obj.ToJson());
  });
}

TEST_F(ObjectWrapperTest, ComplexInit) {
  RunInV8([](TestingContext& context) {
    auto data = ReadJsonResource("complex_init.json");

    ValueBase obj(
        /*json=*/data["INPUT"],
        /*id=*/"<test>",
        /*parent=*/nullptr,
        /*schema=*/
        ReadJsonResource("complex_init.schema.json").As<models::SchemaCPtr>());

    auto result = Execute<std::string>(
                      context, std::make_unique<ComplexInitTestingTask>(obj))
                      .Get(kTimeout);

    EXPECT_EQ(result, "ok");
    EXPECT_EQ(data["EXPECTED"], obj.ToJson());
  });
}

}  // namespace js_pipeline::testing
