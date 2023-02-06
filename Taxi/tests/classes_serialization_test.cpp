#include <algorithm>
#include <vector>

#include <gtest/gtest.h>

#include <tariff-classes/classes_mapper.hpp>
#include <tariff-classes/classes_serialization.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

tariff_classes::Classes GetSomeClasses() {
  using tariff_classes::ClassType;
  return {ClassType::ChildTariff, ClassType::Business, ClassType::Econom};
}

tariff_classes::Classes GetEmptyClasses() { return {}; }

formats::json::Value GetSomeClassesJson() {
  using tariff_classes::ClassType;

  formats::json::ValueBuilder builder(formats::json::Type::kArray);
  builder.PushBack(
      tariff_classes::ClassesMapper::GetClassName(ClassType::ChildTariff));
  builder.PushBack(
      tariff_classes::ClassesMapper::GetClassName(ClassType::Business));
  builder.PushBack(
      tariff_classes::ClassesMapper::GetClassName(ClassType::Econom));
  return builder.ExtractValue();
}

formats::json::Value GetEmptyClassesJson() {
  formats::json::ValueBuilder builder(formats::json::Type::kArray);
  return builder.ExtractValue();
}

bool IsArrrayEqualUnordered(const formats::json::Value& lhs,
                            const formats::json::Value& rhs) {
  std::vector<std::string> lhs_vec;
  lhs_vec.reserve(lhs.GetSize());
  std::transform(
      lhs.begin(), lhs.end(), std::back_inserter(lhs_vec),
      [](const auto& value) { return formats::json::ToString(value); });
  std::sort(lhs_vec.begin(), lhs_vec.end());

  std::vector<std::string> rhs_vec;
  rhs_vec.reserve(rhs.GetSize());
  std::transform(
      rhs.begin(), rhs.end(), std::back_inserter(rhs_vec),
      [](const auto& value) { return formats::json::ToString(value); });
  std::sort(rhs_vec.begin(), rhs_vec.end());
  return lhs_vec == rhs_vec;
}

TEST(ClassesSerialization, Serialization) {
  auto some_classes_serialized =
      formats::json::ValueBuilder(GetSomeClasses()).ExtractValue();
  auto empty_classes_serialized =
      formats::json::ValueBuilder(GetEmptyClasses()).ExtractValue();

  ASSERT_TRUE(
      IsArrrayEqualUnordered(some_classes_serialized, GetSomeClassesJson()));
  ASSERT_TRUE(
      IsArrrayEqualUnordered(empty_classes_serialized, GetEmptyClassesJson()));
}

TEST(ClassesSerialization, Parse) {
  auto some_classes_parsed = GetSomeClassesJson().As<tariff_classes::Classes>();
  auto empty_classes_parsed =
      GetEmptyClassesJson().As<tariff_classes::Classes>();

  ASSERT_EQ(some_classes_parsed, GetSomeClasses());
  ASSERT_EQ(empty_classes_parsed, GetEmptyClasses());
}
