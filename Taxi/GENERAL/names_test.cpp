#include <gtest/gtest.h>

#include "names.hpp"

namespace {

const std::string kName = "name";

}  // namespace

TEST(TagNames, Register) {
  tags::models::Names names;
  ASSERT_TRUE(names.IsEmpty());
  ASSERT_THROW(names.GetName(0u), tags::models::InvariantCorrupted);

  ASSERT_EQ(names.Register(kName), 0u);
  ASSERT_FALSE(names.IsEmpty());
  ASSERT_EQ(names.GetName(0u), kName);

  ASSERT_EQ(names.Register(kName), 0u);
}

TEST(TagNames, BulkRegister) {
  const std::vector<std::string> kNames{"surname", "name", "Name", "Surname"};
  const std::vector<tags::models::Names::Id> kExpectedIds{1u, 0u, 2u, 3u};

  tags::models::Names names;

  ASSERT_EQ(names.Register(kName), 0u);
  ASSERT_EQ(names.Register(kNames), kExpectedIds);
}
