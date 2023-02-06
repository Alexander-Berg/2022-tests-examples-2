#include <gtest/gtest.h>

#include <userver/formats/json/inline.hpp>

#include <radio/blocks/meta.hpp>

namespace hejmdal::radio::blocks {

TEST(TestMetaData, Merge) {
  auto root_meta = Meta(formats::json::MakeObject("some_key", "some_value"));
  auto child_meta_1 = Meta(
      root_meta,
      formats::json::MakeObject(
          "block_params",
          formats::json::MakeObject(
              "some_block_id", formats::json::MakeObject("param1", "value1"))));
  auto child_meta_2 =
      Meta(child_meta_1,
           formats::json::MakeObject(
               "block_params",
               formats::json::MakeObject(
                   "some_block_id", formats::json::MakeObject("param2", 42))));
  auto child_meta_3 = Meta(
      child_meta_2,
      formats::json::MakeObject(
          "block_params", formats::json::MakeObject(
                              "other_block_id", formats::json::MakeObject(
                                                    "param1", "other_value"))));

  auto merged_value = child_meta_3.Get();
  auto expected = formats::json::MakeObject(
      "some_key", "some_value", "block_params",
      formats::json::MakeObject(
          "some_block_id",
          formats::json::MakeObject("param1", "value1", "param2", 42),
          "other_block_id",
          formats::json::MakeObject("param1", "other_value")));
  EXPECT_EQ(expected, merged_value);
}

TEST(TestMetaData, Merge2) {
  auto root_value = formats::json::MakeObject("some_key", "some_value");
  auto root_meta = Meta(root_value);
  auto child_meta_value = formats::json::Value{};
  auto child_meta = Meta(root_meta, child_meta_value);
  auto expected = formats::json::MakeObject("some_key", "some_value");
  EXPECT_EQ(expected, child_meta.Get());
}

}  // namespace hejmdal::radio::blocks
