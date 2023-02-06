#include <userver/utest/utest.hpp>

#include <defs/definitions.hpp>
#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/value_builder.hpp>

using formats::json::ValueBuilder;

TEST(CodegenStrictParsingDOM, Ok) {
  ValueBuilder vb{};
  vb["some"] = "asd";
  EXPECT_EQ(vb.ExtractValue().As<handlers::StrictParsing>(),
            handlers::StrictParsing{"asd"});
}

TEST(CodegenStrictParsingDOM, Fail) {
  ValueBuilder vb2{};
  vb2["some"] = "asd";
  vb2["other"] = "test";
  try {
    vb2.ExtractValue().As<handlers::StrictParsing>();
    FAIL() << "Not thrown";
  } catch (const formats::json::ParseException& e) {
    EXPECT_EQ(e.what(), std::string{"Unknown key 'other' at path '/' for type "
                                    "'handlers::StrictParsing'"});
  }
}

TEST(CodegenStrictParsingSAX, Fail) {
  std::string str{R"({"some":"asd","other":"test"})"};

  try {
    formats::json::parser::ParseToType<handlers::StrictParsing,
                                       handlers::parser::PStrictParsing>(str);
    FAIL() << "Not thrown";
  } catch (const formats::json::parser::ParseError& e) {
    EXPECT_EQ(e.what(),
              std::string{
                  "Parse error at pos 21, path 'other': unknown field 'other' "
                  "for type 'handlers::StrictParsing', the "
                  "latest token was ,\"other\""});
  }
}

TEST(CodegenStrictParsingSAX, Ok) {
  std::string str{R"({"some": "asd"})"};

  EXPECT_EQ(
      (formats::json::parser::ParseToType<
          handlers::StrictParsing, handlers::parser::PStrictParsing>(str)),
      handlers::StrictParsing{"asd"});
}

TEST(CodegenParsing, ArrayIsNotAnObject) {
  ValueBuilder vb{};
  vb["some"] = formats::json::MakeArray();
  auto json = vb.ExtractValue();

  EXPECT_THROW(json["some"].As<handlers::EmptyObject>(),
               formats::json::TypeMismatchException);
}
