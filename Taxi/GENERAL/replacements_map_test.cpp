#include <gtest/gtest.h>

#include "replacements_map.hpp"
#include "test_functions.hpp"

namespace {
using eats_picker_orders::models::AuthorType;
}

TEST(GetReplacementMapping, NoParams) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure({});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 0);
}

TEST(GetReplacementMapping, NoReplacements) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}}});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);

  ASSERT_EQ(result.size(), 2);
  ASSERT_EQ(result["item-1"].size(), 1);
  ASSERT_EQ(result["item-2"].size(), 1);
  ASSERT_EQ(result["item-1"][0].id, 1);
  ASSERT_EQ(result["item-2"][0].id, 2);
}

TEST(GetReplacementMapping, Sample) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}, {3, "item-3", 3, {}}},
       {{4, "item-4", 4, {1}}, {5, "item-2", 2, {}}, {6, "item-3", 3, {}}},
       {{7, "item-4", 4, {1}}, {8, "item-5", 8, {5}}, {9, "item-3", 3, {}}}});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 3);
  ASSERT_EQ(result["item-4"].size(), 1);
  ASSERT_EQ(result["item-5"].size(), 1);
  ASSERT_EQ(result["item-3"].size(), 1);
  ASSERT_EQ(result["item-4"][0].id, 1);
  ASSERT_EQ(result["item-5"][0].id, 5);
  ASSERT_EQ(result["item-3"][0].id, 9);
}

TEST(GetReplacementMapping, MultipleReplacements) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}, {3, "item-3", 3, {}}},
       {{4, "item-4", 4, {1}}, {5, "item-5", 5, {2}}, {6, "item-3", 3, {}}},
       {{7, "item-4", 4, {1}}, {8, "item-5", 5, {2}}, {9, "item-6", 9, {6}}},
       {{10, "item-1", 10, {7}},
        {11, "item-2", 11, {8}},
        {12, "item-3", 12, {9}}}});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 3);
  ASSERT_EQ(result["item-1"].size(), 1);
  ASSERT_EQ(result["item-2"].size(), 1);
  ASSERT_EQ(result["item-3"].size(), 1);
  ASSERT_EQ(result["item-1"][0].id, 1);
  ASSERT_EQ(result["item-2"][0].id, 2);
  ASSERT_EQ(result["item-3"][0].id, 6);
}

TEST(GetReplacementMapping, SelfReplacement) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure(
      {{{1, "item-1", 1, {}}},
       {{4, "item-1", 4, {1}}},
       {{7, "item-1", 7, {4}}}});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result["item-1"].size(), 1);
  ASSERT_EQ(result["item-1"][0].id, 1);
}

TEST(GetReplacementMapping, ReplaceManyToOne) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure(
      {{{1, "item-1", 1, {}},
        {2, "item-2", 2, {}},
        {3, "item-3", 3, {}},
        {4, "item-4", 4, {}}},
       {{5, "item-5", 5, {1, 2}}, {6, "item-6", 6, {3, 4}}},
       {{7, "item-1", 7, {5, 6}}}});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result["item-1"].size(), 4);
  ASSERT_EQ(result["item-1"][0].id, 1);
  ASSERT_EQ(result["item-1"][1].id, 2);
  ASSERT_EQ(result["item-1"][2].id, 3);
  ASSERT_EQ(result["item-1"][3].id, 4);
}

TEST(GetReplacementMapping, ReplaceOneToMany) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure(
      {{{1, "item-1", 1, {}}}, {{2, "item-2", 2, {1}}, {3, "item-3", 3, {1}}}});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 2);
  ASSERT_EQ(result["item-2"].size(), 1);
  ASSERT_EQ(result["item-2"][0].id, 1);
  ASSERT_EQ(result["item-3"].size(), 1);
  ASSERT_EQ(result["item-3"][0].id, 1);
}

TEST(GetReplacementMapping, ReplaceManyToOneToMany) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}},
       {{3, "item-3", 3, {1, 2}}},
       {{4, "item-4", 4, {3}}, {5, "item-5", 5, {3}}}});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 2);
  ASSERT_EQ(result["item-4"].size(), 2);
  ASSERT_EQ(result["item-4"][0].id, 1);
  ASSERT_EQ(result["item-4"][1].id, 2);
  ASSERT_EQ(result["item-5"].size(), 2);
  ASSERT_EQ(result["item-5"][0].id, 1);
  ASSERT_EQ(result["item-5"][1].id, 2);
}

TEST(GetReplacementMapping, ReplaceOneToManyToOne) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure(
      {{{1, "item-1", 1, {}}},
       {{2, "item-2", 2, {1}}, {3, "item-3", 3, {1}}},
       {{4, "item-4", 4, {2, 3}}}});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result["item-4"].size(), 1);
  ASSERT_EQ(result["item-4"][0].id, 1);
}

TEST(GetReplacementMapping, PartiallyOverlappingReplace) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure(
      {{{1, "item-1", 1, {}}, {2, "item-2", 2, {}}, {3, "item-3", 3, {}}},
       {{4, "item-4", 4, {1, 2}}, {5, "item-5", 5, {2, 3}}},
       {{6, "item-6", 6, {4}}, {7, "item-7", 7, {5}}}});
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 2);
  ASSERT_EQ(result["item-6"].size(), 2);
  ASSERT_EQ(result["item-6"][0].id, 1);
  ASSERT_EQ(result["item-6"][1].id, 2);
  ASSERT_EQ(result["item-7"].size(), 2);
  ASSERT_EQ(result["item-7"][0].id, 2);
  ASSERT_EQ(result["item-7"][1].id, 3);
}

TEST(GetReplacementMapping, NoOriginalVersion) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure({
      {},
      {{2, "item-2", 2, {1}}},
      {{3, "item-3", 3, {2}}, {4, "item-4", 4, {1}}},
  });
  auto result = replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(result.size(), 2);
  ASSERT_EQ(result["item-3"].size(), 1);
  ASSERT_EQ(result["item-3"][0].id, 2);
  ASSERT_EQ(result["item-4"].size(), 1);
  ASSERT_EQ(result["item-4"][0].id, 4);
}

TEST(GetReplacementMapping, DifferentPickers) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure({
      {{1, "item-1", 1, {}}},
      // добавление первым сборщиком по старой логике
      {{2, "item-1", 2, {}, "picker-1", std::nullopt}},
      // замена вторым сборщиком по новой логике
      {{3, "item-2", 3, {2}, "picker-2", AuthorType::kPicker}},
      // замена первым сборщиком по новой логике
      {{4, "item-3", 3, {2}, "picker-1", AuthorType::kPicker}},
  });
  auto first_picker_result =
      replacements_map::GetReplacementMapping(items, "picker-1");
  ASSERT_EQ(first_picker_result.size(), 1);
  ASSERT_EQ(first_picker_result["item-3"].size(), 1);
  ASSERT_EQ(first_picker_result["item-3"][0].id, 2);
  auto second_picker_result =
      replacements_map::GetReplacementMapping(items, "picker-2");
  ASSERT_EQ(second_picker_result.size(), 1);
  ASSERT_EQ(second_picker_result["item-2"].size(), 1);
  ASSERT_EQ(second_picker_result["item-2"][0].id, 2);
  auto third_picker_result =
      replacements_map::GetReplacementMapping(items, "picker-3");
  ASSERT_EQ(third_picker_result.size(), 1);
  ASSERT_EQ(third_picker_result["item-1"].size(), 1);
  ASSERT_EQ(third_picker_result["item-1"][0].id, 2);
  auto no_picker_result =
      replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(no_picker_result.size(), 1);
  ASSERT_EQ(no_picker_result["item-1"].size(), 1);
  ASSERT_EQ(no_picker_result["item-1"][0].id, 2);
}

TEST(GetReplacementMapping, CustomerChange) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure({
      {{1, "item-1", 1, {}}},
      // добавление первым сборщиком
      {{2, "item-1", 2, {}, "picker-1", AuthorType::kPicker}},
      // замена покупателем
      {{3, "item-2", 3, {2}, "customer", AuthorType::kCustomer}},
      // замена вторым сборщиком
      {{4, "item-3", 4, {3}, "picker-2", AuthorType::kPicker}},
  });
  auto first_picker_result =
      replacements_map::GetReplacementMapping(items, "picker-1");
  ASSERT_EQ(first_picker_result.size(), 1);
  ASSERT_EQ(first_picker_result["item-2"].size(), 1);
  ASSERT_EQ(first_picker_result["item-2"][0].id, 2);
  auto second_picker_result =
      replacements_map::GetReplacementMapping(items, "picker-2");
  ASSERT_EQ(second_picker_result.size(), 1);
  ASSERT_EQ(second_picker_result["item-3"].size(), 1);
  ASSERT_EQ(second_picker_result["item-3"][0].id, 2);
  auto third_picker_result =
      replacements_map::GetReplacementMapping(items, "picker-3");
  ASSERT_EQ(third_picker_result.size(), 1);
  ASSERT_EQ(third_picker_result["item-2"].size(), 1);
  ASSERT_EQ(third_picker_result["item-2"][0].id, 2);
  auto no_picker_result =
      replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(no_picker_result.size(), 1);
  ASSERT_EQ(no_picker_result["item-2"].size(), 1);
  ASSERT_EQ(no_picker_result["item-2"][0].id, 2);
}

TEST(GetReplacementMapping, SystemChanges) {
  auto items = eats_picker_orders::test::MakeOrderItemWithMeasure({
      {{1, "item-1", 1, {}}},
      // системное добавление от имени первого сборщика
      {{2, "item-1", 2, {}, "picker-1", AuthorType::kSystem}},
      // системная замена от имени покупателя
      {{3, "item-2", 3, {1}, std::nullopt, AuthorType::kSystem}},
      // системная замена от имени второго сборщика
      {{4, "item-3", 4, {2}, "picker-2", AuthorType::kSystem}},
      // системная замена от имени первого сборщика
      {{5, "item-4", 5, {2}, "picker-1", AuthorType::kSystem}},
  });
  auto first_picker_result =
      replacements_map::GetReplacementMapping(items, "picker-1");
  ASSERT_EQ(first_picker_result.size(), 1);
  ASSERT_EQ(first_picker_result["item-4"].size(), 1);
  ASSERT_EQ(first_picker_result["item-4"][0].id, 2);
  auto second_picker_result =
      replacements_map::GetReplacementMapping(items, "picker-2");
  ASSERT_EQ(second_picker_result.size(), 1);
  ASSERT_EQ(second_picker_result["item-3"].size(), 1);
  ASSERT_EQ(second_picker_result["item-3"][0].id, 2);
  auto third_picker_result =
      replacements_map::GetReplacementMapping(items, "picker-3");
  ASSERT_EQ(third_picker_result.size(), 1);
  ASSERT_EQ(third_picker_result["item-2"].size(), 1);
  ASSERT_EQ(third_picker_result["item-2"][0].id, 1);
  auto no_picker_result =
      replacements_map::GetReplacementMapping(items, std::nullopt);
  ASSERT_EQ(no_picker_result.size(), 1);
  ASSERT_EQ(no_picker_result["item-2"].size(), 1);
  ASSERT_EQ(no_picker_result["item-2"][0].id, 1);
}
