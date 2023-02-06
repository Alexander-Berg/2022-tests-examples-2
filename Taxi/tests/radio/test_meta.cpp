#include <gtest/gtest.h>

#include <radio/blocks/meta.hpp>
#include <userver/formats/json/inline.hpp>

namespace hejmdal::radio::blocks {

struct CheckMetaLevels {
  void Run() {
    formats::json::ValueBuilder json;
    json["m11"] = "m11";
    Level11(Meta(json.ExtractValue()));
  }

  void Level11(const Meta& meta) {
    {
      formats::json::ValueBuilder json;
      json["m21"] = "m21";
      json["overwrite_me"] = "to be overwritten";
      Level21(Meta(meta, json.ExtractValue()));
    }
    {
      formats::json::ValueBuilder json;
      json["m22"] = "m22";
      Level22(Meta(meta, json.ExtractValue()));
    }
    m11 = meta;
  }

  void Level21(const Meta& meta) {
    formats::json::ValueBuilder json;
    json["m31"] = "m31";
    json["overwrite_me"] = "overwritten in level 3";
    Level31(Meta(meta, json.ExtractValue()));
    m21 = meta;
  }

  void Level22(const Meta& meta) { m22 = meta; }

  void Level31(const Meta& meta) { m31 = meta; }

  Meta m11 = Meta::kNull;
  Meta m21 = Meta::kNull;
  Meta m22 = Meta::kNull;
  Meta m31 = Meta::kNull;
};

Meta TestGetData(const blocks::MetaDataKind which_data,
                 const bool add_block_data, const bool add_circuit_state_data) {
  if (!add_block_data && !add_circuit_state_data) {
    throw std::logic_error("impossible to create Meta without data");
  }

  formats::json::ValueBuilder builder;
  auto meta =
      add_circuit_state_data
          ? Meta(formats::json::MakeObject("circuit_data",
                                           "initial_circuit_val"))
          : Meta(formats::json::MakeObject("block_data", "initial_block_val"),
                 true);

  // 1. Add circuit state data
  if (add_circuit_state_data) {
    builder["circuit_data"] = "new_circuit_val";
    builder["params"] =
        formats::json::MakeArray(formats::json::MakeObject("param", 1));
    meta = Meta(builder.ExtractValue());
  }

  // 2. Add blocks data
  if (add_block_data) {
    builder["block_data"] = "new_block_val";
    builder["block_params"] = formats::json::MakeObject(
        "block_id", formats::json::MakeObject("param", 2));
    meta = Meta(meta, builder.ExtractValue(), true);
  }

  // 3. Add more circuit state data
  if (add_circuit_state_data) {
    builder["state_data"] = "state_value";
    meta = Meta(meta, builder.ExtractValue());
  }

  // 4. Build expected value and check
  switch (which_data) {
    case MetaDataKind::kBlocksData:
      builder["block_data"] = "new_block_val";
      builder["block_params"] = formats::json::MakeObject(
          "block_id", formats::json::MakeObject("param", 2));
      break;

    case MetaDataKind::kCircuitStateData:
      builder["circuit_data"] = "new_circuit_val";
      builder["params"] =
          formats::json::MakeArray(formats::json::MakeObject("param", 1));
      builder["state_data"] = "state_value";
      break;

    case MetaDataKind::kFullData:
      builder["circuit_data"] = "new_circuit_val";
      builder["params"] =
          formats::json::MakeArray(formats::json::MakeObject("param", 1));
      builder["state_data"] = "state_value";
      builder["block_data"] = "new_block_val";
      builder["block_params"] = formats::json::MakeObject(
          "block_id", formats::json::MakeObject("param", 2));
      break;
  }
  EXPECT_EQ(meta.Get(which_data), builder.ExtractValue());
  return meta;
}

TEST(TestMeta, TestExtraMeta) {
  CheckMetaLevels check;
  check.Run();

  EXPECT_EQ(check.m11.Has("m11"), true);
  EXPECT_EQ(check.m11.Has("m21"), false);
  EXPECT_EQ(check.m11.Has("m22"), false);
  EXPECT_EQ(check.m11.Has("m31"), false);

  EXPECT_EQ(formats::json::MakeObject("m11", "m11"), check.m11.Get());

  EXPECT_EQ(check.m21.Has("m11"), true);
  EXPECT_EQ(check.m21.Has("m21"), true);
  EXPECT_EQ(check.m21.Has("m22"), false);
  EXPECT_EQ(check.m21.Has("m31"), false);

  EXPECT_EQ(formats::json::MakeObject("m11", "m11", "m21", "m21",
                                      "overwrite_me", "to be overwritten"),
            check.m21.Get());

  EXPECT_EQ(check.m22.Has("m11"), true);
  EXPECT_EQ(check.m22.Has("m21"), false);
  EXPECT_EQ(check.m22.Has("m22"), true);
  EXPECT_EQ(check.m22.Has("m31"), false);

  EXPECT_EQ(formats::json::MakeObject("m11", "m11", "m22", "m22"),
            check.m22.Get());

  EXPECT_EQ(check.m31.Has("m11"), true);
  EXPECT_EQ(check.m31.Has("m21"), true);
  EXPECT_EQ(check.m31.Has("m22"), false);
  EXPECT_EQ(check.m31.Has("m31"), true);

  EXPECT_EQ(formats::json::MakeObject("m11", "m11", "m21", "m21", "m31", "m31",
                                      "overwrite_me", "overwritten in level 3"),
            check.m31.Get());
}

TEST(TestMeta, GetCircuitStateData) {
  TestGetData(MetaDataKind::kCircuitStateData, true, true);
}

TEST(TestMeta, GetBlocksData) {
  TestGetData(MetaDataKind::kBlocksData, true, true);
}

TEST(TestMeta, GetFullData) {
  TestGetData(MetaDataKind::kFullData, true, true);
}

TEST(TestMeta, MissingBlockData) {
  EXPECT_THROW(TestGetData(MetaDataKind::kBlocksData, false, true),
               except::NotFound);
}

TEST(TestMeta, MissingCircuitStateData) {
  EXPECT_THROW(TestGetData(MetaDataKind::kCircuitStateData, true, false),
               except::NotFound);
}

TEST(TestMeta, CheckGetData) {
  const auto meta = TestGetData(MetaDataKind::kFullData, true, true);
  EXPECT_EQ(meta.Get("circuit_data").As<std::string>(), "new_circuit_val");
  EXPECT_EQ(meta.Get("block_data").As<std::string>(), "new_block_val");
  EXPECT_THROW(meta.Get("wrong data").As<std::string>(), except::NotFound);
}

}  // namespace hejmdal::radio::blocks
