#include <agl/core/executer_state.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/io/encoded-string.hpp>
#include <agl/sourcing/body.hpp>

#include <userver/formats/bson.hpp>
#include <userver/formats/bson/binary.hpp>
#include <userver/utest/utest.hpp>

namespace agl::sourcing::tests {

UTEST(TestBodyTest, Simple) {
  core::ExecuterState executer_state;

  auto map = core::Variant::Map().Set("test", true).Set("value", 1.234);
  Body body("application/json", core::Variant(std::move(map)));

  core::variant::Dependencies deps;
  body.GetDependencies(deps);
  EXPECT_TRUE(deps.IsEmpty());
  EXPECT_EQ("application/json", body.ContentType(executer_state));
  EXPECT_EQ(formats::json::FromString("{\"test\":true,\"value\":1.234}"),
            formats::json::FromString(
                body.Encode(executer_state, std::string())->data));
}

UTEST(TestBodyTest, SimpleBson) {
  core::ExecuterState executer_state;

  auto map = core::Variant::Map().Set("test", true).Set("value", 1.234);
  Body body("application/bson", core::Variant(std::move(map)));
  std::string bson_encoded = body.Encode(executer_state, {})->data;

  formats::bson::ValueBuilder expected_bulder;
  expected_bulder["test"] = true;
  expected_bulder["value"] = 1.234;
  formats::bson::Value expected = expected_bulder.ExtractValue();

  core::variant::Dependencies deps;
  EXPECT_EQ("application/bson", body.ContentType(executer_state));
  EXPECT_EQ(expected, formats::bson::FromBinaryString(bson_encoded));
}

}  // namespace agl::sourcing::tests
