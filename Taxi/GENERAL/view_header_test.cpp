#include <gtest/gtest.h>

#include <string_view>

#include <models/collections.hpp>

#include "view_header.hpp"

using eats_layout_constructor::models::CollectionContext;
using eats_layout_constructor::models::CollectionInfo;
using eats_layout_constructor::models::ColorConfig;
using eats_layout_constructor::static_widgets::StaticWidgetPtr;
using eats_layout_constructor::static_widgets::view_header::ViewHeader;

namespace {

CollectionContext MakeCollectionContext(
    const std::string& slug, const std::string& title,
    const std::optional<std::string>& description) {
  constexpr std::string_view kCollectionJson = R"(
  {
    "slug": "test",
    "title": "_",
    "actions": {
      "addMetaToPlace": [
        {
          "meta": {
            "description": "Description",
            "informationBlocks": []
          },
          "brand_slug": "brand_slug"
        }
      ]
    },
    "searchConditions": {
      "strategy": "by_brand_id",
      "arguments": {
        "brand_ids": [
          737
        ]
      }
    }
  }
  )";
  auto value = formats::json::FromString(kCollectionJson);
  formats::json::ValueBuilder builder(std::move(value));
  builder["title"] = title;
  if (description.has_value()) {
    builder["description"] = *description;
  }
  return {
      CollectionInfo::Parse(slug, eats_catalog_predicate::collection::Info{},
                            builder.ExtractValue()),
      ColorConfig{}};
}

StaticWidgetPtr MakeWidget(const CollectionContext& collection_context) {
  return std::make_unique<ViewHeader>(collection_context);
}

}  // namespace

TEST(ViewHader, FillFieldsFromCollection) {
  static const std::string kSlug = "my_collection";
  static const std::string kTitle = "MyTitle";
  static const std::string kDescription = "MyLongDescription";

  auto collection_context = MakeCollectionContext(kSlug, kTitle, kDescription);
  auto widget = MakeWidget(collection_context);

  formats::json::ValueBuilder layout_builder;
  widget->UpdateLayout(layout_builder);
  auto layout = layout_builder.ExtractValue();
  ASSERT_TRUE(layout["layout"].IsMissing());
  ASSERT_TRUE(layout["data"]["view_header"].IsObject());

  auto view_header = layout["data"]["view_header"];
  auto payload = view_header["payload"];
  auto meta = view_header["meta"];

  ASSERT_TRUE(payload.IsObject());
  ASSERT_TRUE(meta.IsObject());

  ASSERT_EQ(payload["title"].As<std::string>(), kTitle);
  ASSERT_EQ(payload["description"].As<std::string>(), kDescription);

  ASSERT_EQ(meta["slug"].As<std::string>(), kSlug);
}
