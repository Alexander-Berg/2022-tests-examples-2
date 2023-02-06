#include <gtest/gtest.h>

#include <boost/algorithm/string/predicate.hpp>
#include <boost/core/demangle.hpp>
#include <userver/logging/log.hpp>

#include "collections.hpp"

namespace collections {

TEST(TestCollectionsCast, ExtendOk) {
  std::variant<int, float> source{6.626f};
  std::variant<int, float, std::string> target = cast_variant(source);
  EXPECT_EQ(std::get<float>(target), 6.626f);
}

TEST(TestCollectionsCast, NarrowOk) {
  std::variant<int, float, std::string> source{1.781f};
  std::variant<int, float> target = cast_variant(source);
  EXPECT_EQ(std::get<float>(target), 1.781f);
}

TEST(TestCollectionsCast, NarrowFail) {
  std::variant<int, float, std::string> source{3.141f};
  try {
    std::variant<std::string> target = cast_variant(source);
  } catch (const std::exception& ex) {
    const auto& name = boost::core::demangle(typeid(ex).name());
    LOG_DEBUG() << "Name:" << name;
    EXPECT_TRUE(boost::starts_with(name, "collections::thell::CannotConvert"));
  }
}

}  // namespace collections
