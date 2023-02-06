#include <plugins/common/rendering.hpp>

#include <userver/utest/utest.hpp>

namespace {

namespace plugins = routestats::plugins::common;
using plugins::PluginsVec;
using SerializablePtr = std::shared_ptr<plugins::Serializable>;

class TestObjectWithAddedField : public plugins::Serializable {
 public:
  TestObjectWithAddedField(int added_field) : added_field_{added_field} {}
  formats::json::Value Serialize() const override {
    formats::json::ValueBuilder builder;
    builder["added_field"] = added_field_;
    return builder.ExtractValue();
  }

 private:
  int added_field_;
};

struct TestContext {};
static const TestContext test_ctx;

struct TestPluginBase : public plugins::PluginBase {
  virtual SerializablePtr OnRender(const TestContext&) = 0;
};

class TestPlugin : public TestPluginBase {
 public:
  TestPlugin(int id) : id_{id} {}
  std::string Name() const override { return ""; }
  SerializablePtr OnRender(const TestContext&) override {
    return std::make_shared<TestObjectWithAddedField>(id_);
  }

 private:
  int id_;
};

struct EmptyPlugin : public TestPluginBase {
  std::string Name() const override { return ""; }
  SerializablePtr OnRender(const TestContext&) override { return {}; }
};

}  // namespace

UTEST(TestObjectRendering, Basic) {
  PluginsVec<TestPluginBase> plugins{std::make_shared<TestPlugin>(0)};
  plugins::Runner runner;
  plugins::RenderingResultsMerger merger{runner};

  const auto res_json =
      merger.Merge("object type", plugins, &TestPluginBase::OnRender, test_ctx);
  ASSERT_TRUE(res_json["added_field"].IsInt());
  ASSERT_EQ(0, res_json["added_field"].As<int>());
  ASSERT_EQ(static_cast<size_t>(1), res_json.GetSize());
}

UTEST(TestObjectRendering, DuplicateKeyThrowsException) {
  // Both plugins write to the same key "added_field".
  PluginsVec<TestPluginBase> plugins{
      std::make_shared<TestPlugin>(0),
      std::make_shared<TestPlugin>(1),
  };
  plugins::Runner runner;
  plugins::RenderingResultsMerger merger{runner};

  EXPECT_THROW(
      merger.Merge("object type", plugins, &TestPluginBase::OnRender, test_ctx),
      plugins::RenderException);
}

UTEST(TestObjectRendering, EmptyResult) {
  PluginsVec<TestPluginBase> plugins{std::make_shared<EmptyPlugin>()};
  plugins::Runner runner;
  plugins::RenderingResultsMerger merger{runner};

  const auto res_json =
      merger.Merge("object type", plugins, &TestPluginBase::OnRender, test_ctx);
  ASSERT_EQ(formats::json::Value{}, res_json);
}
