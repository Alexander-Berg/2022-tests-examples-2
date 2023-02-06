#include <gtest/gtest.h>

#include "radio/blocks/commutation/out_points.hpp"
#include "radio/blocks/utils/buffers.hpp"
#include "radio/blocks/utils/meta_filler.hpp"

namespace hejmdal::radio::blocks {

TEST(TestMetaFiller, TestDataMetaFiller) {
  formats::json::ValueBuilder builder;
  builder["type"] = "meta_filler";
  builder["id"] = "meta_filler";
  builder["path"].Resize(2);
  builder["path"][0] = "domain";
  builder["path"][1] = "value";
  auto test = std::make_shared<MetaFiller>(builder.ExtractValue());
  auto exit = std::make_shared<DataBuffer>("");
  test->OnDataOut(exit);

  formats::json::ValueBuilder meta{formats::common::Type::kObject};

  {
    // absent path
    test->DataIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(), 1.234);
    EXPECT_EQ(exit->LastValue(), 1.234);
    auto last_meta = exit->LastMeta();
    ASSERT_TRUE(last_meta.Has("domain"));
    ASSERT_TRUE(last_meta.Get("domain").IsObject());
    ASSERT_TRUE(last_meta.Get("domain").HasMember("value"));
    ASSERT_TRUE(last_meta.Get("domain")["value"].IsDouble());
    EXPECT_EQ(last_meta.Get("domain")["value"].As<double>(), 1.234);
  }

  {
    // not absent path
    meta["domain"]["name"] = "domain_name";
    meta["other_root"] = "other";
    test->DataIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(), 3.456);
    EXPECT_EQ(exit->LastValue(), 3.456);
    auto last_meta = exit->LastMeta();
    ASSERT_TRUE(last_meta.Has("domain"));
    ASSERT_TRUE(last_meta.Get("domain").IsObject());
    ASSERT_TRUE(last_meta.Get("domain").HasMember("value"));
    ASSERT_TRUE(last_meta.Get("domain")["value"].IsDouble());
    EXPECT_EQ(last_meta.Get("domain")["value"].As<double>(), 3.456);

    ASSERT_TRUE(last_meta.Get("domain").HasMember("name"));
    ASSERT_TRUE(last_meta.Get("domain")["name"].IsString());
    EXPECT_EQ(last_meta.Get("domain")["name"].As<std::string>(), "domain_name");

    ASSERT_TRUE(last_meta.Has("other_root"));
    ASSERT_TRUE(last_meta.Get("other_root").IsString());
    EXPECT_EQ(last_meta.Get("other_root").As<std::string>(), "other");
  }

  {
    // rewrite other type (full path exists)
    meta["domain"]["value"] = "other_type";
    test->DataIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(), 4.456);
    EXPECT_EQ(exit->LastValue(), 4.456);
    auto last_meta = exit->LastMeta();
    ASSERT_TRUE(last_meta.Has("domain"));
    ASSERT_TRUE(last_meta.Get("domain").IsObject());
    ASSERT_TRUE(last_meta.Get("domain").HasMember("value"));
    ASSERT_TRUE(last_meta.Get("domain")["value"].IsDouble());
    EXPECT_EQ(last_meta.Get("domain")["value"].As<double>(), 4.456);
  }

  {
    // rewrite other value (full path exists)
    meta["domain"]["value"] = 1.1;
    test->DataIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(), 1.2);
    EXPECT_EQ(exit->LastValue(), 1.2);
    auto last_meta = exit->LastMeta();
    ASSERT_TRUE(last_meta.Has("domain"));
    ASSERT_TRUE(last_meta.Get("domain").IsObject());
    ASSERT_TRUE(last_meta.Get("domain").HasMember("value"));
    ASSERT_TRUE(last_meta.Get("domain")["value"].IsDouble());
    EXPECT_EQ(last_meta.Get("domain")["value"].As<double>(), 1.2);
  }
}

TEST(TestMetaFiller, TestStateMetaFiller) {
  formats::json::ValueBuilder builder;
  builder["type"] = "meta_filler";
  builder["id"] = "meta_filler";
  builder["path"].Resize(2);
  builder["path"][0] = "domain";
  builder["path"][1] = "description";
  auto test = std::make_shared<MetaFiller>(builder.ExtractValue());
  auto exit = std::make_shared<StateBuffer>("");
  test->OnStateOut(exit);

  formats::json::ValueBuilder meta{formats::common::Type::kObject};

  {
    // absent path
    test->StateIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(),
                  State{State::Value::kWarn, "1st state description"});
    EXPECT_EQ(exit->LastState(), State::Value::kWarn);
    auto last_meta = exit->LastMeta();
    ASSERT_TRUE(last_meta.Has("domain"));
    ASSERT_TRUE(last_meta.Get("domain").IsObject());
    ASSERT_TRUE(last_meta.Get("domain").HasMember("description"));
    ASSERT_TRUE(last_meta.Get("domain")["description"].IsString());
    EXPECT_EQ(last_meta.Get("domain")["description"].As<std::string>(),
              "1st state description");
  }

  {
    // not absent path
    meta["domain"]["name"] = "domain_name";
    meta["other_root"] = "other";
    test->StateIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(),
                  State{State::Value::kWarn, "2nd state description"});
    EXPECT_EQ(exit->LastState(), State::Value::kWarn);
    auto last_meta = exit->LastMeta();
    ASSERT_TRUE(last_meta.Has("domain"));
    ASSERT_TRUE(last_meta.Get("domain").IsObject());
    ASSERT_TRUE(last_meta.Get("domain").HasMember("description"));
    ASSERT_TRUE(last_meta.Get("domain")["description"].IsString());
    EXPECT_EQ(last_meta.Get("domain")["description"].As<std::string>(),
              "2nd state description");

    ASSERT_TRUE(last_meta.Get("domain").HasMember("name"));
    ASSERT_TRUE(last_meta.Get("domain")["name"].IsString());
    EXPECT_EQ(last_meta.Get("domain")["name"].As<std::string>(), "domain_name");

    ASSERT_TRUE(last_meta.Has("other_root"));
    ASSERT_TRUE(last_meta.Get("other_root").IsString());
    EXPECT_EQ(last_meta.Get("other_root").As<std::string>(), "other");
  }

  {
    // rewrite other type (full path exists)
    meta["domain"]["description"] = 0.123;
    test->StateIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(),
                  State{State::Value::kWarn, "3rd state description"});
    EXPECT_EQ(exit->LastState(), State::Value::kWarn);
    auto last_meta = exit->LastMeta();
    ASSERT_TRUE(last_meta.Has("domain"));
    ASSERT_TRUE(last_meta.Get("domain").IsObject());
    ASSERT_TRUE(last_meta.Get("domain").HasMember("description"));
    ASSERT_TRUE(last_meta.Get("domain")["description"].IsString());
    EXPECT_EQ(last_meta.Get("domain")["description"].As<std::string>(),
              "3rd state description");
  }

  {
    // rewrite other value (full path exists)
    meta["domain"]["description"] = "old description";
    test->StateIn(Meta{meta.ExtractValue()}, hejmdal::time::Now(),
                  State{State::Value::kWarn, "4th state description"});
    EXPECT_EQ(exit->LastState(), State::Value::kWarn);
    auto last_meta = exit->LastMeta();
    ASSERT_TRUE(last_meta.Has("domain"));
    ASSERT_TRUE(last_meta.Get("domain").IsObject());
    ASSERT_TRUE(last_meta.Get("domain").HasMember("description"));
    ASSERT_TRUE(last_meta.Get("domain")["description"].IsString());
    EXPECT_EQ(last_meta.Get("domain")["description"].As<std::string>(),
              "4th state description");
  }
}

}  // namespace hejmdal::radio::blocks
