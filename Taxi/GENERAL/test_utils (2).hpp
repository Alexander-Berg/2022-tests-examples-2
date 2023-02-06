#pragma once

#include <cmath>

#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>
#include <models/place.hpp>
#include "clustering.hpp"
#include "utils.hpp"

namespace eats_catalog::algo {

inline void ExpectDoubleEqual(const double lhs, const double rhs) {
  EXPECT_TRUE(ApproxEqual(lhs, rhs));
}

inline void ExpectPositionEqual(const ::geometry::Position& lhs,
                                const ::geometry::Position& rhs) {
  EXPECT_TRUE(ApproxEqual(lhs, rhs));
}

template <typename T>
void ExpectOptionalEqual(const std::optional<T>& lhs,
                         const std::optional<T>& rhs) {
  if (!lhs && !rhs) {
    return;
  } else if (lhs && rhs) {
    ExpectDoubleEqual(*lhs, *rhs);
    return;
  }
  FAIL();
}

}  // namespace eats_catalog::algo
