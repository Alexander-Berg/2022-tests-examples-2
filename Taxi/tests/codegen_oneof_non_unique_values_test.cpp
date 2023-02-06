#include <defs/api/openapi-30.hpp>

#include <fmt/format.h>
#include <userver/utest/utest.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

namespace {

constexpr const char* kCardNum = "foo";

constexpr const char* kCardType = "card";
constexpr const char* kCardAType = "card_a";
constexpr const char* kCardBType = "card_b";
constexpr const char* kApplePayType = "applepay";
constexpr const char* kGooglePayType = "googlepay";

std::string GetDoc(std::string type) {
  return fmt::format("{}\"type\": \"{}\", \"card-num\": \"{}\"{}", "{",
                     std::move(type), kCardNum, "}");
}

handlers::SomeOtherPayment GetPayment(std::string type) {
  const auto doc = GetDoc(std::move(type));
  const auto json = formats::json::FromString(doc);
  return json.As<handlers::SomeOtherPayment>();
}

struct Visitor {
  Visitor(std::string cardlike_type, std::string applepay_type,
          std::string googlepay_type)
      : cardlike_type_(std::move(cardlike_type)),
        applepay_type_(std::move(applepay_type)),
        googlepay_type_(std::move(googlepay_type)) {}

  bool operator()(const handlers::SomeCardLikePayment& v) {
    if (cardlike_type_.empty()) {
      return false;
    }

    return v.type == cardlike_type_ && v.card_num == kCardNum;
  }

  bool operator()(const handlers::SomeApplePayPayment& v) {
    if (applepay_type_.empty()) {
      return false;
    }

    return v.type == applepay_type_ && v.card_num == kCardNum;
  }

  bool operator()(const handlers::SomeGooglePayPayment& v) {
    if (googlepay_type_.empty()) {
      return false;
    }

    return v.type == googlepay_type_ && v.card_num == kCardNum;
  }

 private:
  std::string cardlike_type_;
  std::string applepay_type_;
  std::string googlepay_type_;
};

bool DoParseSuccessTest(std::string type, std::string v_cardlike_type,
                        std::string v_applepay_type,
                        std::string v_googlepay_type) {
  auto payment = GetPayment(std::move(type));
  auto visitor = Visitor{std::move(v_cardlike_type), std::move(v_applepay_type),
                         std::move(v_googlepay_type)};
  return std::visit(std::move(visitor), payment.AsVariant());
}

bool DoSerializeSuccessTest(std::string type) {
  auto json = formats::json::FromString(GetDoc(type));
  auto payment_json = handlers::Serialize(
      GetPayment(type), formats::serialize::To<formats::json::Value>());
  return json == payment_json;
}

}  // namespace

TEST(OneOfNonUniqueValues, ParseSuccess) {
  EXPECT_TRUE(DoParseSuccessTest(kCardType, kCardType, "", ""));
  EXPECT_TRUE(DoParseSuccessTest(kCardAType, kCardAType, "", ""));
  EXPECT_TRUE(DoParseSuccessTest(kCardBType, kCardBType, "", ""));

  EXPECT_TRUE(DoParseSuccessTest(kApplePayType, "", kApplePayType, ""));

  EXPECT_TRUE(DoParseSuccessTest(kGooglePayType, "", "", kGooglePayType));
}

TEST(OneOfNonUniqueValues, SerializeSuccess) {
  EXPECT_TRUE(DoSerializeSuccessTest(kCardType));
  EXPECT_TRUE(DoSerializeSuccessTest(kCardAType));
  EXPECT_TRUE(DoSerializeSuccessTest(kCardBType));

  EXPECT_TRUE(DoSerializeSuccessTest(kApplePayType));

  EXPECT_TRUE(DoSerializeSuccessTest(kGooglePayType));
}
