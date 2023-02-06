#include <gtest/gtest.h>

#include "utils/mapper.hpp"

namespace {
class OneArgumentMapper : public utils::Mapper<int(std::string)> {};
class TwoStringsMapper : public utils::Mapper<short(std::string, std::string)> {
};
}  // namespace

TEST(MapperTest, OneArgument) {
  OneArgumentMapper mapper;
  EXPECT_EQ(0, mapper.GetOrCreateIndex("a"));
  EXPECT_EQ(1, mapper.GetOrCreateIndex("b"));
  EXPECT_EQ(1, mapper.GetOrCreateIndex("b"));
  EXPECT_EQ(0, mapper.GetOrCreateIndex("a"));
}

TEST(MapperTest, TwoArguments) {
  TwoStringsMapper mapper;
  const std::string s1("aaa");
  const std::string s2("bbb");
  const std::string s3("aaabbb");
  EXPECT_EQ(0, mapper.GetOrCreateIndex(s1, s3));
  EXPECT_EQ(1, mapper.GetOrCreateIndex(s2, s3));
  EXPECT_EQ(2, mapper.GetOrCreateIndex(s1 + s2, s3));
  EXPECT_EQ(0, mapper.GetOrCreateIndex(s1, s1 + s2));
}

TEST(MapperTest, ImplementationSelection) {
  [[maybe_unused]] OneArgumentMapper::impl_type_plain_tag test_1;
  [[maybe_unused]] TwoStringsMapper::impl_type_tuple_tag test_2;
}
