#include <gtest/gtest.h>

#include "state.hpp"

namespace eats_catalog::pricing {

TEST(PricingState, SaveWasNotCalled) {
  PricingState state{};
  const bool result = state.IsChanged({});
  ASSERT_TRUE(result);
}

TEST(PricingState, DifferentLength) {
  PricingState state{};
  state.Save({
      {models::Money{10}, models::Money{10}},
      {models::Money{20}, models::Money{20}},
  });
  const bool result = state.IsChanged({
      {models::Money{10}, models::Money{10}},
  });
  ASSERT_TRUE(result);
}

TEST(PricingState, NotEqual) {
  PricingState state{};
  state.Save({
      {models::Money{10}, models::Money{10}},
      {models::Money{20}, models::Money{20}},
  });
  const bool result = state.IsChanged({
      {models::Money{10}, models::Money{10}},
      {models::Money{20}, models::Money{30}},
  });
  ASSERT_TRUE(result);
}

TEST(PricingState, NotChanged) {
  PricingState state{};
  state.Save({
      {models::Money{10}, models::Money{10}},
      {models::Money{20}, models::Money{20}},
  });
  const bool result = state.IsChanged({
      {models::Money{10}, models::Money{10}},
      {models::Money{20}, models::Money{20}},
  });
  ASSERT_FALSE(result);
}

}  // namespace eats_catalog::pricing
