#include "data_provider.hpp"

#include <gtest/gtest.h>

namespace {

void Foo(const std::shared_ptr<const std::string>& /*a*/) {}

}  // namespace

TEST(DataProvider, SafePtr) {
  using utils::detail::SafePtr;
  using StrSafePtr = SafePtr<std::string>;
  using StrPtr = StrSafePtr::Base;

  EXPECT_THROW(StrSafePtr(nullptr), std::logic_error);

  const auto a = std::make_shared<std::string>();
  const StrSafePtr safe_a(a);

  // EXPECT_EQ(std::string(), *StrSafePtr(a));  // not build
  EXPECT_EQ(std::string(), *safe_a);  // OK

  // EXPECT_EQ(0u, StrSafePtr(a)->size());      // not build
  EXPECT_EQ(0u, safe_a->size());  // OK

  // Foo(StrSafePtr(a));  // not build, but may be it's OK
  Foo(safe_a);  // OK

  StrPtr ptr;
  // ptr = StrSafePtr(a);  // not build, but may be it's OK
  ptr = safe_a;  // OK

  // const StrPtr& ref_fail = StrSafePtr(a);  // not build
  // std::ignore = ref_fail;

  const StrPtr& ref_ok = safe_a;  // OK
  std::ignore = ref_ok;
}
