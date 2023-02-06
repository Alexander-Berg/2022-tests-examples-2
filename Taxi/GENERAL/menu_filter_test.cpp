#include <gtest/gtest.h>

#include "menu_filter.hpp"

namespace eats_rest_menu_storage::menu_filter {
namespace {

std::chrono::system_clock::time_point DeletedAt() {
  const static auto kDeletedAt =
      ::utils::datetime::Stringtime("2019-11-19T21:34:13.0+0000");
  return kDeletedAt;
}

}  // namespace

TEST(FilterHistoryEntities, Categories) {
  handlers::UpdateMenuRequest request{};
  auto& category_one = request.categories.emplace_back();
  category_one.origin_id = "category_1";
  category_one.legacy_id = 1;
  category_one.deleted_at = DeletedAt();
  auto& category_two = request.categories.emplace_back();
  category_two.origin_id = "category_1";
  category_two.legacy_id = 2;

  request = FilterHistoryEntities(std::move(request));
  ASSERT_EQ(request.categories.size(), 1);
  ASSERT_EQ(request.categories.front().legacy_id.value(), 2);
  ASSERT_FALSE(request.categories.front().deleted_at.has_value());
}

TEST(FilterHistoryEntities, Items) {
  handlers::UpdateMenuRequest request{};
  auto& item_one = request.items.emplace_back();
  item_one.origin_id = "item_1";
  item_one.legacy_id = 1;
  item_one.deleted_at = DeletedAt();
  auto& item_two = request.items.emplace_back();
  item_two.origin_id = "item_1";
  item_two.legacy_id = 2;

  request = FilterHistoryEntities(std::move(request));
  ASSERT_EQ(request.items.size(), 1);
  ASSERT_EQ(request.items.front().legacy_id.value(), 2);
  ASSERT_FALSE(request.items.front().deleted_at.has_value());
}

TEST(FilterHistoryEntities, ItemsMaxDeletedAt) {
  handlers::UpdateMenuRequest request{};
  auto& item_one = request.items.emplace_back();
  item_one.origin_id = "item_1";
  item_one.legacy_id = 1;
  item_one.deleted_at = DeletedAt();
  item_one.updated_at = DeletedAt();
  auto& item_two = request.items.emplace_back();
  item_two.origin_id = "item_1";
  item_two.legacy_id = 2;
  item_two.deleted_at = DeletedAt() + std::chrono::minutes{10};
  item_two.updated_at = DeletedAt() + std::chrono::minutes{10};

  request = FilterHistoryEntities(std::move(request));
  ASSERT_EQ(request.items.size(), 1);
  ASSERT_EQ(request.items.front().legacy_id.value(), 2);
  ASSERT_TRUE(request.items.front().deleted_at.has_value());
}

TEST(FilterHistoryEntities, ItemsMany) {
  handlers::UpdateMenuRequest request{};
  auto& item_one = request.items.emplace_back();
  item_one.origin_id = "item_1";
  item_one.legacy_id = 1;
  item_one.deleted_at = DeletedAt();
  auto& item_two = request.items.emplace_back();
  item_two.origin_id = "item_1";
  item_two.legacy_id = 2;
  item_two.deleted_at = DeletedAt() + std::chrono::minutes{10};
  auto& item_three = request.items.emplace_back();
  item_three.origin_id = "item_1";
  item_three.legacy_id = 3;

  request = FilterHistoryEntities(std::move(request));
  ASSERT_EQ(request.items.size(), 1);
  ASSERT_EQ(request.items.front().legacy_id.value(), 3);
  ASSERT_FALSE(request.items.front().deleted_at.has_value());
}

TEST(FilterHistoryEntities, ItemTwoNotDeleted) {
  handlers::UpdateMenuRequest request{};
  auto& item_one = request.items.emplace_back();
  item_one.origin_id = "item_1";
  item_one.legacy_id = 1;
  auto& item_two = request.items.emplace_back();
  item_two.origin_id = "item_1";
  item_two.legacy_id = 2;

  request = FilterHistoryEntities(std::move(request));
  ASSERT_EQ(request.items.size(), 1);
  ASSERT_EQ(request.items.front().legacy_id.value(), 1);
}

TEST(FilterHistoryEntities, InnerOptions) {
  handlers::UpdateMenuRequest request{};
  auto& item = request.items.emplace_back();
  item.inner_options.emplace();

  auto& option_one = item.inner_options->emplace_back();
  option_one.origin_id = "item_1";
  option_one.legacy_id = 1;
  option_one.deleted_at = DeletedAt();
  auto& option_two = item.inner_options->emplace_back();
  option_two.origin_id = "item_1";
  option_two.legacy_id = 2;

  request = FilterHistoryEntities(std::move(request));
  const auto& result_inner_opts = request.items.front().inner_options.value();
  ASSERT_EQ(result_inner_opts.size(), 1);
  ASSERT_EQ(result_inner_opts.front().legacy_id.value(), 2);
}

TEST(FilterHistoryEntities, OptionGroups) {
  handlers::UpdateMenuRequest request{};
  auto& item = request.items.emplace_back();
  item.options_groups.emplace();

  auto& group_one = item.options_groups->emplace_back();
  group_one.origin_id = "item_1";
  group_one.legacy_id = 1;
  group_one.deleted_at = DeletedAt();
  auto& group_two = item.options_groups->emplace_back();
  group_two.origin_id = "item_1";
  group_two.legacy_id = 2;

  request = FilterHistoryEntities(std::move(request));
  const auto& result_groups = request.items.front().options_groups.value();
  ASSERT_EQ(result_groups.size(), 1);
  ASSERT_EQ(result_groups.front().legacy_id.value(), 2);
}

TEST(FilterHistoryEntities, Options) {
  handlers::UpdateMenuRequest request{};
  auto& item = request.items.emplace_back();
  item.options_groups.emplace();
  auto& options = item.options_groups->emplace_back().options.emplace();

  auto& option_one = options.emplace_back();
  option_one.origin_id = "item_1";
  option_one.legacy_id = 1;
  option_one.deleted_at = DeletedAt();
  auto& option_two = options.emplace_back();
  option_two.origin_id = "item_1";
  option_two.legacy_id = 2;

  request = FilterHistoryEntities(std::move(request));
  const auto& result_options =
      request.items.front().options_groups->front().options.value();
  ASSERT_EQ(result_options.size(), 1);
  ASSERT_EQ(result_options.front().legacy_id.value(), 2);
}

}  // namespace eats_rest_menu_storage::menu_filter
