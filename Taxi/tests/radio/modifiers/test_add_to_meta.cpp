#include <gtest/gtest.h>

#include "../mock_block.hpp"

#include <radio/blocks/commutation/entry_points.hpp>

namespace hejmdal::radio::blocks {

namespace {

class MetaCheckEnv : public MockBlock {
 public:
  MetaCheckEnv(formats::json::Value add_to_meta, bool save_to_db)
      : last_meta(Meta::kNull), entry("") {
    formats::json::ValueBuilder json;
    json["type"] = "state_entry_point";
    json["id"] = "test_entry";
    json["additional_meta"] = add_to_meta;
    json["save_additional_meta_to_db"] = save_to_db;
    auto description = json.ExtractValue();
    entry = StateEntryPoint{description};
    entry.OnStateOut(this);
  }

  virtual void StateIn(const Meta& meta, const time::TimePoint&,
                       const State&) override {
    last_meta = meta;
  }

  Meta last_meta;

  StateEntryPoint entry;
};

MetaCheckEnv CreateEnv(formats::json::Value add_to_meta, bool save_to_db) {
  return MetaCheckEnv{add_to_meta, save_to_db};
}

static const formats::json::Value kTestJson = [] {
  formats::json::ValueBuilder json;
  json["hello"] = "world";
  json["goodbye"] =
      formats::json::MakeObject("cruel", "world", "forever", "and ever");
  return json.ExtractValue();
}();

}  // namespace

TEST(TestAddToMetaBlock, TestAddSaveToDb) {
  auto env = CreateEnv(kTestJson, true);

  env.entry.StateIn(
      Meta{formats::json::MakeObject("global_stuff", "some stuff")},
      time::TimePoint{}, State::kOk);

  auto circuit_data = env.last_meta.Get(MetaDataKind::kCircuitStateData);

  EXPECT_TRUE(circuit_data.HasMember("global_stuff"));
  ASSERT_TRUE(circuit_data.HasMember("hello"));
  EXPECT_EQ(circuit_data["hello"].As<std::string>(), "world");
  ASSERT_TRUE(circuit_data.HasMember("goodbye"));
  EXPECT_EQ(circuit_data["goodbye"],
            formats::json::MakeObject("cruel", "world", "forever", "and ever"));
}

TEST(TestAddToMetaBlock, TestAddNotSaveToDb) {
  auto env = CreateEnv(kTestJson, false);

  env.entry.StateIn(
      Meta{formats::json::MakeObject("global_stuff", "some stuff")},
      time::TimePoint{}, State::kOk);

  {
    auto circuit_data = env.last_meta.Get(MetaDataKind::kCircuitStateData);

    EXPECT_TRUE(circuit_data.HasMember("global_stuff"));
    EXPECT_FALSE(circuit_data.HasMember("hello"));
    EXPECT_FALSE(circuit_data.HasMember("goodbye"));
  }
  {
    auto blocks_data = env.last_meta.Get(MetaDataKind::kBlocksData);
    ASSERT_TRUE(blocks_data.HasMember("hello"));
    EXPECT_EQ(blocks_data["hello"].As<std::string>(), "world");
    ASSERT_TRUE(blocks_data.HasMember("goodbye"));
    EXPECT_EQ(
        blocks_data["goodbye"],
        formats::json::MakeObject("cruel", "world", "forever", "and ever"));
  }
}

}  // namespace hejmdal::radio::blocks
