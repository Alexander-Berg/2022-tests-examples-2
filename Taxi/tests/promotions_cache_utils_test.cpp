#include <userver/utest/utest.hpp>

#include <optional>

#include <promotions_cache/utils/utils.hpp>
#include <tests/test_utils.hpp>

namespace promotions_cache::tests {

struct Internal {
  std::vector<std::string> vec;
};

struct Internal2 {
  Internal field;
};

struct Struct1 {
  int id;
  std::string str;
  Internal internal;
  Internal2 internal2;
};

struct Struct2 {
  int id;
  std::string str;
  std::optional<Internal> internal;
  std::optional<Internal2> internal2;
};

Internal Parse(const formats::json::Value& json, formats::parse::To<Internal>) {
  return Internal{json["vec"].As<std::vector<std::string>>()};
}

Internal2 Parse(const formats::json::Value& json,
                formats::parse::To<Internal2>) {
  return Internal2{json["field"].As<Internal>()};
}

Struct1 Parse(const formats::json::Value& json, formats::parse::To<Struct1>) {
  return Struct1{json["id"].As<int>(), json["str"].As<std::string>(),
                 json["internal"].As<Internal>(),
                 json["internal2"].As<Internal2>()};
}

Struct2 Parse(const formats::json::Value& json, formats::parse::To<Struct2>) {
  return Struct2{json["id"].As<int>(), json["str"].As<std::string>(),
                 json["internal"].As<std::optional<Internal>>(),
                 json["internal2"].As<std::optional<Internal2>>()};
}

formats::json::Value Serialize(const Internal& value,
                               formats::serialize::To<formats::json::Value>) {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);

  builder.EmplaceNocheck("vec", value.vec);

  return builder.ExtractValue();
}

formats::json::Value Serialize(const Internal2& value,
                               formats::serialize::To<formats::json::Value>) {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);

  builder.EmplaceNocheck("field", value.field);

  return builder.ExtractValue();
}

formats::json::Value Serialize(const Struct1& value,
                               formats::serialize::To<formats::json::Value>) {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);

  builder.EmplaceNocheck("id", value.id);
  builder.EmplaceNocheck("str", value.str);
  builder.EmplaceNocheck("internal", value.internal);
  builder.EmplaceNocheck("internal2", value.internal2);

  return builder.ExtractValue();
}

formats::json::Value Serialize(const Struct2& value,
                               formats::serialize::To<formats::json::Value>) {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);

  builder.EmplaceNocheck("id", value.id);
  builder.EmplaceNocheck("str", value.str);
  builder.EmplaceNocheck("internal", value.internal);
  builder.EmplaceNocheck("internal2", value.internal2);

  return builder.ExtractValue();
}

UTEST(PromotionsCacheUtilsTest, MappingTest) {
  Struct1 struct1{1, "s", {{"a", "b"}}, {{{"t"}}}};
  Struct2 struct2 =
      promotions_cache::utils::MapThroughJson<Struct1, Struct2>(struct1);
  Struct1 struct1_deserialized =
      promotions_cache::utils::MapThroughJson<Struct2, Struct1>(struct2);

  promotions_cache::tests::utils::AssertEqAsJson(struct1, struct2);
  promotions_cache::tests::utils::AssertEqAsJson(struct1, struct1_deserialized);
}

UTEST(PromotionsCacheUtilsTest, MappingWithDefaultsTest) {
  Struct2 struct2{1, "s", std::nullopt, std::nullopt};
  Struct1 struct1 = promotions_cache::utils::MapThroughJson<Struct2, Struct1>(
      struct2, [](formats::json::ValueBuilder& json_builder) {
        json_builder["internal"] = Internal{{"tmp"}};
        json_builder["internal2"] = Internal2{{{"tmp", "tmp2"}}};
      });

  Struct1 struct1_expected = Struct1{1, "s", {{"tmp"}}, {{{"tmp", "tmp2"}}}};

  promotions_cache::tests::utils::AssertEqAsJson(struct1, struct1_expected);
}

}  // namespace promotions_cache::tests
