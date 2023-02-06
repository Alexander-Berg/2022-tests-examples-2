#include <cargo_custom_contexts/cargo_custom_contexts.hpp>
#include <cargo_custom_contexts/errors.hpp>

#include <userver/utest/utest.hpp>

#include "constants.hpp"

using namespace test_constants;

TEST(CustomContextTest, TryGetEatsContextWithoutType) {
  const auto& result = cargo_custom_contexts::TryGetEatsContext(
      kEatsCustomContextWithoutTypeJson);
  ASSERT_TRUE(result.has_value());
}

TEST(CustomContextTest, TryGetEatsContextWithType) {
  const auto& result =
      cargo_custom_contexts::TryGetEatsContext(kEatsCustomContextWithTypeJson);
  ASSERT_TRUE(result.has_value());
}

TEST(CustomContextTest, TryGetEatsContextWithWrongJson) {
  const auto& result_without_type = cargo_custom_contexts::TryGetEatsContext(
      kGroceryCustomContextWithoutTypeJson);
  EXPECT_FALSE(result_without_type.has_value());

  const auto& result_with_type = cargo_custom_contexts::TryGetEatsContext(
      kGroceryCustomContextWithTypeJson);
  ASSERT_FALSE(result_with_type.has_value());
}

TEST(CustomContextTest, TryGetGroceryContextWithoutType) {
  const auto& result = cargo_custom_contexts::TryGetGroceryContext(
      kGroceryCustomContextWithoutTypeJson);
  ASSERT_TRUE(result.has_value());
}

TEST(CustomContextTest, TryGetGroceryContextWithType) {
  const auto& result = cargo_custom_contexts::TryGetGroceryContext(
      kGroceryCustomContextWithTypeJson);
  ASSERT_TRUE(result.has_value());
}

TEST(CustomContextTest, TryGetGroceryContextWithWrongJson) {
  const auto& result_without_type = cargo_custom_contexts::TryGetGroceryContext(
      kEatsCustomContextWithoutTypeJson);
  EXPECT_FALSE(result_without_type.has_value());

  const auto& result_with_type = cargo_custom_contexts::TryGetGroceryContext(
      kEatsCustomContextWithTypeJson);
  ASSERT_FALSE(result_with_type.has_value());
}

TEST(CustomContextTest, EatsDeliveryFlagsRequiredFieldsMissing_Throw) {
  const auto& wrong_json =
      formats::json::FromString(R"({"delivery_flags":"wrong_delivery_flag"})");
  ASSERT_THROW(cargo_custom_contexts::GetEatsContext(wrong_json),
               cargo_custom_contexts::ArgumentException);
}

TEST(CustomContextTest, EatsDeliveryFlagsRequiredFields_NoThrow) {
  const auto& correct_json = formats::json::FromString(R"({
          "delivery_flags":{
            "assign_rover": true,
            "is_forbidden_to_be_second_in_batch": true,
            "is_forbidden_to_be_in_batch": true,
            "is_forbidden_to_be_in_taxi_batch": true
          }
        })");
  ASSERT_NO_THROW(cargo_custom_contexts::GetEatsContext(correct_json));
}

TEST(CustomContextTest, GetEatsContextWithoutType_NoThrow) {
  ASSERT_NO_THROW(
      cargo_custom_contexts::GetEatsContext(kEatsCustomContextWithoutTypeJson));
}

TEST(CustomContextTest, GetEatsContextWithType_NoThrow) {
  ASSERT_NO_THROW(
      cargo_custom_contexts::GetEatsContext(kEatsCustomContextWithTypeJson));
}

TEST(CustomContextTest, GetEatsContextWithWrongJson_Throw) {
  EXPECT_THROW(cargo_custom_contexts::GetEatsContext(
                   kGroceryCustomContextWithoutTypeJson),
               cargo_custom_contexts::ArgumentException);

  ASSERT_THROW(
      cargo_custom_contexts::GetEatsContext(kGroceryCustomContextWithTypeJson),
      cargo_custom_contexts::ContextTypeMismatchException);
}

TEST(CustomContextTest, GetGroceryContextWithoutType_NoThrow) {
  ASSERT_NO_THROW(cargo_custom_contexts::GetGroceryContext(
      kGroceryCustomContextWithoutTypeJson));
}

TEST(CustomContextTest, GetGroceryContextWithType_NoThrow) {
  ASSERT_NO_THROW(cargo_custom_contexts::GetGroceryContext(
      kGroceryCustomContextWithTypeJson));
}

TEST(CustomContextTest, GetGroceryContextWithWrongJson_Throw) {
  EXPECT_THROW(cargo_custom_contexts::GetGroceryContext(
                   kEatsCustomContextWithoutTypeJson),
               cargo_custom_contexts::ArgumentException);

  ASSERT_THROW(
      cargo_custom_contexts::GetGroceryContext(kEatsCustomContextWithTypeJson),
      cargo_custom_contexts::ContextTypeMismatchException);
}
