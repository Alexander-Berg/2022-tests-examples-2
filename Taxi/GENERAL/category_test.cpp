#include <gtest/gtest.h>

#include <eats-full-text-search-models/category.hpp>

#include <userver/formats/json/value_builder.hpp>
#include <userver/formats/parse/common_containers.hpp>

TEST(ParentCategory, Serialization) {
  eats_full_text_search_models::ParentCategory model{};
  model.id = 10;
  model.parent_id = 100;
  model.title = "Category Title";

  auto value = formats::json::ValueBuilder{model}.ExtractValue();
  auto restored_model =
      value.As<eats_full_text_search_models::ParentCategory>();

  ASSERT_EQ(restored_model.id, model.id);
  ASSERT_TRUE(restored_model.parent_id.has_value());
  ASSERT_EQ(restored_model.parent_id, model.parent_id);
  ASSERT_EQ(restored_model.title, model.title);
}

TEST(ParentCategory, OptionalParentId) {
  eats_full_text_search_models::ParentCategory model{};
  model.id = 10;
  model.title = "Category Title";

  auto value = formats::json::ValueBuilder{model}.ExtractValue();
  auto restored_model =
      value.As<eats_full_text_search_models::ParentCategory>();

  ASSERT_EQ(restored_model.id, model.id);
  ASSERT_FALSE(restored_model.parent_id.has_value());
  ASSERT_EQ(restored_model.parent_id, model.parent_id);
  ASSERT_EQ(restored_model.title, model.title);
}
