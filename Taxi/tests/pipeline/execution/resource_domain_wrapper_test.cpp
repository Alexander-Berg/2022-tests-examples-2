#include <js-pipeline/execution/resource_domain_wrapper.hpp>

#include "../../common.hpp"
#include "common.hpp"

#include <userver/utils/assert.hpp>

namespace js_pipeline::testing {

using js_pipeline::execution::ResourceDomainWrapper;

namespace {

struct BasicTestingTask : public TestingTask {
  std::shared_ptr<ResourceDomainWrapper> wrapper;

  BasicTestingTask(const char* js_fname,
                   std::shared_ptr<ResourceDomainWrapper> wrapper)
      : TestingTask(ReadResource(js_fname)), wrapper(wrapper) {}

  v8::Local<v8::Value> Execute(const AsyncPublicContext&) const override {
    v8::EscapableHandleScope scope(js::GetCurrentIsolate());
    auto js_obj = wrapper->AsJsValue();
    UASSERT(ResourceDomainWrapper::InstanceOf(js_obj));
    return scope.Escape(
        js::CallGlobal(js::FromContext<v8::Function>("test"), js_obj));
  }
};

struct DummyResourceInstance : public resource_management::Instance {
  std::string name;

  DummyResourceInstance(std::string name) : name(std::move(name)) {}

  v8::Local<v8::Value> AsJsValue() const override {
    return js::New("dummy resource instance " + name);
  }
};

struct ResourceDomainWrapperTest : public JSTest {
  using JSTest::JSTest;
};

}  // namespace

TEST_F(ResourceDomainWrapperTest, Basic) {
  RunInV8([](TestingContext& context) {
    auto wrapper =
        std::make_shared<ResourceDomainWrapper>(resource_management::Instances{
            {"r1", std::make_unique<DummyResourceInstance>("r1")},
            {"r2", std::make_unique<DummyResourceInstance>("r2")},
            {"r3", std::make_unique<DummyResourceInstance>("r3")},
        });

    ASSERT_EQ("ok",
              Execute<std::string>(context, std::make_unique<BasicTestingTask>(
                                                "basic.js", wrapper))
                  .Get(kTimeout));
  });
}

TEST_F(ResourceDomainWrapperTest, Immutable) {
  RunInV8([](TestingContext& context) {
    auto wrapper =
        std::make_shared<ResourceDomainWrapper>(resource_management::Instances{
            {"r1", std::make_unique<DummyResourceInstance>("r1")},
            {"r2", std::make_unique<DummyResourceInstance>("r2")},
            {"r3", std::make_unique<DummyResourceInstance>("r3")},
        });

    ASSERT_EQ("ok",
              Execute<std::string>(context, std::make_unique<BasicTestingTask>(
                                                "immutable.js", wrapper))
                  .Get(kTimeout));
  });
}

TEST_F(ResourceDomainWrapperTest, Caching) {
  static int total_count;
  total_count = 0;

  struct CountingResourceInstance : public DummyResourceInstance {
    using DummyResourceInstance::DummyResourceInstance;

    v8::Local<v8::Value> AsJsValue() const override {
      ++total_count;
      return js::New("dummy resource instance " + name);
    }
  };

  RunInV8([](TestingContext& context) {
    auto wrapper =
        std::make_shared<ResourceDomainWrapper>(resource_management::Instances{
            {"r1", std::make_unique<CountingResourceInstance>("r1")},
            {"r2", std::make_unique<CountingResourceInstance>("r2")},
            {"r3", std::make_unique<CountingResourceInstance>("r3")},
        });

    ASSERT_EQ("ok",
              Execute<std::string>(context, std::make_unique<BasicTestingTask>(
                                                "caching.js", wrapper))
                  .Get(kTimeout));
    ASSERT_EQ(3, total_count);
  });
}

TEST_F(ResourceDomainWrapperTest, Extend) {
  static int total_count;
  total_count = 0;

  struct CountingResourceInstance : public DummyResourceInstance {
    using DummyResourceInstance::DummyResourceInstance;

    v8::Local<v8::Value> AsJsValue() const override {
      ++total_count;
      return js::New("dummy resource instance " + name);
    }
  };

  RunInV8([](TestingContext& context) {
    auto wrapper =
        std::make_shared<ResourceDomainWrapper>(resource_management::Instances{
            {"r1", std::make_unique<CountingResourceInstance>("r1")},
            {"r2", std::make_unique<CountingResourceInstance>("r2")},
            {"r3", std::make_unique<CountingResourceInstance>("r3")},
        });

    ASSERT_EQ("ok",
              Execute<std::string>(context, std::make_unique<BasicTestingTask>(
                                                "extend1.js", wrapper))
                  .Get(kTimeout));
    ASSERT_EQ(3, total_count);

    total_count = 0;

    wrapper->Extend({
        {"r4", std::make_unique<CountingResourceInstance>("r4")},
    });

    ASSERT_EQ("ok",
              Execute<std::string>(context, std::make_unique<BasicTestingTask>(
                                                "extend2.js", wrapper))
                  .Get(kTimeout));

    ASSERT_EQ(4, total_count);
  });
}

}  // namespace js_pipeline::testing
