#include <gmock/gmock-matchers.h>
#include <gtest/gtest.h>

#include <set>

#include <userver/logging/log.hpp>

#include <boost/fusion/include/adapt_struct.hpp>

#include <pricing-functions/lang/models/expression.hpp>
#include <pricing-functions/lang/models/expressions/scalar.hpp>
#include <pricing-functions/lang/models/identifier.hpp>
#include <pricing-functions/lang/models/scalars/tuple.hpp>
#include <pricing-functions/lang/models/type.hpp>
#include <pricing-functions/lang/models/type_mapper.hpp>
#include <pricing-functions/lang/models/types/named_tuple.hpp>
#include <pricing-functions/lang/models/types/set.hpp>
#include <pricing-functions/parser/typename_maker.hpp>

namespace {

class Types : public testing::Test {
 protected:
  static void SetUpTestSuite() {}

  static void TearDownTestSuite() { parser::ResetTypeinfoMaps(); }

  void SetUp() override {}

  void TearDown() override {}
};

template <typename T>
lang::models::Scalar MakeScalar(T&& value) {
  return lang::models::Scalar{
      lang::models::scalars::Value<T>{std::move(value)}};
}

struct Foo {};

template <template <typename...> class Container, typename T>
auto WrapContainerIdentifiers(Container<std::string, T>&& data) {
  Container<lang::models::Identifier, T> transformed_data{};
  std::transform(data.begin(), data.end(),
                 std::inserter(transformed_data, transformed_data.end()),
                 [](auto& kv) {
                   return std::make_pair<lang::models::Identifier, T>(
                       lang::models::CreateGlobalIdentifier(kv.first),
                       std::move(kv.second));
                 });
  return transformed_data;
}

template <typename T>
lang::models::Scalar MakeRefScalar(const T& value) {
  return lang::models::Scalar{std::cref(value)};
}

lang::models::types::NamedTuple MakeTupleType(
    std::unordered_map<std::string, lang::models::Type>&& data) {
  std::vector<lang::models::types::ValueField> fields{};
  size_t id = 0;
  std::transform(data.begin(), data.end(), std::back_inserter(fields),
                 [&id](const auto& field_desc) {
                   return lang::models::types::ValueField{
                       lang::models::CreateGlobalIdentifier(field_desc.first),
                       id++, field_desc.second, lang::models::Feature::kNone};
                 });
  return {std::move(fields)};
}

lang::models::scalars::Tuple MakeTuple(
    std::unordered_map<std::string, lang::models::Scalar>&& data) {
  auto wrapped_data = WrapContainerIdentifiers(std::move(data));
  std::vector<lang::models::types::ValueField> fields{};
  std::vector<lang::models::Scalar> values{};
  size_t id = 0;
  for (const auto& [k, v] : wrapped_data) {
    fields.emplace_back(k, id, v.GetType(), lang::models::Feature::kNone);
    values.emplace_back(v);
    ++id;
  }
  return {
      lang::models::Type{lang::models::types::NamedTuple{std::move(fields)}},
      std::move(values)};
}

}  // namespace

TEST_F(Types, PrimitiveTypeBasicOps) {
  lang::models::Type int_{typeid(int)};
  lang::models::Type double_{typeid(double)};
  auto int_opt_ = int_.MakeOptional();

  ASSERT_FALSE(int_.IsOptional());
  ASSERT_TRUE(int_.IsPrimitive());
  ASSERT_FALSE(int_.IsSet());
  ASSERT_FALSE(int_.IsSequence());
  ASSERT_FALSE(int_.IsComposite());
  ASSERT_THROW(int_.InnerType(), std::domain_error);
  ASSERT_THROW(int_.ElementType(), std::domain_error);
  ASSERT_THROW(int_.GetField(lang::models::CreateGlobalIdentifier("x")),
               std::domain_error);
  ASSERT_THROW(int_.ListFields(), std::domain_error);
  ASSERT_THROW(int_.Enumerate(MakeScalar<int>(1)), std::domain_error);
  ASSERT_EQ(int_opt_.InnerType(), int_);
  ASSERT_EQ(int_.GetTypeName(), "int");
  ASSERT_EQ(int_, int_);
  ASSERT_FALSE(int_ == int_opt_);
  ASSERT_EQ(int_ || int_, int_);
  ASSERT_EQ(int_ && int_, int_);
  ASSERT_THROW(int_ && double_, std::logic_error);
  ASSERT_THROW(int_ || double_, std::logic_error);
}

TEST_F(Types, OptionalTypeBasicOps) {
  lang::models::Type int_{typeid(int)};
  auto int_opt_ = int_.MakeOptional();

  ASSERT_TRUE(int_opt_.IsOptional());
  ASSERT_FALSE(int_opt_.IsPrimitive());
  ASSERT_FALSE(int_opt_.IsSet());
  ASSERT_FALSE(int_opt_.IsSequence());
  ASSERT_FALSE(int_opt_.IsComposite());
  ASSERT_EQ(int_opt_.InnerType(), int_);
  ASSERT_THROW(int_opt_.ElementType(), std::domain_error);
  ASSERT_THROW(int_opt_.GetField(lang::models::CreateGlobalIdentifier("x")),
               std::domain_error);
  ASSERT_THROW(int_opt_.ListFields(), std::domain_error);
  ASSERT_THROW(int_opt_.Enumerate(MakeScalar<int>(1)), std::domain_error);
  ASSERT_EQ(int_opt_.GetTypeName(), "std::optional<int>");
  ASSERT_EQ(int_opt_, int_opt_);
  ASSERT_EQ(int_opt_ || int_opt_, int_opt_);
  ASSERT_EQ(int_opt_ || int_, int_opt_);
  ASSERT_EQ(int_ || int_opt_, int_opt_);
  ASSERT_EQ(int_opt_ && int_opt_, int_opt_);
  ASSERT_EQ(int_opt_ && int_, int_);
  ASSERT_EQ(int_ && int_opt_, int_);
}

template <typename T>
void RegisterType() {
  lang::models::types::MakeTypeMapping<T>();
  parser::AddTypeinfo(parser::details::TypeNameMaker<T>::Make(), typeid(T));
}

TEST_F(Types, VectorBasicOps) {
  RegisterType<std::vector<int>>();

  std::vector<int> vec_value_{1, 4, 7};
  lang::models::Type int_vec_{typeid(std::vector<int>)};
  lang::models::Type int_{typeid(int)};
  auto int_vec_opt_ = int_vec_.MakeOptional();

  ASSERT_FALSE(int_vec_.IsOptional());
  ASSERT_FALSE(int_vec_.IsPrimitive());
  ASSERT_FALSE(int_vec_.IsSet());
  ASSERT_TRUE(int_vec_.IsSequence());
  ASSERT_FALSE(int_vec_.IsComposite());
  ASSERT_THROW(int_vec_.InnerType(), std::domain_error);
  ASSERT_EQ(int_vec_.ElementType(), int_);
  ASSERT_THROW(int_vec_.GetField(lang::models::CreateGlobalIdentifier("x")),
               std::domain_error);
  ASSERT_THROW(int_vec_.ListFields(), std::domain_error);
  ASSERT_THAT(
      int_vec_.Enumerate(lang::models::Scalar{std::cref(vec_value_)}),
      ::testing::ElementsAre(lang::models::Scalar{std::cref(vec_value_[0])},
                             lang::models::Scalar{std::cref(vec_value_[1])},
                             lang::models::Scalar{std::cref(vec_value_[2])}));
  ASSERT_EQ(int_vec_opt_.InnerType(), int_vec_);
  ASSERT_EQ(int_vec_.GetTypeName(), "std::vector<int>");
  ASSERT_EQ(int_vec_, int_vec_);
  ASSERT_FALSE(int_vec_ == int_vec_opt_);
  ASSERT_EQ(int_vec_ || int_vec_, int_vec_);
  ASSERT_EQ(int_vec_ && int_vec_, int_vec_);
}

namespace tests::types {

struct SomeStruct {
  int x;
  double y;
  std::string s;
};

struct AnotherSomeStruct {
  double a;
  int x;
  bool b;
};

}  // namespace tests::types

BOOST_FUSION_ADAPT_STRUCT(tests::types::SomeStruct,
                          (int, x)(double, y)(std::string, s))

BOOST_FUSION_ADAPT_STRUCT(tests::types::AnotherSomeStruct,
                          (double, a)(int, x)(bool, b))

TEST_F(Types, StructTypeBasicOps) {
  RegisterType<tests::types::SomeStruct>();
  RegisterType<tests::types::AnotherSomeStruct>();
  lang::models::Type some_struct_{typeid(tests::types::SomeStruct)};
  lang::models::Type another_struct_{typeid(tests::types::AnotherSomeStruct)};
  lang::models::Type int_{typeid(int)};
  lang::models::Type double_{typeid(double)};
  lang::models::Type string_{typeid(std::string)};
  tests::types::SomeStruct some_struct_inst_v_{1, 2.25, "test"};
  lang::models::Scalar some_struct_inst_{std::cref(some_struct_inst_v_)};

  tests::types::AnotherSomeStruct another_struct_v{7.77, 42, true};
  lang::models::Scalar another_struct_inst_{std::cref(another_struct_v)};

  ASSERT_FALSE(some_struct_.IsOptional());
  ASSERT_FALSE(some_struct_.IsPrimitive());
  ASSERT_FALSE(some_struct_.IsSet());
  ASSERT_FALSE(some_struct_.IsSequence());
  ASSERT_TRUE(some_struct_.IsComposite());

  ASSERT_THROW(some_struct_.InnerType(), std::domain_error);
  ASSERT_THROW(some_struct_.ElementType(), std::domain_error);

  auto fields = some_struct_.ListFields();
  std::sort(fields.begin(), fields.end(), [](const auto& l, const auto& r) {
    return l.GetId().name.GetName() < r.GetId().name.GetName();
  });
  ASSERT_EQ(fields.size(), 3);
  std::vector<lang::models::Scalar> field_values{};
  std::transform(fields.begin(), fields.end(), std::back_inserter(field_values),
                 [&some_struct_inst_](const auto& value_field) {
                   return value_field.Get(some_struct_inst_);
                 });
  ASSERT_THAT(
      field_values,
      ::testing::ElementsAre(
          lang::models::Scalar{std::cref(some_struct_inst_v_.s)},
          lang::models::Scalar{static_cast<double>(some_struct_inst_v_.x)},
          lang::models::Scalar{some_struct_inst_v_.y}));

  auto x_field =
      some_struct_.GetField(lang::models::CreateGlobalIdentifier("x"));
  auto y_field =
      some_struct_.GetField(lang::models::CreateGlobalIdentifier("y"));
  auto s_field =
      some_struct_.GetField(lang::models::CreateGlobalIdentifier("s"));
  ASSERT_EQ(y_field.GetType(), double_);
  ASSERT_EQ(s_field.GetType(), string_);
  ASSERT_EQ(x_field.GetType(), double_);

  ASSERT_THROW(some_struct_.Enumerate(some_struct_inst_), std::domain_error);
  ASSERT_EQ(some_struct_.GetTypeName(), "tests::types::SomeStruct");
  ASSERT_EQ(some_struct_, some_struct_);
}

TEST_F(Types, StructTypeMerging) {
  namespace lm = lang::models;
  RegisterType<tests::types::SomeStruct>();
  RegisterType<tests::types::AnotherSomeStruct>();
  lang::models::Type some_struct_{typeid(tests::types::SomeStruct)};
  lang::models::Type another_struct_{typeid(tests::types::AnotherSomeStruct)};

  ASSERT_EQ(some_struct_ || some_struct_, some_struct_);
  ASSERT_EQ(some_struct_ && some_struct_, some_struct_);
  lang::models::Type struct_merge{
      {{lm::CreateGlobalIdentifier("x"), lang::models::Type{typeid(double)}},
       {lm::CreateGlobalIdentifier("y"), lang::models::Type{typeid(double)}},
       {lm::CreateGlobalIdentifier("a"), lang::models::Type{typeid(double)}},
       {lm::CreateGlobalIdentifier("s"),
        lang::models::Type{typeid(std::string)}},
       {lm::CreateGlobalIdentifier("b"), lang::models::Type{typeid(bool)}}}};
  ASSERT_EQ(some_struct_ && another_struct_, struct_merge);

  lang::models::Type struct_merge_opts{
      {{lm::CreateGlobalIdentifier("x"), lang::models::Type{typeid(double)}},
       {lm::CreateGlobalIdentifier("y"),
        lang::models::Type{typeid(double)}.MakeOptional()},
       {lm::CreateGlobalIdentifier("a"),
        lang::models::Type{typeid(double)}.MakeOptional()},
       {lm::CreateGlobalIdentifier("s"),
        lang::models::Type{typeid(std::string)}.MakeOptional()},
       {lm::CreateGlobalIdentifier("b"),
        lang::models::Type{typeid(bool)}.MakeOptional()}}};
  ASSERT_EQ(some_struct_ || another_struct_, struct_merge_opts);
}

TEST_F(Types, NonAdaptedTypeUsing) {
  ASSERT_THROW(lang::models::Type(typeid(Foo)), std::domain_error);
}

TEST_F(Types, ValueFieldBasicOps) {
  namespace lmt = lang::models::types;
  namespace lm = lang::models;

  {
    lmt::ValueField val_f{lm::CreateGlobalIdentifier("x"), 1,
                          lm::Type{typeid(double)}, lm::Feature::kNone};
    auto tuple_ = MakeTuple({{"x", MakeScalar<double>(42)}});
    ASSERT_EQ(val_f.Get(tuple_).Serialize(), "42.000000");
  }  // namespace lm=lang::models;

  {
    lmt::ValueField val_f{lm::CreateGlobalIdentifier("x"), 1,
                          lm::Type{typeid(double)}, lm::Feature::kNone};
    auto tuple_ = MakeTuple({{"x", MakeScalar<double>(42)}});
    ASSERT_EQ(val_f.Get(std::move(tuple_)).Serialize(), "42.000000");
  }
}

TEST_F(Types, SetBasicOps) {
  const auto& set_ = lang::models::types::MakeTypeMapping<std::set<int>>();
  ASSERT_EQ(set_, set_);
  ASSERT_TRUE(set_.IsSet());
}

TEST_F(Types, MapBasicOps) {
  const auto& map_ = lang::models::types::MakeTypeMapping<std::map<int, int>>();
  ASSERT_EQ(map_, map_);
  ASSERT_TRUE(map_.IsSet());
}

TEST_F(Types, TupleTypeRawType) {
  auto tuple_type_ = MakeTupleType({{"x", lang::models::Type{typeid(double)}},
                                    {"y", lang::models::Type{typeid(double)}}});
  ASSERT_THROW(tuple_type_.RawType(), std::domain_error);
}
