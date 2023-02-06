#include "yt_logger.hpp"
#include <gtest/gtest.h>

using logging::internal::GetIdFromType;

class SimpleClass {};
namespace {
class ClassInAnon {};
}  // namespace
namespace outer_namespace {
class ClassInNamespace {};
namespace inner_namespace {
class ClassInNamespaces {};
}  // namespace inner_namespace
}  // namespace outer_namespace

TEST(YtLogger, NameFromType) {
  EXPECT_EQ("simple_class", GetIdFromType(typeid(SimpleClass)));
  EXPECT_EQ("class_in_anon", GetIdFromType(typeid(ClassInAnon)));
  EXPECT_EQ("class_in_namespace",
            GetIdFromType(typeid(outer_namespace::ClassInNamespace)));
  EXPECT_EQ("class_in_namespaces",
            GetIdFromType(
                typeid(outer_namespace::inner_namespace::ClassInNamespaces)));
}
