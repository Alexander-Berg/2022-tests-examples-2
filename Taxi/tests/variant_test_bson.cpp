// todo move to agl

#include <agl/core/executer_state.hpp>
#include <agl/core/variant.hpp>

#include <userver/storages/secdist/secdist.hpp>

#include <userver/utest/utest.hpp>

#include <agl/core/dynamic_config.hpp>

#include <limits>

#include <userver/formats/bson.hpp>

namespace agl::core {

static const DynamicConfig kDynamicConfig;
static const storages::secdist::SecdistConfig kSecdistConfig;

TEST(TestVariant, BsonEqualsSimple) {
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

  agl::core::Variant sample_bson_null((formats::bson::Value()));
  agl::core::Variant sample_bson_false(
      formats::bson::ValueBuilder(false).ExtractValue());
  agl::core::Variant sample_bson_true(
      formats::bson::ValueBuilder(true).ExtractValue());
  agl::core::Variant sample_bson_int0(
      formats::bson::ValueBuilder(int64_t(0)).ExtractValue());
  agl::core::Variant sample_bson_int42(
      formats::bson::ValueBuilder(int64_t(42)).ExtractValue());
  agl::core::Variant sample_bson_double0(
      formats::bson::ValueBuilder(double(0)).ExtractValue());
  agl::core::Variant sample_bson_double11(
      formats::bson::ValueBuilder(double(11.0)).ExtractValue());
  agl::core::Variant sample_bson_string_empty(
      formats::bson::ValueBuilder("").ExtractValue());
  agl::core::Variant sample_bson_string_test(
      formats::bson::ValueBuilder("test").ExtractValue());
  agl::core::Variant sample_bson_list_empty(
      formats::bson::ValueBuilder(formats::common::Type::kArray)
          .ExtractValue());
  formats::bson::ValueBuilder list_builder(formats::common::Type::kArray);
  list_builder.PushBack("foo");
  list_builder.PushBack(int64_t(100500));
  list_builder.PushBack(false);
  agl::core::Variant sample_bson_list_non_empty(list_builder.ExtractValue());
  agl::core::Variant sample_bson_map_empty(
      formats::bson::ValueBuilder(formats::common::Type::kObject)
          .ExtractValue());
  formats::bson::ValueBuilder map_builder(formats::common::Type::kObject);
  map_builder["key1"] = "value1";
  map_builder["int"] = int64_t(42);
  map_builder["bool"] = true;
  agl::core::Variant sample_bson_map_non_empty(map_builder.ExtractValue());

  agl::core::Variant sample_nested1(
      agl::core::Variant::List()
      << std::string("foo") << int64_t(100500)
      << (agl::core::Variant::List() << "bar" << true) << false);
  formats::bson::ValueBuilder sample_nested1_sub_list_builder(
      formats::common::Type::kArray);
  sample_nested1_sub_list_builder.PushBack("bar");
  sample_nested1_sub_list_builder.PushBack(true);
  formats::bson::ValueBuilder sample_nested1_list_builder(
      formats::common::Type::kArray);
  sample_nested1_list_builder.PushBack("foo");
  sample_nested1_list_builder.PushBack(int64_t(100500));
  sample_nested1_list_builder.PushBack(
      sample_nested1_sub_list_builder.ExtractValue());
  sample_nested1_list_builder.PushBack(false);
  agl::core::Variant sample_bson_nested1(
      sample_nested1_list_builder.ExtractValue());

  formats::bson::ValueBuilder sample_nested2_inner_bson_builder;
  sample_nested2_inner_bson_builder["test"] = "value";
  sample_nested2_inner_bson_builder["int"] = 116;
  formats::bson::Value sample_nested2_inner_bson(
      sample_nested2_inner_bson_builder.ExtractValue());
  agl::core::Variant sample_nested2(
      agl::core::Variant::List()
      << variant::io::BsonPromise(sample_nested2_inner_bson)
      << std::string("foo") << int64_t(100500)
      << (agl::core::Variant::List()
          << "bar" << true
          << variant::io::BsonPromise(sample_nested2_inner_bson))
      << (agl::core::Variant::Map()
              .Set("foo", "bar")
              .Set("false", false)
              .Set("bson", variant::io::BsonPromise(sample_nested2_inner_bson)))
      << false);
  formats::bson::ValueBuilder sample_nested2_sub_list_builder(
      formats::common::Type::kArray);
  sample_nested2_sub_list_builder.PushBack("bar");
  sample_nested2_sub_list_builder.PushBack(true);
  sample_nested2_sub_list_builder.PushBack(sample_nested2_inner_bson);
  formats::bson::ValueBuilder sample_nested2_sub_map_builder(
      formats::common::Type::kObject);
  sample_nested2_sub_map_builder["foo"] = "bar";
  sample_nested2_sub_map_builder["false"] = false;
  sample_nested2_sub_map_builder["bson"] = sample_nested2_inner_bson;
  formats::bson::ValueBuilder sample_nested2_list_builder(
      formats::common::Type::kArray);
  sample_nested2_list_builder.PushBack(sample_nested2_inner_bson);
  sample_nested2_list_builder.PushBack("foo");
  sample_nested2_list_builder.PushBack(int64_t(100500));
  sample_nested2_list_builder.PushBack(
      sample_nested2_sub_list_builder.ExtractValue());
  sample_nested2_list_builder.PushBack(
      sample_nested2_sub_map_builder.ExtractValue());
  sample_nested2_list_builder.PushBack(false);
  agl::core::Variant sample_bson_nested2(
      sample_nested2_list_builder.ExtractValue());

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

      &sample_bson_null,
      &sample_bson_false,
      &sample_bson_true,
      &sample_bson_int0,
      &sample_bson_int42,
      &sample_bson_double0,
      &sample_bson_double11,
      &sample_bson_string_empty,
      &sample_bson_string_test,
      &sample_bson_list_empty,
      &sample_bson_list_non_empty,
      &sample_bson_map_empty,
      &sample_bson_map_non_empty,
      &sample_bson_nested1,
      &sample_bson_nested2,
  };

  const std::vector<
      std::pair<const agl::core::Variant*, const agl::core::Variant*>>
      kEqual{
          {&sample_none, &sample_bson_null},
          {&sample_false, &sample_bson_false},
          {&sample_true, &sample_bson_true},
          {&sample_int0, &sample_bson_int0},
          {&sample_int0, &sample_bson_double0},
          {&sample_int42, &sample_bson_int42},
          //  {&sample_bson_int0, &sample_bson_double0}, bson compare is strict
          {&sample_double0, &sample_bson_double0},
          {&sample_double0, &sample_bson_int0},
          {&sample_double11, &sample_bson_double11},
          {&sample_string_empty, &sample_bson_string_empty},
          {&sample_string_test, &sample_bson_string_test},
          {&sample_list_empty, &sample_bson_list_empty},
          {&sample_list_non_empty, &sample_bson_list_non_empty},
          {&sample_map_empty, &sample_bson_map_empty},
          {&sample_map_non_empty, &sample_bson_map_non_empty},
          {&sample_nested1, &sample_bson_nested1},
          {&sample_nested2, &sample_bson_nested2},
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

TEST(TestVariant, BsonEqualsJson) {
  Variant bson{formats::bson::Value()};
  Variant json{formats::json::Value()};
  ASSERT_THROW(bson.Equals(json), std::runtime_error);
}

}  // namespace agl::core
