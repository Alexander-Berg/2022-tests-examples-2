#include <gtest/gtest.h>

#include <utils/scope_guard.hpp>

TEST(ScopeGuardTest, Basic) {
  bool triggered = false;
  {
    utils::ScopeGuard guard{[&triggered] { triggered = true; }};

    EXPECT_FALSE(triggered);
  }

  EXPECT_TRUE(triggered);
}

TEST(ScopeGuardTest, ExceptionPropagation) {
  struct TestException {};

  EXPECT_THROW([] { utils::ScopeGuard guard{[] { throw TestException{}; }}; }(),
               TestException);
}

TEST(ScopeGuardTest, ExceptionSuppression) {
  struct TestExceptionInner {};
  struct TestExceptionOuter {};

  EXPECT_THROW(
      [] {
        utils::ScopeGuard guard{[] { throw TestExceptionInner{}; }};
        throw TestExceptionOuter{};
      }(),
      TestExceptionOuter);
}
