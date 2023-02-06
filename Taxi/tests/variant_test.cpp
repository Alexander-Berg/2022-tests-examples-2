// todo move to agl

#include <agl/core/executer_state.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/io/json.hpp>

#include <userver/formats/bson/value_builder.hpp>
#include <userver/utest/utest.hpp>

#include <limits>

namespace agl::core {

static const std::vector<std::string> kSources;
static ExecuterState kExecuterState;

namespace {

template <typename T>
T ScalarGetter(const agl::core::Variant&) {
  return T();
}
template <>
bool ScalarGetter<>(const agl::core::Variant& v) {
  return v.AsBool();
}
template <>
int64_t ScalarGetter<>(const agl::core::Variant& v) {
  return v.AsInt();
}
template <>
double ScalarGetter<>(const agl::core::Variant& v) {
  return v.AsDouble();
}
template <>
std::string ScalarGetter<>(const agl::core::Variant& v) {
  return v.AsString();
}

template <typename T>
void ScalarConstantHelper(T value) {
  agl::core::variant::Dependencies deps;
  agl::core::Variant v(value);
  formats::json::Value json = formats::json::ValueBuilder(value).ExtractValue();

  EXPECT_TRUE(v.IsConstant());
  EXPECT_FALSE(v.IsNone());
  EXPECT_TRUE(deps.IsEmpty());
  EXPECT_EQ(json, variant::io::EncodeJson(v, kExecuterState));
  EXPECT_EQ(ScalarGetter<T>(v), value);

  agl::core::Variant evaluated = v.Evaluate(kExecuterState);
  evaluated.GetDependencies(deps);
  EXPECT_TRUE(evaluated.IsConstant());
  EXPECT_FALSE(evaluated.IsNone());
  EXPECT_TRUE(deps.IsEmpty());
  EXPECT_EQ(json, variant::io::EncodeJson(evaluated, kExecuterState));
  EXPECT_EQ(ScalarGetter<T>(evaluated), value);
  EXPECT_EQ(ScalarGetter<T>(evaluated), ScalarGetter<T>(v));
}

}  // namespace

TEST(TestVariant, ScalarConstants) {
  {
    agl::core::variant::Dependencies deps;
    agl::core::Variant v;
    v.GetDependencies(deps);
    EXPECT_TRUE(v.IsConstant());
    EXPECT_TRUE(v.IsNone());
    EXPECT_TRUE(deps.IsEmpty());
    EXPECT_EQ(formats::json::Value(),
              variant::io::EncodeJson(v, kExecuterState));

    agl::core::Variant evaluated = v.Evaluate(kExecuterState);
    evaluated.GetDependencies(deps);
    EXPECT_TRUE(evaluated.IsConstant());
    EXPECT_TRUE(evaluated.IsNone());
    EXPECT_TRUE(deps.IsEmpty());
    EXPECT_EQ(formats::json::Value(),
              variant::io::EncodeJson(evaluated, kExecuterState));
  }  // namespace core=core::api_proxy;

  ScalarConstantHelper<bool>(true);
  ScalarConstantHelper<bool>(false);

  ScalarConstantHelper<int64_t>(0);
  ScalarConstantHelper<int64_t>(-1);
  ScalarConstantHelper<int64_t>(1);
  ScalarConstantHelper<int64_t>(std::numeric_limits<int64_t>::min());
  ScalarConstantHelper<int64_t>(std::numeric_limits<int64_t>::max());

  ScalarConstantHelper<double>(0);
  ScalarConstantHelper<double>(3.1415);
  ScalarConstantHelper<double>(-0.123456789);

  ScalarConstantHelper<std::string>("");
  ScalarConstantHelper<std::string>("test");
}

TEST(TestVariant, ListConstants) {
  {
    formats::json::Value json =
        formats::json::ValueBuilder(formats::json::Type::kArray).ExtractValue();
    agl::core::variant::Dependencies deps;
    agl::core::Variant v = agl::core::Variant::List();
    EXPECT_TRUE(v.IsConstant());
    EXPECT_FALSE(v.IsNone());
    EXPECT_TRUE(deps.IsEmpty());
    EXPECT_EQ(json, variant::io::EncodeJson(v, kExecuterState));
  }  // namespace core=core::api_proxy;

  {
    agl::core::variant::Dependencies deps;
    agl::core::Variant::List list;
    list.PushBack(true);
    list.PushBack(int64_t(42));
    list.PushBack(agl::core::Variant());
    list.PushBack(std::string("unit test"));
    list.PushBack("string constant");
    {
      auto sublist = agl::core::Variant::List() << "test" << int64_t(18);
      list.PushBack(std::move(sublist));
    }
    {
      auto subobj = agl::core::Variant::Map().Set("a", 3.1415).Set("b", "ok");
      list.PushBack(std::move(subobj));
    }
    agl::core::Variant v = list;
    EXPECT_TRUE(v.IsConstant());
    EXPECT_FALSE(v.IsNone());
    EXPECT_TRUE(deps.IsEmpty());

    auto json = formats::json::ValueBuilder(formats::json::Type::kArray);
    json.PushBack(true);
    json.PushBack(42);
    json.PushBack(formats::json::ValueBuilder());
    json.PushBack(std::string("unit test"));
    json.PushBack("string constant");

    {
      auto sublist = formats::json::ValueBuilder(formats::json::Type::kArray);
      sublist.PushBack("test");
      sublist.PushBack(18);
      json.PushBack(std::move(sublist));
    }

    {
      auto subobj = formats::json::ValueBuilder(formats::json::Type::kObject);
      subobj["a"] = 3.1415;
      subobj["b"] = std::string("ok");
      json.PushBack(std::move(subobj));
    }

    auto json_value = json.ExtractValue();
    EXPECT_EQ(json_value, variant::io::EncodeJson(v, kExecuterState));

    agl::core::Variant evaluated = v.Evaluate(kExecuterState);
    evaluated.GetDependencies(deps);
    EXPECT_TRUE(evaluated.IsConstant());
    EXPECT_FALSE(evaluated.IsNone());
    EXPECT_TRUE(deps.IsEmpty());
    EXPECT_EQ(json_value, variant::io::EncodeJson(evaluated, kExecuterState));
  }
}

TEST(TestVariant, MapConstants) {
  {
    formats::json::Value json =
        formats::json::ValueBuilder(formats::json::Type::kObject)
            .ExtractValue();
    agl::core::variant::Dependencies deps;
    agl::core::Variant v = agl::core::Variant::Map();
    EXPECT_TRUE(v.IsConstant());
    EXPECT_FALSE(v.IsNone());
    EXPECT_TRUE(deps.IsEmpty());
    EXPECT_EQ(json, variant::io::EncodeJson(v, kExecuterState));
  }  // namespace core=core::api_proxy;

  {
    agl::core::variant::Dependencies deps;
    agl::core::Variant::Map map;
    map.Set("true", true);
    map.Set("false", false);
    map.Set("seven", int64_t(7));
    map.Set("pi", 3.14159265358979323846);
    map.Set("string", "hello world");
    map.Set("list", agl::core::Variant::List()
                        << "abc" << false << "42" << 42.42);

    auto json = formats::json::ValueBuilder(formats::json::Type::kObject);
    json["true"] = true;
    json["false"] = false;
    json["seven"] = 7;
    json["pi"] = 3.14159265358979323846;
    json["string"] = "hello world";

    auto sublist = formats::json::ValueBuilder(formats::json::Type::kArray);
    sublist.PushBack("abc");
    sublist.PushBack(false);
    sublist.PushBack("42");
    sublist.PushBack(42.42);
    json["list"] = std::move(sublist);

    auto json_value = json.ExtractValue();

    agl::core::Variant v(std::move(map));
    EXPECT_TRUE(v.IsConstant());
    EXPECT_FALSE(v.IsNone());
    EXPECT_TRUE(deps.IsEmpty());
    EXPECT_EQ(json_value, variant::io::EncodeJson(v, kExecuterState));

    agl::core::Variant evaluated = v.Evaluate(kExecuterState);
    evaluated.GetDependencies(deps);
    EXPECT_TRUE(evaluated.IsConstant());
    EXPECT_FALSE(evaluated.IsNone());
    EXPECT_TRUE(deps.IsEmpty());
    EXPECT_EQ(json_value, variant::io::EncodeJson(evaluated, kExecuterState));
  }
}

TEST(TestVariant, EqualsSimple) {
  agl::core::Variant sample_none;
  agl::core::Variant sample_false(false);
  agl::core::Variant sample_true(true);
  agl::core::Variant sample_int0(int64_t(0));
  agl::core::Variant sample_int42(int64_t(42));
  agl::core::Variant sample_double0(double(0));
  agl::core::Variant sample_double11(double(11.0));
  agl::core::Variant sample_string_empty(std::string(""));
  agl::core::Variant sample_string_test(std::string("test"));
  agl::core::Variant sample_list_empty((agl::core::Variant::List()));
  agl::core::Variant sample_list_non_empty(agl::core::Variant::List()
                                           << std::string("foo")
                                           << int64_t(100500) << false);
  agl::core::Variant sample_map_empty((agl::core::Variant::Map()));
  agl::core::Variant sample_map_non_empty(agl::core::Variant::Map()
                                              .Set("key1", "value1")
                                              .Set("int", int64_t(42))
                                              .Set("bool", true));

  agl::core::Variant sample_json_null((formats::json::Value()));
  agl::core::Variant sample_json_false(
      formats::json::ValueBuilder(false).ExtractValue());
  agl::core::Variant sample_json_true(
      formats::json::ValueBuilder(true).ExtractValue());
  agl::core::Variant sample_json_int0(
      formats::json::ValueBuilder(int64_t(0)).ExtractValue());
  agl::core::Variant sample_json_int42(
      formats::json::ValueBuilder(int64_t(42)).ExtractValue());
  agl::core::Variant sample_json_double0(
      formats::json::ValueBuilder(double(0)).ExtractValue());
  agl::core::Variant sample_json_double11(
      formats::json::ValueBuilder(double(11.0)).ExtractValue());
  agl::core::Variant sample_json_string_empty(
      formats::json::ValueBuilder("").ExtractValue());
  agl::core::Variant sample_json_string_test(
      formats::json::ValueBuilder("test").ExtractValue());
  agl::core::Variant sample_json_list_empty(
      formats::json::ValueBuilder(formats::json::Type::kArray).ExtractValue());
  formats::json::ValueBuilder list_builder(formats::json::Type::kArray);
  list_builder.PushBack("foo");
  list_builder.PushBack(int64_t(100500));
  list_builder.PushBack(false);
  agl::core::Variant sample_json_list_non_empty(list_builder.ExtractValue());
  agl::core::Variant sample_json_map_empty(
      formats::json::ValueBuilder(formats::json::Type::kObject).ExtractValue());
  formats::json::ValueBuilder map_builder(formats::json::Type::kObject);
  map_builder["key1"] = "value1";
  map_builder["int"] = int64_t(42);
  map_builder["bool"] = true;
  agl::core::Variant sample_json_map_non_empty(map_builder.ExtractValue());

  agl::core::Variant sample_nested1(
      agl::core::Variant::List()
      << std::string("foo") << int64_t(100500)
      << (agl::core::Variant::List() << "bar" << true) << false);
  formats::json::ValueBuilder sample_nested1_sub_list_builder(
      formats::json::Type::kArray);
  sample_nested1_sub_list_builder.PushBack("bar");
  sample_nested1_sub_list_builder.PushBack(true);
  formats::json::ValueBuilder sample_nested1_list_builder(
      formats::json::Type::kArray);
  sample_nested1_list_builder.PushBack("foo");
  sample_nested1_list_builder.PushBack(int64_t(100500));
  sample_nested1_list_builder.PushBack(
      sample_nested1_sub_list_builder.ExtractValue());
  sample_nested1_list_builder.PushBack(false);
  agl::core::Variant sample_json_nested1(
      sample_nested1_list_builder.ExtractValue());

  formats::json::ValueBuilder sample_nested2_inner_json_builder;
  sample_nested2_inner_json_builder["test"] = "value";
  sample_nested2_inner_json_builder["int"] = 116;
  variant::io::JsonPromise sample_nested2_inner_json(
      sample_nested2_inner_json_builder.ExtractValue());
  agl::core::Variant sample_nested2(
      agl::core::Variant::List()
      << sample_nested2_inner_json << std::string("foo") << int64_t(100500)
      << (agl::core::Variant::List()
          << "bar" << true << sample_nested2_inner_json)
      << (agl::core::Variant::Map()
              .Set("foo", "bar")
              .Set("false", false)
              .Set("json", sample_nested2_inner_json))
      << false);
  formats::json::ValueBuilder sample_nested2_sub_list_builder(
      formats::json::Type::kArray);
  sample_nested2_sub_list_builder.PushBack("bar");
  sample_nested2_sub_list_builder.PushBack(true);
  sample_nested2_sub_list_builder.PushBack(sample_nested2_inner_json.AsJson());
  formats::json::ValueBuilder sample_nested2_sub_map_builder(
      formats::json::Type::kObject);
  sample_nested2_sub_map_builder["foo"] = "bar";
  sample_nested2_sub_map_builder["false"] = false;
  sample_nested2_sub_map_builder["json"] = sample_nested2_inner_json.AsJson();
  formats::json::ValueBuilder sample_nested2_list_builder(
      formats::json::Type::kArray);
  sample_nested2_list_builder.PushBack(sample_nested2_inner_json.AsJson());
  sample_nested2_list_builder.PushBack("foo");
  sample_nested2_list_builder.PushBack(int64_t(100500));
  sample_nested2_list_builder.PushBack(
      sample_nested2_sub_list_builder.ExtractValue());
  sample_nested2_list_builder.PushBack(
      sample_nested2_sub_map_builder.ExtractValue());
  sample_nested2_list_builder.PushBack(false);
  agl::core::Variant sample_json_nested2(
      variant::io::JsonPromise(sample_nested2_list_builder.ExtractValue()));

  const std::vector<const agl::core::Variant*> kAll{
      &sample_none,
      &sample_false,
      &sample_true,
      &sample_int0,
      &sample_int42,
      &sample_double0,
      &sample_double11,
      &sample_string_empty,
      &sample_string_test,
      &sample_list_empty,
      &sample_list_non_empty,
      &sample_map_empty,
      &sample_map_non_empty,
      &sample_nested1,
      &sample_nested2,

      &sample_json_null,
      &sample_json_false,
      &sample_json_true,
      &sample_json_int0,
      &sample_json_int42,
      &sample_json_double0,
      &sample_json_double11,
      &sample_json_string_empty,
      &sample_json_string_test,
      &sample_json_list_empty,
      &sample_json_list_non_empty,
      &sample_json_map_empty,
      &sample_json_map_non_empty,
      &sample_json_nested1,
      &sample_json_nested2,
  };

  const std::vector<
      std::pair<const agl::core::Variant*, const agl::core::Variant*>>
      kEqual{
          {&sample_none, &sample_json_null},
          {&sample_false, &sample_json_false},
          {&sample_true, &sample_json_true},
          {&sample_int0, &sample_json_int0},
          {&sample_int0, &sample_json_double0},
          {&sample_int42, &sample_json_int42},
          {&sample_json_int0, &sample_json_double0},
          {&sample_double0, &sample_json_double0},
          {&sample_double0, &sample_json_int0},
          {&sample_double11, &sample_json_double11},
          {&sample_string_empty, &sample_json_string_empty},
          {&sample_string_test, &sample_json_string_test},
          {&sample_list_empty, &sample_json_list_empty},
          {&sample_list_non_empty, &sample_json_list_non_empty},
          {&sample_map_empty, &sample_json_map_empty},
          {&sample_map_non_empty, &sample_json_map_non_empty},
          {&sample_nested1, &sample_json_nested1},
          {&sample_nested2, &sample_json_nested2},
      };

  for (const auto& pair : kEqual) {
    EXPECT_TRUE(pair.first->Equals(*pair.second))
        << " failed `first == second` at position #"
        << std::distance(&kEqual.front(), &pair);
    EXPECT_TRUE(pair.second->Equals(*pair.first))
        << " failed `second == first` at position #"
        << std::distance(&kEqual.front(), &pair);
  }

  for (const agl::core::Variant* value : kAll) {
    EXPECT_TRUE(value->Equals(*value));
  }

  int i_a = 0;
  for (const agl::core::Variant* a : kAll) {
    int i_b = 0;
    for (const agl::core::Variant* b : kAll) {
      auto eq1 = std::make_pair(a, b);
      auto eq2 = std::make_pair(b, a);
      if (std::find(kEqual.cbegin(), kEqual.cend(), eq1) == kEqual.cend() &&
          std::find(kEqual.cbegin(), kEqual.cend(), eq2) == kEqual.cend() &&
          a != b) {
        EXPECT_FALSE(a->Equals(*b))
            << "kAll[" << i_a << "] == kAll[" << i_b << "]";
        EXPECT_FALSE(b->Equals(*a))
            << "kAll[" << i_b << "] == kAll[" << i_a << "]";
      }
      i_b++;
    }
    i_a++;
  }
}

namespace {

template <typename T>
void CheckSameListFromIterator(const std::vector<T>& origin,
                               agl::core::Variant variant) {
  std::vector<T> res;
  for (const auto& value : variant.IterateAsList()) {
    res.push_back(value.As<T>());
  }

  ASSERT_EQ(res, origin);
}

template <typename T>
std::tuple<agl::core::Variant, agl::core::Variant, agl::core::Variant>
MakeVariantJsonBsonFromList(const std::vector<T>& origin) {
  agl::core::Variant::List variant_list{};
  formats::json::ValueBuilder json_list{};
  formats::bson::ValueBuilder bson_list{};

  for (const auto& e : origin) {
    variant_list << e;
    json_list.PushBack(e);
    bson_list.PushBack(e);
  }

  return {variant_list, json_list.ExtractValue(), bson_list.ExtractValue()};
}

template <typename T>
void CheckListFromList(const std::vector<T>& origin) {
  auto [variant, json, bson] = MakeVariantJsonBsonFromList(origin);
  CheckSameListFromIterator(origin, variant);
  CheckSameListFromIterator(origin, json);
  CheckSameListFromIterator(origin, bson);
}

template <typename T>
void CheckSameMapFromIterator(const std::unordered_map<std::string, T>& origin,
                              agl::core::Variant variant) {
  std::unordered_map<std::string, T> res;
  for (const auto& [key, value] : variant.IterateAsMap()) {
    res[key] = value.As<T>();
  }

  ASSERT_EQ(res, origin);
}

template <typename T>
std::tuple<agl::core::Variant, agl::core::Variant, agl::core::Variant>
MakeVariantJsonBsonFromMap(const std::unordered_map<std::string, T>& origin) {
  agl::core::Variant::Map variant_map{};
  formats::json::ValueBuilder json_map{};
  formats::bson::ValueBuilder bson_map{};

  for (const auto& [key, value] : origin) {
    variant_map.Set(key, value);
    json_map[key] = value;
    bson_map[key] = value;
  }

  return {variant_map, json_map.ExtractValue(), bson_map.ExtractValue()};
}

template <typename T>
void CheckMapFromMap(const std::vector<std::string>& origin_keys,
                     const std::vector<T>& origin_values) {
  std::unordered_map<std::string, T> origin;
  for (size_t i = 0; i < origin_keys.size(); ++i) {
    origin[origin_keys[i]] = origin_values[i];
  }
  auto [variant, json, bson] = MakeVariantJsonBsonFromMap(origin);
  CheckSameMapFromIterator(origin, variant);
  CheckSameMapFromIterator(origin, json);
  CheckSameMapFromIterator(origin, bson);
}

}  // namespace

TEST(TestVariant, ListMapVariantIterator) {
  std::vector<std::string> keys = {"key1", "key2", "key3"};
  std::vector<std::string> string_values = {"foo", "bar", "baz"};
  std::vector<int64_t> int_values = {42, 54, 0};

  CheckListFromList(string_values);
  CheckListFromList(int_values);

  CheckMapFromMap(keys, string_values);
  CheckMapFromMap(keys, int_values);
}

}  // namespace agl::core
