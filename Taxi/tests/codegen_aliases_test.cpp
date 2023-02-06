#include <defs/definitions.hpp>

#include <userver/formats/json/serialize.hpp>

#include <userver/utest/utest.hpp>

TEST(CodegenAliases, Basic) {
  static_assert(
      !std::is_same_v<handlers::ApplePayPayment, handlers::CardLikePayment>,
      "Must be a strong typedef for oneOf to work");
  static_assert(
      !std::is_same_v<handlers::ApplePayPayment, handlers::CoopAccountPayment>,
      "Must be a strong typedef for oneOf to work");

  const auto json_corp = formats::json::FromString(R"({
    "type": "the corp type",
    "card-num": "the card-num"
  })");
  const auto corp = json_corp.As<handlers::CoopAccountPayment>();
  EXPECT_EQ(corp.type, "the corp type");
  EXPECT_EQ(corp.card_num, "the card-num");

  const auto json_apple = formats::json::FromString(R"({
    "type": "the apple type",
    "card-num": "the card-num"
  })");
  const auto apple = json_apple.As<handlers::ApplePayPayment>();
  EXPECT_EQ(apple.type, "the apple type");
  EXPECT_EQ(apple.card_num, "the card-num");
}

namespace handlers {

// Make sure that we do not add unnecessary aliases.
// If alias is created then we get 'error: redefinition of '
struct TesingAliasEnum {};
struct TestingAliasIntEnum {};
struct TestingAliasVariant {};
struct TestingAliasArray {};
struct TestingAliasString {};
struct TestingAliasInt {};

}  // namespace handlers
