#include <gtest/gtest.h>

#include <memory>
#include <type_traits>

#include <fmt/format.h>
#include <libplatform/libplatform.h>
#include <v8.h>

#include <js/isolate_wrapper.hpp>
#include <js/utils.hpp>
#include <js/wrappers/bson_wrapper.hpp>

constexpr auto kEqKeys = {
    "key1",         "some_large_str_with_postfix_",
    "-100",         "-100500",
    "+79162991489", "79162991489",
    "4294967295",
};

constexpr auto kUndefKeys = {"4294967294", "1000000000", "100500", "123", "0"};

const std::string kValue{"test_value"};

namespace {

namespace impl {

[[maybe_unused]] class PlatformIniter {
 public:
  PlatformIniter() {
    ::v8::V8::InitializePlatform(platform_.get());
    ::v8::V8::Initialize();
  }

  ~PlatformIniter() {
    ::v8::V8::Dispose();
    ::v8::V8::ShutdownPlatform();
  }

 private:
  std::unique_ptr<::v8::Platform> platform_{
      ::v8::platform::CreateDefaultPlatform()};
} const platform_initer_;

struct Env {
  IsolateWrapper isolate_wrapper_;

  ::v8::Isolate::Scope isolate_scope_{isolate_wrapper_.Isolate()};
  ::v8::HandleScope handle_scope_{isolate_wrapper_.Isolate()};

  ::v8::Local<::v8::Context> context{
      ::v8::Context::New(isolate_wrapper_.Isolate())};
  ::v8::Context::Scope context_scope{context};
};

auto MakeSource(const std::string& s) {
  static const std::string kUseStrict{"'use strict';"};

  return fmt::format("{}\n{}", kUseStrict, s);
}

auto MakeBson() {
  ::mongo::BSONObjBuilder builder;

  for (const auto key : kEqKeys) {
    builder.append(key, kValue);
  }

  for (const auto key : kUndefKeys) {
    builder.append(key, kValue);
  }

  return builder.obj();
}

template <typename T>
auto GetField(::v8::Local<::v8::Object> holder, int i) {
  return static_cast<T*>(
      holder->GetInternalField(i).As<::v8::External>()->Value());
}

template <typename V>
void GetterCallback(::v8::Local<::v8::Name> property,
                    const ::v8::PropertyCallbackInfo<::v8::Value>& info) {
  const auto key = ::js::TypeCast<std::string>(property);

  auto expected_key = GetField<std::string>(info.Holder(), 0);
  auto value = GetField<V>(info.Holder(), 1);

  if (key == *expected_key) {
    info.GetReturnValue().Set(::js::New(*value));
    return;
  }

  throw std::exception{};
}

template <typename F, typename V>
void DoTest(std::string key, V v, F f, ::v8::Local<::v8::Value> obj = {}) {
  const auto arg = [&key, &v, obj] {
    if (!obj.IsEmpty()) {
      return obj;
    }

    auto tpl = ::v8::ObjectTemplate::New(::js::CheckIsolate());

    tpl->SetInternalFieldCount(2);

    tpl->SetHandler({GetterCallback<V>, nullptr, nullptr, nullptr, nullptr,
                     nullptr, v8::Local<::v8::Object>{},
                     ::v8::PropertyHandlerFlags::kNonMasking});

    auto arg = tpl->NewInstance(::js::CheckContext()).ToLocalChecked();

    arg->SetInternalField(0, ::v8::External::New(::js::CheckIsolate(), &key));
    arg->SetInternalField(1, ::v8::External::New(::js::CheckIsolate(), &v));

    return arg.As<::v8::Value>();
  }();

  {
    const std::string kSource{
        fmt::format("function handle(obj) {{ return obj['{}']; }}", key)};

    auto script = ::js::Compile(MakeSource(kSource));

    static_cast<void>(::js::Run(script));
    auto handle = ::js::FromContext<::v8::Function>("handle");

    f(::js::Call(handle, arg));
  }
}

}  // namespace impl

template <typename V>
void TestEq(const std::string& key, V v) {
  impl::Env env;

  impl::DoTest(key, v, [&v](::v8::Local<::v8::Value> result) {
    EXPECT_EQ(v, ::js::TypeCast<std::decay_t<V>>(result));
  });
}

template <typename V>
void TestUndef(const std::string& key, V v) {
  impl::Env env;

  impl::DoTest(key, v, [](::v8::Local<::v8::Value> result) {
    EXPECT_TRUE(result->IsUndefined());
  });
}

template <typename V>
void TestWrapperEq(const std::string& key, V v) {
  impl::Env env;

  ::js::wrappers::BsonJsWrapper wrapper{impl::MakeBson()};

  impl::DoTest(key, v,
               [&v](::v8::Local<::v8::Value> result) {
                 EXPECT_EQ(v, ::js::TypeCast<std::decay_t<V>>(result));
               },
               wrapper.AsJsValue());
}

template <typename V>
void TestWrapperUndef(const std::string& key, V v) {
  impl::Env env;

  ::js::wrappers::BsonJsWrapper wrapper{impl::MakeBson()};

  impl::DoTest(key, v,
               [](::v8::Local<::v8::Value> result) {
                 EXPECT_TRUE(result->IsUndefined());
               },
               wrapper.AsJsValue());
}

template <typename EqFunc, typename UndefFunc>
void BaseTest(EqFunc eq_func, UndefFunc undef_func) {
  for (const auto key : kEqKeys) {
    eq_func(key, kValue);
  }

  for (const auto key : kUndefKeys) {
    undef_func(key, kValue);
  }
}

}  // namespace

TEST(V8NamedPropertyHandler, PureLazyImpl) {
  BaseTest(TestEq<decltype(kValue)>, TestUndef<decltype(kValue)>);
}

TEST(V8NamedPropertyHandler, BsonJsWrapper) {
  BaseTest(TestWrapperEq<decltype(kValue)>, TestWrapperUndef<decltype(kValue)>);
}
