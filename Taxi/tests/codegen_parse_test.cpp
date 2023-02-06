#include <userver/utest/utest.hpp>

#include <codegen/parser/validator.hpp>
#include <defs/all_definitions.hpp>

#include <defs/internal/sample-model.hpp>

using namespace handlers;

using namespace formats::json::parser;

TEST(SwaggerParse, StructWithRequiredFields) {
  const auto parse = &ParseToType<ErrorBase, parser::PErrorBase>;

  EXPECT_EQ(parse(R"({"code":"OOPS", "message":"oops..."})"),
            (ErrorBase{ErrorBaseCode::kOops, "oops..."}));

  EXPECT_THROW(parse(R"({"message":"oops..."})"), ParseError);

  EXPECT_EQ(parse(R"({"code":"OOPS", "message":"oops...", "extra": 1})"),
            (ErrorBase{ErrorBaseCode::kOops, "oops..."}));
}

TEST(SwaggerParse, StructWithoutRequiredFields) {
  const auto parse =
      &ParseToType<StructWithoutRequired, parser::PStructWithoutRequired>;

  auto result = parse(R"({"a": "123"})");

  EXPECT_EQ(result, (StructWithoutRequired{"123"}));

  EXPECT_EQ(parse(R"({})"), StructWithoutRequired{{}});

  EXPECT_EQ(parse(R"({"invalid": 1})"), StructWithoutRequired());
}

TEST(SwaggerParse, EnumInt) {
  const auto parse = &ParseToType<IntEnum, parser::PIntEnum>;

  EXPECT_EQ(parse("1"), IntEnum::k1);

  EXPECT_EQ(parse("9223372036854775807"), IntEnum::k9223372036854775807);
  EXPECT_EQ(parse("-8"), IntEnum::k_8);

  EXPECT_THROW(parse("-5"), ParseError);
  EXPECT_THROW(parse("3"), ParseError);
  EXPECT_THROW(parse("0"), ParseError);
}

TEST(SwaggerParse, IntValidation) {
  formats::json::parser::Int64Parser int64_parser;
  struct Validator {
    void Validate(int64_t value) {
      if (value < 4) throw std::runtime_error("too big");
    }
  };
  codegen::parser::Validator<Int64Parser, Validator> validator(int64_parser);

  validator.Reset();
  int64_t result{0};
  formats::json::parser::SubscriberSink sink(result);
  validator.Subscribe(sink);

  ParserState state;
  state.PushParser(validator.GetParser());
  EXPECT_THROW(state.ProcessInput("2"), ParseError);
}

TEST(SwaggerParse, RecursiveType) {
  const auto parse = [](std::string_view sw) {
    RecursiveNode result;
    parser::PRecursiveNode result_parser;

    result_parser.Reset();
    ::formats::json::parser::SubscriberSink sink(result);
    result_parser.Subscribe(sink);

    formats::json::parser::ParserState state;
    state.PushParser(result_parser.GetParser());
    state.ProcessInput(sw);
    return result;
  };

  EXPECT_EQ(parse("{}"), RecursiveNode());

  EXPECT_EQ(parse(R"({"left": {}})"),
            (RecursiveNode{std::make_unique<RecursiveNode>(), {}}));

  EXPECT_EQ(parse(R"({"left": {}, "right": {}})"),
            (RecursiveNode{std::make_unique<RecursiveNode>(),
                           std::make_unique<RecursiveNode>()}));

  EXPECT_EQ(parse(R"({"left": {"left":{"right":{}}}})"),
            (RecursiveNode{std::make_unique<RecursiveNode>(
                RecursiveNode{std::make_unique<RecursiveNode>(RecursiveNode{
                    ::std::optional<
                        ::codegen::NonNullPtr<::handlers::RecursiveNode>>{},
                    std::make_unique<RecursiveNode>(),
                })})}));
}

TEST(SwaggerParse, Nullable) {
  const auto parse =
      &ParseToType<NullableWithRegexField, parser::PNullableWithRegexField>;

  EXPECT_EQ(parse(R"({"nullable_field": null})"),
            handlers::NullableWithRegexField{});

  EXPECT_EQ(parse(R"({"nullable_field": "1234"})"),
            handlers::NullableWithRegexField{{"1234"}});

  EXPECT_THROW(parse(R"({"nullable_field": "abc"})"), ParseError);

  EXPECT_EQ(parse(R"({})"), handlers::NullableWithRegexField{});
}

TEST(SwaggerParse, NullToDefault) {
  namespace ns = defs::internal::sample_model;
  const auto parse =
      &ParseToType<ns::TreatNullAsDefault, ns::parser::PTreatNullAsDefault>;

  EXPECT_EQ(parse(R"({"x": null})"),
            ns::TreatNullAsDefault{"the default value"});
}
