#include <tests/common.hpp>

struct JsValueBuilder : Fixture {};

TEST_F(JsValueBuilder, ExampleUsage) {
  ExecuteInV8([] {
    /// [Sample formats::js::ValueBuilder usage]
    // #include <formats/js/value_builder.hpp>
    formats::js::ValueBuilder builder;
    builder["key1"] = 1;
    builder["key2"]["key3"] = "val";
    formats::js::Value js = builder.ExtractValue();

    EXPECT_EQ(js["key1"].As<int>(), 1);
    EXPECT_EQ(js["key2"]["key3"].As<std::string>(), "val");
    /// [Sample formats::js::ValueBuilder usage]
  });
}

TEST_F(JsValueBuilder, ValueString) {
  ExecuteInV8([] {
    formats::js::ValueBuilder builder;
    builder = "abc";
    formats::js::Value js = builder.ExtractValue();

    EXPECT_EQ(js.As<std::string>(), "abc");
    EXPECT_THROW(js.As<int>(), formats::js::TypeMismatchException);
  });
}

TEST_F(JsValueBuilder, ValueEmptyString) {
  ExecuteInV8([] {
    formats::js::ValueBuilder builder;
    builder = "";
    formats::js::Value js = builder.ExtractValue();

    EXPECT_EQ(js.As<std::string>(), "");
    EXPECT_THROW(js.As<std::vector<std::string>>(),
                 formats::js::TypeMismatchException);
  });
}

TEST_F(JsValueBuilder, ValueNumber) {
  ExecuteInV8([] {
    formats::js::ValueBuilder builder;
    builder = 321;
    formats::js::Value js = builder.ExtractValue();

    EXPECT_EQ(js.As<int>(), 321);
    EXPECT_THROW(js.As<bool>(), formats::js::TypeMismatchException);
  });
}

TEST_F(JsValueBuilder, ValueTrue) {
  ExecuteInV8([] {
    formats::js::ValueBuilder builder;
    builder = true;
    formats::js::Value js = builder.ExtractValue();

    EXPECT_EQ(js.As<bool>(), true);
    EXPECT_THROW(js.As<int>(), formats::js::TypeMismatchException);
  });
}

TEST_F(JsValueBuilder, ValueFalse) {
  ExecuteInV8([] {
    formats::js::ValueBuilder builder = false;
    formats::js::Value js = builder.ExtractValue();

    EXPECT_EQ(js.As<bool>(), false);
    EXPECT_THROW(js.As<int>(), formats::js::TypeMismatchException);
  });
}

TEST_F(JsValueBuilder, ValueNull) {
  ExecuteInV8([] {
    formats::js::ValueBuilder builder;
    builder = std::optional<int>{};
    formats::js::Value js = builder.ExtractValue();

    EXPECT_EQ(js.As<std::optional<int>>(), std::nullopt);
    EXPECT_EQ(js.As<std::optional<std::vector<std::string>>>(), std::nullopt);
    EXPECT_THROW(js.As<int>(), formats::js::TypeMismatchException);

    formats::js::ValueBuilder builder_def;
    formats::js::Value json_def = builder_def.ExtractValue();

    EXPECT_EQ(json_def.As<std::optional<std::string>>(), std::nullopt);
  });
}

TEST_F(JsValueBuilder, PushBack) {
  ExecuteInV8([] {
    formats::js::ValueBuilder builder;

    builder.PushBack(1);
    builder.PushBack(2);
    builder.PushBack(3);
    builder.PushBack(4);

    formats::js::Value js = builder.ExtractValue();

    EXPECT_EQ(js.GetSize(), 4);

    uint32_t sum = 0;

    for (const auto& item : js) {
      sum += item.As<uint32_t>();
    }

    EXPECT_EQ(sum, 10);
  });
}

/// [Sample Customization formats::js::ValueBuilder usage]
namespace my_namespace {

struct MyKeyValue {
  std::string field1;
  int field2;
};

// The function must be declared in the namespace of your type
formats::js::Value Serialize(const MyKeyValue& data,
                             formats::serialize::To<formats::js::Value>) {
  formats::js::ValueBuilder builder;
  builder["field1"] = data.field1;
  builder["field2"] = data.field2;

  return builder.ExtractValue();
}

TEST_F(JsValueBuilder, ExampleCustomization) {
  ExecuteInV8([] {
    MyKeyValue object = {"val", 1};
    formats::js::ValueBuilder builder;
    builder["example"] = object;
    auto js = builder.ExtractValue();
    EXPECT_EQ(js["example"]["field1"].As<std::string>(), "val");
    EXPECT_EQ(js["example"]["field2"].As<int>(), 1);
  });
}

}  // namespace my_namespace

/// [Sample Customization formats::js::ValueBuilder usage]
